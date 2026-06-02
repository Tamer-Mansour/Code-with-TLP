# Debugging and Tracing Virtual Prototypes

Debugging a virtual prototype is different from debugging application software. The bug might be in the firmware, in the platform model, or in the interaction between the two. A disciplined approach using the right tools is essential.

## The Debugging Stack

Virtual prototype debugging operates across three layers simultaneously:

1. **Firmware / software** — wrong algorithm, null pointer, stack overflow.
2. **Platform model** — peripheral register behaviour wrong, DMA model incorrect, interrupt not firing.
3. **Interaction / timing** — correct model + correct firmware, but the sequence of events is wrong.

Always identify which layer is failing before choosing a debug tool.

## GDB Integration

Most ISA simulators expose a **GDB remote serial protocol (RSP)** stub. This lets you attach GDB and step through firmware as if you were on real hardware:

```bash
# Terminal 1: start QEMU in GDB server mode
qemu-system-riscv32 -machine virt -kernel firmware.elf -s -S

# Terminal 2: connect GDB
riscv32-unknown-elf-gdb firmware.elf
(gdb) target remote :1234
(gdb) break main
(gdb) continue
(gdb) info registers
(gdb) x/4wx 0x80000000    # examine memory
```

With Spike:

```bash
spike -d --rbb-port=9824 pk firmware.elf &
riscv64-unknown-elf-gdb firmware.elf -ex "target remote :9824"
```

## Instruction Tracing

Instruction traces capture every instruction executed along with register values. This is invaluable for:

- Comparing two simulators (golden reference vs. implementation under test).
- Finding the first divergence point between expected and actual behaviour.
- Profiling hot code paths.

### Spike commit log

```bash
spike --log-commits pk firmware.elf 2> trace.log
# trace.log contains lines like:
# core   0: 0x80000000 (0x00000513) addi    a0, zero, 0
# core   0: 3 0x80000004 (0x00000593) addi    a1, zero, 0
```

### QEMU plugin tracing

```bash
qemu-system-riscv64 \
  -plugin /path/to/libinsn.so,arg=trace.out \
  -kernel firmware.elf -nographic
```

## Memory and Register Watchpoints

Watchpoints fire when a specific memory address or register is written — far more useful than breakpoints when tracking down a corrupted data structure:

```gdb
(gdb) watch *(uint32_t*)0x20000100   # Break when address 0x20000100 is written
(gdb) rwatch *(uint32_t*)0x20000100  # Break on read
(gdb) awatch *(uint32_t*)0x20000100  # Break on read or write
```

## Printf-Style Tracing in the Model

When the bug is in the peripheral model itself, the quickest approach is logging inside the model:

```cpp
// In a SystemC TLM peripheral
void UART::b_transport(tlm::tlm_generic_payload& trans, sc_core::sc_time& delay) {
    uint64_t addr = trans.get_address();
    bool is_write = (trans.get_command() == tlm::TLM_WRITE_COMMAND);
    fprintf(stderr, "[UART] %s addr=0x%08lx time=%s\n",
            is_write ? "WRITE" : "READ",
            addr,
            sc_core::sc_time_stamp().to_string().c_str());
    // ...
}
```

## Differential Debugging: Two-Simulator Comparison

The most powerful technique for finding ISA simulator bugs is **differential debugging**:

1. Run the same firmware on Spike (gold reference) and your simulator.
2. Dump register state after every N instructions.
3. Compare the dumps — the first divergence identifies the faulty instruction handler.

```python
# Pseudocode: differential trace comparison
spike_trace = parse_trace("spike_trace.log")
sim_trace   = parse_trace("my_sim_trace.log")

for i, (s, m) in enumerate(zip(spike_trace, sim_trace)):
    if s.regs != m.regs or s.pc != m.pc:
        print(f"Divergence at step {i}: PC={s.pc}")
        print(f"  Spike: {s.regs}")
        print(f"  Mine:  {m.regs}")
        break
```

## Common Pitfalls

- **Peripheral not asserting interrupt**: check that the interrupt controller model is connected and the pending bit is actually set. Trace `mip`/`mie` CSRs in the firmware.
- **Unaligned access silently ignored**: RISC-V raises an alignment fault on unaligned word/doubleword access unless the Zicclsm extension is enabled. Ensure the model raises the correct exception.
- **Simulation time vs. wall time**: when the model asserts timing delays, verify that `sc_time_stamp()` or the simulator clock is advancing correctly — a stuck clock produces infinite loops.

## Interview Answer

> "I debug virtual prototypes in three layers: firmware bugs with GDB attached via RSP, model bugs with printf tracing inside the peripheral, and interaction bugs with differential comparison against a golden reference like Spike. Watchpoints and commit logs are the most efficient tools for finding silent data corruption."
