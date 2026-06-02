# Saving and Restoring Context

When a trap fires, the processor abandons the current execution stream and jumps to a handler. After the handler finishes, execution must resume as if nothing happened — or, in the case of a context switch, a completely different thread must be resumed. This requires saving and later restoring the **architectural context**: all state that the interrupted code depends on.

---

## What constitutes "context"?

The minimal architectural context for a RISC-V hart consists of:

| Category | Registers |
|----------|-----------|
| Integer registers | `x0`–`x31` (32 GPRs; `x0` always zero, but save slot still needed for alignment) |
| Program counter | Saved automatically in `mepc` by hardware |
| Floating-point registers | `f0`–`f31` (if F/D extension present) |
| Floating-point status | `fcsr` (rounding mode + accrued flags) |
| Vector registers | `v0`–`v31` (if V extension present) |
| Application CSRs | `mstatus` / `sstatus`, `mie` / `sie`, etc. (only relevant ones) |

The hardware automatically saves `mepc`, `mcause`, `mstatus`, and `mtval` at trap entry. Everything else is the handler's responsibility.

---

## The RISC-V calling convention and interrupt handlers

RISC-V defines caller-saved and callee-saved registers (ABI). Interrupt handlers do not follow the ABI with respect to a caller — the interrupted code could be *any* instruction. Therefore a correct ISR must save **all** registers it could clobber before using them.

A minimal assembly prologue for a trap handler:

```asm
.global trap_entry
.align 4
trap_entry:
    # Allocate stack frame: 32 GPRs × 8 bytes = 256 bytes
    addi  sp, sp, -256
    sd    ra,   0(sp)
    sd    t0,   8(sp)
    sd    t1,  16(sp)
    sd    t2,  24(sp)
    sd    a0,  32(sp)
    sd    a1,  40(sp)
    sd    a2,  48(sp)
    sd    a3,  56(sp)
    # ... save all caller-saved registers ...

    # Call C handler
    call  c_trap_handler

    # Restore
    ld    ra,   0(sp)
    ld    t0,   8(sp)
    ld    t1,  16(sp)
    ld    t2,  24(sp)
    ld    a0,  32(sp)
    ld    a1,  40(sp)
    # ...
    addi  sp, sp, 256

    mret  # restore mstatus.MIE from MPIE, restore privilege, jump to mepc
```

---

## Minimal vs full context save

**Minimal save** — only caller-saved registers (`ra`, `t0`–`t6`, `a0`–`a7`). Sufficient if the handler is a leaf function that does not call anything else and does not need callee-saved registers. Saves time and stack space.

**Full save** — all 32 GPRs plus FPU state. Required when:
- The handler calls other functions (which may use callee-saved registers).
- The handler performs a context switch (different thread needs to be resumed).
- The handler enables nested interrupts (re-entrant handler).

---

## Thread context block (TCB) layout

An RTOS stores the full context in a per-thread **Thread Control Block**:

```c
typedef struct {
    uintptr_t regs[32];   // x0..x31
    uintptr_t pc;         // saved mepc
    uintptr_t mstatus;    // saved mstatus
    double    fregs[32];  // f0..f31 (if FPU present)
    uint32_t  fcsr;       // FPU control/status
    // ... scheduling metadata ...
} TCB;
```

During a context switch inside the trap handler, the current TCB is filled in, then the next thread's TCB is loaded.

---

## The `mret` instruction

`mret` is the return-from-machine-mode-trap instruction. It atomically:

1. Restores `mstatus.MIE` from `mstatus.MPIE`.
2. Restores the privilege level from `mstatus.MPP`.
3. Sets `pc = mepc`.

```asm
# Before mret:
#   mstatus.MPIE = 1  (was enabled before trap)
#   mstatus.MPP  = U  (interrupted code was in user mode)
#   mepc         = 0x1000  (return address)
mret
# After mret:
#   mstatus.MIE = 1, privilege = U, pc = 0x1000
```

---

## Common pitfalls

- **Forgetting `fcsr`** — FPU accrued exception flags carry across the handler boundary and corrupt the interrupted code's status checks.
- **Not saving `ra` (x1)** — any `jal` or `call` inside the handler overwrites `ra`.
- **Stack overflow** — deep interrupt nesting without tracking stack usage can overflow the interrupt stack silently.
- **Saving to the wrong stack** — handlers must switch to a dedicated interrupt stack before pushing; using the user stack is a security risk.

---

> **Interview answer:** Context save is the act of pushing all architectural registers the handler might modify onto a dedicated stack (or TCB) before touching them, and restoring them before returning with `mret`. The hardware automatically saves `mepc`, `mcause`, and `mstatus`; everything else — all 32 GPRs and the FPU state — must be saved by software in the trap entry stub.
