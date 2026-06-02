# Endianness: Big-Endian vs Little-Endian

When a multi-byte integer is stored in memory, which byte goes first? The answer depends on the **endianness** of the system. Getting this wrong when reading binary files, network packets, or cross-platform data is one of the most common low-level bugs.

## The Two Conventions

Given the 32-bit value `0xDEADBEEF` stored starting at address `0x1000`:

| Address | Big-Endian | Little-Endian |
|---|---|---|
| 0x1000 | `0xDE` (most significant) | `0xEF` (least significant) |
| 0x1001 | `0xAD` | `0xBE` |
| 0x1002 | `0xBE` | `0xAD` |
| 0x1003 | `0xEF` | `0xDE` (most significant) |

**Big-endian**: the most significant byte is at the lowest address. Think of it like writing a number — thousands before units.

**Little-endian**: the least significant byte is at the lowest address. x86, x86-64, and ARM (default mode) are all little-endian.

## Which Systems Use Which?

| Architecture | Default endianness |
|---|---|
| x86 / x86-64 | Little-endian |
| ARM (most modes) | Little-endian |
| MIPS (configurable) | Big-endian (historically) |
| PowerPC | Big-endian (historically) |
| RISC-V | Little-endian |
| Network byte order | Big-endian |
| SPARC | Big-endian |

ARM is technically **bi-endian** (configurable at boot), but Linux on ARM runs in little-endian mode.

## Visualizing with a Union

```c
#include <stdio.h>
#include <stdint.h>

typedef union {
    uint32_t word;
    uint8_t  bytes[4];
} Peek;

int main(void) {
    Peek p;
    p.word = 0xDEADBEEF;

    for (int i = 0; i < 4; i++)
        printf("bytes[%d] = 0x%02X\n", i, p.bytes[i]);
    return 0;
}
```

On a little-endian x86 machine this prints:
```
bytes[0] = 0xEF
bytes[1] = 0xBE
bytes[2] = 0xAD
bytes[3] = 0xDE
```

`bytes[0]` is the byte at the lowest address — the least significant byte. This confirms x86 is little-endian.

## Byte Swapping

To convert between endiannesses, byte-swap the value. For a 32-bit integer:

```c
#include <stdint.h>

uint32_t swap32(uint32_t x) {
    return ((x & 0xFF000000) >> 24) |
           ((x & 0x00FF0000) >>  8) |
           ((x & 0x0000FF00) <<  8) |
           ((x & 0x000000FF) << 24);
}
```

POSIX provides `htonl` / `ntohl` (host-to-network-long / network-to-host-long) as standard byte-swap helpers for 32-bit values, and `htons` / `ntohs` for 16-bit. "Network byte order" is always big-endian.

```c
#include <arpa/inet.h>

uint32_t host_val = 0xDEADBEEF;
uint32_t net_val  = htonl(host_val);  // big-endian for the wire
uint32_t back     = ntohl(net_val);   // back to host order
```

## Where Endianness Bites You

- **Binary file formats** — a `.bmp` or `.wav` file stores integers in a specific endian order. Reading raw bytes on the wrong architecture gives garbage values.
- **Network protocols** — IP, TCP, UDP headers are big-endian. An x86 host must byte-swap before reading port numbers or IP addresses.
- **OS kernel data structures** — device drivers must swap bytes when talking to big-endian peripherals (some network cards, FPGAs).
- **Debuggers and hex dumps** — a hex dump shows bytes in memory order (address-ascending), not the logical integer value. Be careful when reading multi-byte values from a dump.

## Common Pitfalls

- Casting `int *` to `char *` and reading individual bytes — valid C, but the result is endian-dependent.
- Storing a struct to disk with `fwrite` — the binary layout is endian-specific. Use explicit serialization if portability is needed.
- Assuming network libraries handle swapping — they do for address/port, but the payload bytes are your responsibility.

> **Interview answer:** Endianness is the order in which bytes of a multi-byte integer are stored in memory. Little-endian (x86, ARM) stores the least significant byte at the lowest address; big-endian (network byte order, SPARC) stores the most significant byte first. Converting between them requires a byte swap, done with helpers like `htonl`/`ntohl` for network communication.
