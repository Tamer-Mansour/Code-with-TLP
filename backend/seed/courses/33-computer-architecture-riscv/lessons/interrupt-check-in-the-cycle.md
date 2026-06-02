# Where Interrupts Fit in the Cycle

A program running on a CPU does not exist in isolation. At any moment, a hardware timer might fire, a network packet might arrive, or a user might press a key. These **interrupts** demand that the processor stop what it is doing and respond — but stopping mid-instruction would corrupt the machine's state. So where, exactly, does the processor check for interrupts, and how does it safely respond?

## Interrupts vs. Exceptions: A Quick Distinction

Both interrupts and exceptions divert the instruction cycle from its normal path, but they differ in origin:

| Term | Origin | Example |
|---|---|---|
| **Interrupt** (async) | External hardware | Timer, I/O device, network card |
| **Exception** (sync) | The instruction itself | Illegal opcode, misaligned address, divide by zero |
| **Trap** | Deliberate software | `ECALL` in RISC-V (system call) |

In RISC-V, all three are handled by the same trap mechanism. The `mcause` register distinguishes whether a trap was synchronous (exception) or asynchronous (interrupt).

## The Safe Check Point: End of an Instruction

The processor checks for pending interrupts at the **boundary between two instruction cycles** — specifically, after the current instruction has fully completed (write-back finished) and before the next instruction's fetch begins. This is the only moment when the architectural state is **completely consistent**:

- All registers reflect the effect of every completed instruction
- The PC points to the *next* instruction (not the one that just finished)
- No partial writes are in progress

```
... [IF][ID][EX][MEM][WB] ──► INTERRUPT CHECK ──► [IF][ID][EX][MEM][WB] ...
        instruction N          ^                      instruction N+1
                               │
                     (or: jump to trap handler)
```

This boundary check is why interrupts are sometimes called **between-instruction interrupts**.

## What Happens When an Interrupt Is Taken

In RISC-V, when a trap is taken, the hardware performs these steps atomically (within one cycle transition):

1. **Save the PC of the interrupted instruction** into `mepc` (Machine Exception PC). For interrupts, this is the address of the next instruction that *would have* executed.
2. **Save the processor status** into `mcause` (cause code) and `mstatus` (privilege and interrupt-enable state).
3. **Disable further interrupts** by clearing the MIE bit in `mstatus` (prevents nested traps from overwriting saved state).
4. **Set the PC to the trap vector** address from the `mtvec` register.
5. Fetch the first instruction of the interrupt handler.

```
Normal flow:     PC = 0x1000 (next instruction to fetch)
Interrupt fires: mepc   ← 0x1000
                 mcause ← 0x80000007  (machine timer interrupt)
                 mstatus.MIE ← 0
                 PC ← mtvec (e.g., 0x0000_0100)
                 → fetch handler
```

To return from the handler, the `MRET` instruction restores `mepc` into the PC and re-enables interrupts.

## Interrupt Latency

**Interrupt latency** is the time from when an interrupt signal is asserted to when the first instruction of the handler executes. In a simple in-order pipeline:

- The current instruction must finish (up to 5 cycles)
- Pipeline flush and trap entry overhead: 1–2 cycles
- Fetch of the handler's first instruction: 1+ cycles (cache miss??)

Modern real-time systems specify a **worst-case interrupt latency** (WCIL). RISC-V processors designed for embedded real-time use (like the SiFive E-series) guarantee single-digit cycle latencies under certain configurations.

## Interrupts in a Pipelined Processor

Pipelining complicates interrupt handling. When an interrupt is detected, multiple instructions are in flight simultaneously. The processor must:

1. **Complete or drain** instructions already past decode (or squash them if they have not written state yet)
2. **Flush** instructions in the fetch and decode stages (they have not committed state)
3. **Save PC of the instruction at the commit point** (the last instruction that fully completed)

This is why the **commit stage** (or write-back boundary) is the canonical interrupt check point even in out-of-order processors — state is only "official" once committed.

## Interrupt Enable/Disable

Programs can temporarily **disable interrupts** to protect critical sections. In RISC-V M-mode:

```asm
csrrci x0, mstatus, 0x8   # clear MIE bit → disable machine interrupts
# ... critical section ...
csrrsi x0, mstatus, 0x8   # set MIE bit → re-enable machine interrupts
```

Between the disable and re-enable, any interrupt will be **pending** but not acted upon. When re-enabled, if the interrupt is still asserted, the trap fires at the next instruction boundary.

## Common Pitfalls

- **Confusing mepc semantics for interrupts vs. exceptions.** For exceptions (e.g., illegal instruction), `mepc` points to the *faulting* instruction. For interrupts, it points to the *next* instruction that would have run. MRET must return to the right place.
- **Forgetting to save/restore registers in the handler.** The interrupt handler is just assembly code — it uses registers. If it clobbers a register without saving it, the interrupted program sees corrupted state.
- **Assuming interrupt latency is fixed.** Cache misses, pipeline depth, and priority arbitration all affect latency. Worst-case analysis is essential for real-time systems.
- **Nesting interrupts carelessly.** Re-enabling interrupts inside a handler (to allow higher-priority interrupts) requires carefully saving `mepc`, `mcause`, and `mstatus` on the stack first.

> **Interview answer:** Interrupts are checked at instruction boundaries — after write-back completes and before the next fetch begins — the only moment when architectural state is fully consistent. The hardware then saves the PC and status registers, sets the PC to the trap vector, and jumps to the interrupt handler, returning via MRET.
