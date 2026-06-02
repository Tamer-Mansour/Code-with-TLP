# Debugging and Tracing With a Virtual Prototype

One of the greatest advantages of a virtual prototype over real hardware is the depth of observability it provides. You can halt execution at any simulated moment, inspect every register and memory byte, replay a crash from the beginning, and add instrumentation without reflashing. This lesson covers the key debugging techniques used in production virtual prototype environments.

## GDB + Remote Serial Protocol (RSP)

Most ISSes expose a **GDB stub** via the Remote Serial Protocol. QEMU, Spike, and commercial platforms all support this. The OS or firmware runs on the ISS; GDB runs on the host and communicates over a TCP socket.

```bash
# Terminal 1: Start QEMU with GDB stub on port 1234
qemu-system-riscv64 \
    -M virt -kernel vmlinux \
    -nographic -s -S          # -s: port 1234, -S: halt at reset

# Terminal 2: Connect GDB
riscv64-unknown-linux-gnu-gdb vmlinux
(gdb) target remote :1234
(gdb) b start_kernel          # breakpoint at kernel entry
(gdb) c
(gdb) info registers          # dump all CPU registers
(gdb) x/20i $pc               # disassemble 20 instructions at PC
```

Because the ISS halts on breakpoints deterministically, you can break inside interrupt handlers, inspect the stack frame, and single-step through exception entry — impossible on real silicon without a JTAG probe.

## Instruction Tracing

An instruction trace logs every PC the processor executes, along with register values and memory accesses. This is invaluable for diagnosing crashes in code with no debug symbols.

```bash
# QEMU instruction trace (log every executed instruction)
qemu-system-riscv64 -M virt -kernel vmlinux \
    -d in_asm,cpu,int 2>trace.log
```

The trace file allows you to:
- Find the exact instruction before a crash.
- Confirm that a branch was taken or not taken.
- Measure how many instructions elapsed between two events.

> **Interview answer:** A virtual prototype enables deterministic replay, instruction-level tracing, and hardware watchpoints without physical access; GDB/RSP connects to the ISS stub and halts execution at any cycle, making debugging dramatically more efficient than with real silicon.

## Hardware Watchpoints on MMIO

Because MMIO registers are modeled in software, you can add a watchpoint that fires whenever a specific register is read or written — without any hardware support.

```cpp
// Inside the UART model's write handler
void UART::write(uint32_t offset, uint32_t data) {
    if (offset == 0x00) {
        printf("[TRACE] UART TX: 0x%02x ('%c') at time %s\n",
               data & 0xFF, isprint(data) ? data : '.', sc_time_stamp().to_string().c_str());
    }
    // … normal handling
}
```

This produces a timestamped log of every byte the firmware sends to the UART, which is far more useful than an oscilloscope trace on real hardware.

## Memory Access Logging and ASAN-style Checks

Virtual prototypes can detect memory safety bugs that are invisible on real hardware:

- **Out-of-bounds access** — flag any access outside modeled DRAM ranges.
- **Uninitialized memory reads** — mark bytes as "uninitialized" after reset; warn on read before write.
- **Stack overflow** — place a guard page at the bottom of the stack and raise a fault on access.

```python
# Conceptual: shadow memory checker in a Python ISS
def mem_read(addr, size):
    for byte_addr in range(addr, addr + size):
        if shadow[byte_addr] == UNINITIALIZED:
            print(f"WARNING: read of uninitialized byte at 0x{byte_addr:08x}")
    return memory[addr:addr+size]
```

## Deterministic Replay

Because a virtual prototype has no external non-determinism (no timing jitter, no hardware races), you can **record** an execution and **replay** it exactly:

1. Record all external inputs (UART input bytes, network packets, timer values).
2. On replay, feed the same inputs at the same simulated timestamps.
3. The execution is bit-for-bit identical every time — including the crash.

This allows you to reproduce a one-in-a-million race condition reliably, add instrumentation after the fact, and narrow down the root cause.

## Common Debugging Workflows

| Problem | Tool | Technique |
|---|---|---|
| Kernel panic at boot | GDB + RSP | Break on `panic`, print backtrace |
| Driver timeout | MMIO watchpoint | Log every register read/write |
| Memory corruption | Shadow memory | Mark freed pages, detect stale writes |
| Wrong interrupt | Interrupt trace | Log claim/complete transactions |
| Infinite loop | Instruction trace | Find repeating PC range |

## Pitfalls

- **Non-deterministic host I/O** — if your model reads host wall-clock time, replays are not bit-identical. Always use simulated time.
- **Trace file size** — instruction traces grow at ~50 MB/s of simulated execution. Use filtering (trace only a PC range) to keep files manageable.
- **GDB and hardware threads** — in multi-core QEMU, GDB by default controls all vCPUs; use `set scheduler-locking on` to single-step one hart without advancing others.

Virtual prototype debugging is a superpower in embedded systems development. Mastering these techniques separates engineers who find bugs in hours from those who spend weeks.
