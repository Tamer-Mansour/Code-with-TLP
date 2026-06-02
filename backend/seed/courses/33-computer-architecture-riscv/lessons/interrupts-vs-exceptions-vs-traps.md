# Interrupts vs Exceptions vs Traps

Modern processors distinguish between several kinds of control-flow disruptions that force the CPU to abandon normal sequential execution and jump to a handler routine. The three most important categories are **interrupts**, **exceptions**, and **traps**. Understanding the difference is essential for writing operating systems, embedded firmware, and any software that interacts with hardware.

---

## Interrupts

An **interrupt** is an asynchronous signal raised by hardware external to the currently executing instruction stream. A network card receiving a packet, a timer reaching its count, or a keyboard key being pressed all generate interrupts. The CPU finishes whatever it is doing at a convenient boundary, saves its state, and vectors to an interrupt service routine (ISR).

Key traits:
- **Asynchronous** — the interrupt arrives independently of the current instruction.
- **External** — the source is a peripheral or another hardware unit.
- **Maskable (usually)** — software can temporarily disable most interrupts by clearing a flag in a status register (e.g., clearing `mstatus.MIE` in RISC-V machine mode).

---

## Exceptions

An **exception** is a synchronous event caused by the instruction currently executing. Division by zero, an illegal opcode, a page fault, or a misaligned memory access are all exceptions.

Key traits:
- **Synchronous** — reproducible; the same instruction in the same state always triggers the same exception.
- **Internal** — the CPU itself detects the problem.
- **Precise (usually)** — the architectural state before the faulting instruction is exactly known.

Common RISC-V exception causes (`mcause` register, `Interrupt` bit = 0):

| Code | Cause |
|------|-------|
| 0    | Instruction address misaligned |
| 2    | Illegal instruction |
| 5    | Load access fault |
| 8    | Environment call from U-mode (`ecall`) |
| 12   | Instruction page fault |

---

## Traps

**Trap** is an umbrella term used in RISC-V (and many other architectures) for any event that causes control to be transferred to a privileged handler. It encompasses both interrupts and exceptions. Some authors also use "trap" to mean a deliberate, software-generated exception — the `ecall` or `ebreak` instruction being the canonical example.

In RISC-V the word *trap* appears in register names (`mcause`, `mtval`, `mepc`) precisely because the same registers handle both interrupts and exceptions.

---

## Side-by-side comparison

| Property        | Interrupt            | Exception              | Trap (software)        |
|-----------------|----------------------|------------------------|------------------------|
| Cause           | External hardware    | Faulting instruction   | Deliberate instruction |
| Timing          | Asynchronous         | Synchronous            | Synchronous            |
| Maskable?       | Usually yes          | Usually no             | No                     |
| Example         | Timer IRQ            | Page fault             | `ecall`, `ebreak`      |
| Return address  | Next instruction     | Faulting or next       | Instruction after trap |

---

## RISC-V `mcause` register

The top bit of `mcause` distinguishes the two broad families:

```
mcause[XLEN-1] = 1  →  interrupt
mcause[XLEN-1] = 0  →  exception (synchronous)
```

```asm
# After a trap, read mcause to dispatch
csrr  t0, mcause
bltz  t0, handle_interrupt   # high bit set → interrupt
j     handle_exception
```

---

## Worked example

Suppose a program executes `lw t0, 3(sp)` — a misaligned load on a 4-byte boundary.

1. The CPU detects the misalignment during address calculation.
2. It saves `pc` to `mepc` (the address of the `lw`), sets `mcause = 4` (load address misaligned), and saves privilege mode in `mstatus.MPP`.
3. Control jumps to `mtvec` (the trap vector base).
4. The handler either fixes the misalignment (emulation) or terminates the process.

This is a synchronous exception — every execution of that instruction with that stack pointer will fault.

---

> **Interview answer:** An interrupt is an asynchronous hardware signal; an exception is a synchronous error raised by the current instruction; a trap is the general mechanism (or a deliberate `ecall`/`ebreak`) that transfers control to a privileged handler. In RISC-V the same CSRs (`mepc`, `mcause`, `mtvec`) handle all three.
