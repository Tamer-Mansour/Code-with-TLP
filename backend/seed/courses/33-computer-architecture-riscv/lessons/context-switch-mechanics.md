# Context Switch Mechanics on RISC-V

A context switch is the act of saving one process's CPU state and restoring another's. It is the lowest-level mechanism that makes multitasking possible. On RISC-V the hardware gives the OS almost nothing for free, so understanding what must be saved — and in what order — is essential.

## What Constitutes a Process Context?

On a RISC-V core, a process's CPU context is everything that describes "where the computation is" at a point in time:

| Category | Registers |
|----------|-----------|
| Integer registers | `x0`–`x31` (32 general-purpose registers) |
| Program counter | `pc` (saved in `sepc` on trap entry) |
| Floating-point registers | `f0`–`f31` + `fcsr` (if F/D extension enabled) |
| Supervisor CSRs | `sstatus`, `sepc`, `scause`, `stvec`, `satp`, etc. |

`x0` is always zero — no need to save it. The OS also maintains the page-table root (`satp`) per process, which is swapped atomically with a TLB flush.

## The Two-Phase Save

A context switch on RISC-V happens in two logical phases:

**Phase 1 — Hardware (automatic on any trap):**
- PC → `sepc`
- Privilege mode → `sstatus.SPP`
- Interrupt enable → `sstatus.SPIE` (clears current IE)
- Jump to `stvec`

**Phase 2 — Software (the trap handler must do this):**

```asm
# Entry: save all caller- and callee-saved registers to the process's trapframe
# a0 already holds the trapframe pointer (set up before reaching here)
sd  ra,  0(a0)
sd  sp,  8(a0)
sd  gp,  16(a0)
sd  tp,  24(a0)
sd  t0,  32(a0)
# ... repeat for all 32 registers
sd  t6,  248(a0)
```

The trapframe is a per-process structure in kernel memory. In xv6-riscv it is mapped at a fixed virtual address (`TRAPFRAME`) so the trap handler can reach it without knowing the current kernel stack.

## The Scheduler Hand-Off

Once the current process's state is saved, the kernel runs the scheduler, which selects a new process and calls `swtch()`:

```c
// Simplified xv6 swtch: saves callee-saved regs, restores next process's
void swtch(struct context *old, struct context *new);
```

`swtch` only saves/restores **callee-saved** registers (`ra`, `sp`, `s0`–`s11`) because it is a normal function call — the C ABI already guarantees caller-saved registers are not preserved across calls.

```asm
swtch:
    sd ra,  0(a0)    # save ra into old context
    sd sp,  8(a0)
    sd s0,  16(a0)
    # ... s1-s11
    ld ra,  0(a1)    # restore ra from new context
    ld sp,  8(a1)
    ld s0,  16(a1)
    # ... s1-s11
    ret              # jumps to new process's scheduler return point
```

## Restoring a Process

To resume a process, the kernel reverses the save:

1. Restore all 32 integer registers from the trapframe.
2. Load `sepc` with the process's saved PC.
3. Set `satp` to the process's page table.
4. Execute `sret` — the hardware restores privilege level, re-enables interrupts, and jumps to `sepc`.

**Critical ordering:** `satp` must be written **before** `sret`, and an `sfence.vma` instruction must follow the `satp` write to flush stale TLB entries. Violating this order causes the process to execute with the wrong address space — a subtle and destructive bug.

## Common Pitfalls

- Saving the trapframe but forgetting `fcsr` when floating-point is in use.
- Using a kernel stack address as the process stack after the switch — each process must have its own kernel stack.
- Forgetting `sfence.vma` after changing `satp`, leading to stale TLB translations.
- `swtch` saves only callee-saved registers: if you call `swtch` without saving caller-saved registers first, they are silently lost.

> **Interview answer:** A RISC-V context switch saves the 32 integer registers (plus FP state) to a per-process trapframe in the trap handler, then calls `swtch()` which saves/restores only callee-saved registers (since it is a C function), updates `satp` + `sfence.vma` for the new address space, and uses `sret` to atomically restore privilege and jump to the saved PC.
