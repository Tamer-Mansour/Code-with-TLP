# The RISC-V Trap Model

A **trap** in RISC-V is any event that causes the processor to stop normal execution and transfer control to a designated handler routine. Traps are the backbone of operating systems, enabling privilege escalation, hardware interrupt servicing, and fault recovery — all in a uniform, hardware-enforced mechanism.

## What Qualifies as a Trap?

RISC-V groups trap-causing events into two categories:

| Category | Triggered by | Examples |
|---|---|---|
| **Exception** | Current instruction | Illegal opcode, page fault, misaligned access, ecall |
| **Interrupt** | External asynchronous event | Timer, software interrupt, external device |

Both types funnel through the same hardware pathway. From the programmer's perspective the only difference is the MSB of `mcause`.

## The Three Privilege Levels

RISC-V defines up to three privilege levels that matter for traps:

- **M-mode (Machine)** — highest privilege, always present, runs firmware/bootloader
- **S-mode (Supervisor)** — optional, runs OS kernels
- **U-mode (User)** — lowest privilege, runs application code

By default, all traps are taken in M-mode. Delegation registers (`medeleg`, `mideleg`) can redirect selected traps to S-mode.

## The Core Trap CSRs

Six CSRs are central to trap handling at M-mode:

| CSR | Role |
|---|---|
| `mtvec` | Trap vector base address and mode |
| `mepc` | Exception Program Counter (return address) |
| `mcause` | Cause code (interrupt bit + cause number) |
| `mtval` | Additional fault information (faulting address, bad instruction) |
| `mstatus` | Global interrupt enable bits and privilege tracking |
| `mscratch` | Scratch register for the trap handler to save context |

S-mode has a mirror set: `stvec`, `sepc`, `scause`, `stval`, `sstatus`, `sscratch`.

## What Happens at the Hardware Level

When a trap is taken the CPU atomically performs these steps (before your first handler instruction executes):

1. The current PC is saved to `mepc`.
2. The cause code is written to `mcause`.
3. Auxiliary information is written to `mtval` (may be zero for some causes).
4. The previous privilege level and interrupt-enable state are saved in `mstatus.MPP` / `mstatus.MPIE`.
5. Machine-level interrupts are disabled (`mstatus.MIE` cleared).
6. The privilege level is raised to M-mode.
7. The PC jumps to the address encoded in `mtvec`.

This sequence is **atomic from the programmer's perspective** — no partial state is visible.

## Returning from a Trap

The `mret` instruction reverses the hardware trap entry:

- PC is restored from `mepc`.
- Privilege is restored from `mstatus.MPP`.
- `mstatus.MIE` is restored from `mstatus.MPIE`.

```asm
# Minimal trap return
csrr  t0, mepc        # read saved PC
addi  t0, t0, 4       # advance past the faulting instruction (for exceptions)
csrw  mepc, t0
mret                  # atomically restore privilege and jump back
```

## Why This Model Is Elegant

RISC-V deliberately keeps the trap model minimal and orthogonal:

- A single entry point per privilege level reduces hardware complexity.
- Delegation lets the OS handle its own traps without M-mode round-trips.
- The `mscratch` register gives the handler a safe scratch pad before it can save general-purpose registers.

> **Interview answer:** In RISC-V a trap is any control-flow transfer triggered by an exception or interrupt. The hardware atomically saves the PC to `mepc`, encodes the cause in `mcause`, disables interrupts, elevates to M-mode, and jumps to `mtvec`. The handler uses `mret` to return.

## Common Pitfalls

- Forgetting to **advance `mepc` by 4** after handling a synchronous exception causes an infinite re-trap loop.
- Enabling interrupts (`mstatus.MIE`) inside a handler without saving/restoring all CSRs risks corrupting handler state on a nested trap.
- `mtval` is not always meaningful — its content is cause-specific and may be zero for causes that have no associated address.
