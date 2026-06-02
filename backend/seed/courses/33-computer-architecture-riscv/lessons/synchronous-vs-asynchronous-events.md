# Synchronous vs Asynchronous Events

One of the most fundamental distinctions in processor control-flow is whether a disruptive event is **synchronous** (tied to a specific instruction) or **asynchronous** (independent of the instruction stream). This distinction determines how the processor saves state, what the return address means, and whether the event is reproducible.

---

## Synchronous Events

A synchronous event occurs as a direct, deterministic consequence of the instruction the CPU is currently executing. If you run the same program with the same inputs and the same initial state, the same instruction will always trigger the same event.

Examples:
- **Arithmetic exception** — division by zero.
- **Page fault** — a virtual address that is not mapped.
- **Illegal instruction** — an opcode the CPU does not recognize.
- **`ecall` / `ebreak`** — deliberate software traps in RISC-V.

Because the event is tied to a precise instruction, the hardware can save an exact snapshot of architectural state and report the exact program counter (`mepc` in RISC-V) that caused the problem.

### Preciseness guarantee

For synchronous exceptions the processor guarantees that:
1. All instructions before the faulting one have completed (their results are visible).
2. The faulting instruction and all instructions after it appear as if they have not executed.

This is called a **precise exception** and is the default model in RISC-V.

---

## Asynchronous Events

An asynchronous event is raised by a source external to the current instruction stream — a peripheral, a timer, or another CPU core. The event can arrive at any clock cycle, independent of what instruction the CPU happens to be executing.

Examples:
- **Timer interrupt** — a hardware counter reaching its reload value.
- **UART receive interrupt** — a byte arriving on a serial port.
- **External interrupt** — a GPIO pin toggled by a sensor.

Because the event has no relationship to any particular instruction, the processor waits for a safe point (usually the commit of the current instruction) before handling it. The saved `mepc` points to the **next** instruction that should run after the handler returns, not to an instruction that caused the interrupt.

---

## Impact on the return address

This is a common interview pitfall:

| Event type  | `mepc` points to              | Reason                                       |
|-------------|-------------------------------|----------------------------------------------|
| Interrupt   | Next instruction after the interrupted PC | Interrupted instruction already completed |
| Recoverable exception (page fault) | Faulting instruction | Handler fixes the problem; re-execute the instruction |
| Non-recoverable exception | Faulting instruction | OS will terminate the process |
| `ecall`     | The `ecall` instruction itself | Handler advances `mepc` by 4 before returning |

```asm
# Typical ecall handler epilogue: advance past the ecall
csrr  t0, mepc
addi  t0, t0, 4
csrw  mepc, t0
mret              # return to instruction after ecall
```

---

## Timing diagram intuition

```
Instruction stream:  I1  I2  I3  I4  I5 ...
                                 ^
                                 |
              Synchronous exception fires HERE (caused by I3)
              Asynchronous interrupt can fire ANYWHERE ↕
```

---

## Why the distinction matters in hardware design

Out-of-order processors execute instructions in a different order than the program specifies. Handling asynchronous interrupts in such a pipeline is straightforward — the CPU picks a commit boundary. Handling synchronous exceptions precisely is harder: instructions ahead of the faulter in the pipeline must be squashed without changing visible state.

Processors that do not guarantee precise synchronous exceptions are said to generate **imprecise exceptions** — a topic covered in the "Precise vs Imprecise Exceptions" lesson.

---

## RISC-V register snapshot

When any trap fires the hardware atomically performs:

```
mepc    ← PC to resume (see table above)
mcause  ← interrupt/exception cause code
mstatus.MPIE ← mstatus.MIE   (save interrupt-enable bit)
mstatus.MIE  ← 0              (disable interrupts)
mstatus.MPP  ← current privilege mode
PC      ← mtvec (trap vector)
```

This atomic snapshot ensures the handler always sees a consistent machine state.

---

> **Interview answer:** A synchronous event is caused by the currently executing instruction and is reproducible — it always fires at the same instruction. An asynchronous event is triggered by external hardware at an unpredictable time. The key practical difference is the saved return address: for synchronous exceptions it typically points to the faulting instruction so the handler can re-execute it; for asynchronous interrupts it points to the next instruction to resume after the handler returns.
