# The gdb Remote Serial Protocol Stub

When you type `target remote localhost:1234` in gdb, both sides speak the **GDB Remote Serial Protocol (RSP)** — a simple ASCII packet protocol that has remained almost unchanged since the early 1990s. Understanding it makes you a much more effective platform developer because you can implement the stub, diagnose dropped packets, and add custom monitor commands.

## Packet Structure

Every RSP packet has the form:

```
$ packet-data # checksum
```

- `$` — start of packet
- `packet-data` — the payload (ASCII or hex-encoded)
- `#` — end of payload
- `checksum` — two hex digits, sum of all bytes in `packet-data` modulo 256

The receiver replies `+` (ACK) or `-` (NACK, requesting retransmit). In modern gdb, the acknowledgment mode can be disabled for speed.

**Example: read four bytes at address 0x10000**

```
-> $m10000,4#b2       (gdb requests memory read)
<- +                  (VP acks the packet)
<- $deadbeef#xx       (VP returns 4 bytes, little-endian hex)
-> +                  (gdb acks)
```

## Core RSP Commands Your Stub Must Implement

| Packet | Meaning |
|---|---|
| `?` | Halt reason — reply `S05` (SIGTRAP) to indicate stopped |
| `g` | Read all general-purpose registers (returned as one hex string) |
| `G...` | Write all general-purpose registers |
| `m addr,len` | Read `len` bytes from `addr` |
| `M addr,len:data` | Write `data` to `addr` |
| `c [addr]` | Continue (resume execution) |
| `s [addr]` | Single-step one instruction |
| `Z0,addr,kind` | Insert software breakpoint |
| `z0,addr,kind` | Remove software breakpoint |
| `qSupported` | Feature negotiation handshake |
| `k` | Kill / disconnect |

Unrecognized packets must get an empty reply `$#00` — this signals "not supported" without disconnecting.

## Implementing a Minimal Stub in C++

A sketch of the server loop inside an ISS:

```cpp
class RspServer {
    int listen_fd, conn_fd;
public:
    void run_server(int port) {
        listen_fd = tcp_listen(port);   // your TCP helper
        conn_fd   = tcp_accept(listen_fd);
        std::string pkt;
        while (true) {
            if (!recv_packet(conn_fd, pkt)) break;
            std::string reply = dispatch(pkt);
            send_packet(conn_fd, reply);
        }
    }

    std::string dispatch(const std::string& pkt) {
        if (pkt == "?")         return "S05";
        if (pkt[0] == 'g')      return read_all_regs();
        if (pkt[0] == 'm')      return read_mem(pkt);
        if (pkt[0] == 'c')      { cpu_resume(); return "";  }
        if (pkt[0] == 's')      { cpu_step();   return "S05"; }
        return "";              // unsupported — empty reply
    }
};
```

The key insight: `cpu_resume()` is non-blocking — it starts the ISS thread and returns immediately. The stub only sends the next `S##` stop-reply when the ISS hits a breakpoint or trap.

## Software vs Hardware Breakpoints

- **Software breakpoint (`Z0`):** The stub overwrites the target instruction with a trap opcode (e.g., `BKPT 0` on ARM Thumb, `EBREAK` on RISC-V). Hitting it raises a fault, which the ISS intercepts.
- **Hardware breakpoint (`Z1`):** The ISS maintains a list of breakpoint addresses and checks the PC after every step — no target memory modification.

VPs almost always support hardware breakpoints cheaply (it's just a list comparison), so prefer `Z1` when implementing.

## Monitor Commands

RSP passes arbitrary text to the stub via `qRcmd,hex-encoded-command`. This is how gdb's `monitor` command works:

```
(gdb) monitor trace on
```

translates to `qRcmd,7472616365206f6e`. Your stub decodes the hex, processes the command, and returns output as `O` (output) packets before the final `OK`.

```cpp
if (pkt.rfind("qRcmd,", 0) == 0) {
    std::string cmd = hex_decode(pkt.substr(6));
    if (cmd == "trace on")  { tracing = true; return "OK"; }
}
```

## Common Pitfalls

- **Checksum errors.** Off-by-one in the checksum loop causes constant NACK loops. Recalculate manually for your first test packet.
- **Register order.** gdb expects registers in a specific order defined by the target's XML feature file or the GDB source. Getting this wrong scrambles `info registers`.
- **Endianness.** Memory reads must return bytes in target byte order. An ARM little-endian target returns `0xDEADBEEF` at address A as `ef be ad de` in the packet.

> **Interview answer:** "RSP is a simple ASCII packet protocol — `$data#checksum` — where gdb sends commands like `m` (read memory) or `g` (read registers) and the ISS stub replies. Implementing it requires TCP, checksum handling, and wiring each packet type to ISS operations."
