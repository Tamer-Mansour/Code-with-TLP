# The Debug Transport Interface

The debug transport interface provides a way to read or write target memory without affecting simulation state — no time advances, no side effects, no interrupts triggered. It is primarily used by debuggers, trace loggers, and analysis tools that need to inspect the system while it is running or paused.

## Signature

```cpp
virtual unsigned int transport_dbg(tlm::tlm_generic_payload& trans) = 0;
```

The return value is the number of bytes actually transferred. The generic payload fields (command, address, data pointer, length) carry the same meaning as in `b_transport`. The critical differences are:

- **No time annotation parameter** — debug transport is instantaneous in simulation time.
- **No side effects required** — reading a UART status register must not clear its FIFO; writing a timer count-down must not reset the timer (though targets may choose to support writes for initialization).
- **Partial transfers are legal** — a target may return fewer bytes than requested (the return value indicates how many it handled).

## When to Use Debug Transport

| Scenario | Why debug transport fits |
|---|---|
| GDB stub reading memory to display variables | Must not perturb executing simulation |
| Waveform dumper snapshotting register values | No timing side effects desired |
| Test bench verifying memory contents after a DMA | Clean, side-effect-free read |
| Memory initialization before `sc_start()` | No simulation time yet |

## Implementing transport_dbg in a Target

```cpp
unsigned int Ram::transport_dbg(tlm::tlm_generic_payload& trans) {
    tlm::tlm_command cmd = trans.get_command();
    sc_dt::uint64    adr = trans.get_address();
    unsigned char*   ptr = trans.get_data_ptr();
    unsigned int     len = trans.get_data_length();

    // Clamp to available memory
    if (adr >= MEM_SIZE) return 0;
    unsigned int actual = std::min(len, (unsigned int)(MEM_SIZE - adr));

    if (cmd == tlm::TLM_WRITE_COMMAND)
        memcpy(&mem[adr], ptr, actual);
    else if (cmd == tlm::TLM_READ_COMMAND)
        memcpy(ptr, &mem[adr], actual);

    // No response_status required — return byte count
    return actual;
}
```

There is no requirement to set `response_status`. The return value carries all the information the caller needs.

## Calling transport_dbg from an Initiator or Test Bench

```cpp
// Read 64 bytes from address 0x8000 without advancing time
uint8_t buf[64] = {};
tlm::tlm_generic_payload dbg_trans;

dbg_trans.set_command(tlm::TLM_READ_COMMAND);
dbg_trans.set_address(0x8000);
dbg_trans.set_data_ptr(buf);
dbg_trans.set_data_length(sizeof(buf));
dbg_trans.set_streaming_width(sizeof(buf));
dbg_trans.set_byte_enable_ptr(nullptr);
dbg_trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);

unsigned int bytes = socket->transport_dbg(dbg_trans);
std::cout << "Read " << bytes << " bytes\n";
```

Because no time advances, this can be called from an `SC_METHOD`, a `before_end_of_elaboration` callback, or even before `sc_start()`.

## Debug Transport vs b_transport

| Property | `b_transport` | `transport_dbg` |
|---|---|---|
| Time annotation | Yes (sc_time& t) | None |
| Side effects | Yes (caller expects them) | No (optional) |
| Partial transfer | Error (must transfer all) | Allowed |
| Response status | Required | Not required |
| Can call from SC_METHOD | No | Yes |

## Limitations

- Targets are not required to implement `transport_dbg`. The default implementation in `simple_target_socket` returns 0 bytes, so verify your target provides a real implementation before depending on it.
- MMIO registers with read-clear semantics (e.g., interrupt status flags) must be careful: a debug read clearing a flag would corrupt the running software's view of the hardware.
- Debug transport bypasses any bus arbiters or access-control logic in the interconnect. That is intentional for debugging but means you see the "raw" memory, not what a particular bus master would see.

## Common Pitfalls

- **Confusing `transport_dbg` with `b_transport` for initialization** — if initialization requires side effects (e.g., writing a register that enables clocks), `b_transport` is correct; `transport_dbg` is for non-destructive inspection.
- **Ignoring the return value** — a return of 0 means the address is unmapped; silently proceeding with an uninitialized buffer is a hard-to-trace bug.
- **Calling from an elaboration callback before memory is allocated** — the target's backing array may not be initialized yet; always sequence carefully.

> **Interview answer:** `transport_dbg` is the TLM-2.0 side-channel for non-destructive memory inspection — it takes the same generic payload as `b_transport` but has no time parameter, requires no side effects, allows partial transfers, and can be called from anywhere (including SC_METHOD), making it ideal for debuggers and test-bench verification.
