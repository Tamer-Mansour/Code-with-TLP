# Writing a Minimal Trap Handler

Theory becomes real when you write an actual trap handler. This lesson builds a minimal but complete M-mode trap handler in RISC-V assembly, explains every design decision, and then shows the equivalent C approach using GCC compiler support.

## What the Handler Must Do

A correct minimal trap handler must:

1. Save all general-purpose registers it will touch (or all of them for a full context switch).
2. Identify the trap cause from `mcause`.
3. Dispatch to exception or interrupt handling.
4. Restore all saved registers.
5. Return with `mret`.

It must do this without corrupting any register that was live in the interrupted code.

## The mscratch Bootstrap Problem

On trap entry we have no free register — all 32 GPRs belong to the interrupted context. The solution is `mscratch`:

```asm
# Before any trap can occur, M-mode boot code runs:
la    t0, _trap_stack_top   # address of per-hart trap stack
csrw  mscratch, t0          # store it in mscratch
```

On trap entry the handler uses `csrrw` to atomically swap `mscratch` with `t0`, giving us one free register while preserving the original `t0` in `mscratch`:

```asm
_trap_entry:
    csrrw  t0, mscratch, t0   # t0 = trap stack ptr, mscratch = original t0
```

## Full Minimal Trap Handler (RV32)

```asm
    .section .text
    .align 4
    .global _trap_entry

_trap_entry:
    # ---- Save context to trap stack ----
    csrrw  t0, mscratch, t0       # t0 = trap stack base; save original t0
    sw     ra,   0(t0)
    sw     sp,   4(t0)
    sw     gp,   8(t0)
    sw     tp,  12(t0)
    sw     t1,  16(t0)
    sw     t2,  20(t0)
    sw     s0,  24(t0)
    sw     s1,  28(t0)
    sw     a0,  32(t0)
    sw     a1,  36(t0)
    sw     a2,  40(t0)
    sw     a3,  44(t0)
    sw     a4,  48(t0)
    sw     a5,  52(t0)
    sw     a6,  56(t0)
    sw     a7,  60(t0)
    sw     s2,  64(t0)
    sw     s3,  68(t0)
    sw     s4,  72(t0)
    sw     s5,  76(t0)
    sw     s6,  80(t0)
    sw     s7,  84(t0)
    sw     s8,  88(t0)
    sw     s9,  92(t0)
    sw     s10, 96(t0)
    sw     s11,100(t0)
    sw     t3, 104(t0)
    sw     t4, 108(t0)
    sw     t5, 112(t0)
    sw     t6, 116(t0)
    csrr   t1, mscratch           # t1 = original t0
    sw     t1, 120(t0)            # save original t0

    # ---- Set up C stack pointer ----
    mv     sp, t0

    # ---- Dispatch ----
    csrr   a0, mcause
    csrr   a1, mepc
    csrr   a2, mtval
    bltz   a0, _interrupt_handler
    call   exception_handler      # exception_handler(mcause, mepc, mtval)
    j      _trap_exit

_interrupt_handler:
    call   interrupt_handler      # interrupt_handler(mcause, mepc, mtval)

_trap_exit:
    # ---- Restore context ----
    csrr   t0, mscratch           # t0 = trap stack base (still there)
    lw     ra,   0(t0)
    lw     sp,   4(t0)
    lw     gp,   8(t0)
    lw     tp,  12(t0)
    lw     t1,  16(t0)
    lw     t2,  20(t0)
    lw     s0,  24(t0)
    lw     s1,  28(t0)
    lw     a0,  32(t0)
    lw     a1,  36(t0)
    lw     a2,  40(t0)
    lw     a3,  44(t0)
    lw     a4,  48(t0)
    lw     a5,  52(t0)
    lw     a6,  56(t0)
    lw     a7,  60(t0)
    lw     s2,  64(t0)
    lw     s3,  68(t0)
    lw     s4,  72(t0)
    lw     s5,  76(t0)
    lw     s6,  80(t0)
    lw     s7,  84(t0)
    lw     s8,  88(t0)
    lw     s9,  92(t0)
    lw     s10, 96(t0)
    lw     s11,100(t0)
    lw     t3, 104(t0)
    lw     t4, 108(t0)
    lw     t5, 112(t0)
    lw     t6, 116(t0)
    lw     t0, 120(t0)            # restore original t0 last
    mret
```

## C-Level Handlers

```c
#include <stdint.h>

// Called by the assembly stub
void exception_handler(long mcause, uintptr_t mepc, uintptr_t mtval) {
    switch (mcause) {
    case 8:   // ecall from U-mode
        handle_syscall();
        // Advance mepc past the ecall instruction
        write_csr(mepc, mepc + 4);
        break;
    case 2:   // illegal instruction
        // Try to emulate or kill the process
        handle_illegal_insn(mepc, mtval);
        write_csr(mepc, mepc + 4);
        break;
    case 13:  // load page fault
        handle_page_fault(mtval, /*write=*/0);
        // mepc unchanged; hardware will retry the load
        break;
    default:
        // Unhandled exception: halt
        while (1) {}
    }
}

void interrupt_handler(long mcause, uintptr_t mepc, uintptr_t mtval) {
    long code = mcause & 0x7FFFFFFF;
    switch (code) {
    case 7:   // machine timer interrupt
        schedule_next_tick();   // update mtimecmp
        break;
    case 11:  // machine external interrupt (via PLIC)
        plic_handle();
        break;
    case 3:   // machine software interrupt (IPI)
        handle_ipi();
        *(volatile uint32_t*)(CLINT_BASE) = 0;  // clear msip
        break;
    }
    // mepc unchanged; interrupt resumes at mepc after mret
}
```

## Initialization

```c
void trap_init(void) {
    extern void _trap_entry(void);
    // Direct mode: all traps go to _trap_entry
    write_csr(mtvec, (uintptr_t)_trap_entry);

    // Set up trap stack in mscratch (per-hart)
    extern uint8_t _trap_stack[1024];
    write_csr(mscratch, (uintptr_t)(_trap_stack + 1024));

    // Enable machine timer interrupt
    set_csr(mie, MIE_MTIE);
    set_csr(mstatus, MSTATUS_MIE);
}
```

## Design Decisions and Trade-offs

| Decision | Reason |
|---|---|
| Save **all** GPRs | Safe for any handler code; necessary for context switch |
| Use `mscratch` for trap stack | Provides a stable base before `sp` is restored |
| Pass `mcause/mepc/mtval` as args | Avoids re-reading CSRs in C handler |
| Advance `mepc` in the exception handler | Keeps the dispatch logic close to cause-specific handling |
| Restore `t0` last | `t0` holds the stack pointer during restore; must be last |

> **Interview answer:** A minimal RISC-V trap handler uses `csrrw t0, mscratch, t0` to get a free register, saves all GPRs to a trap stack, reads `mcause` to dispatch between exception and interrupt handlers, then restores all registers and executes `mret`. The assembly stub handles context save/restore; C functions handle the logic.

## Common Pitfalls

- Saving to the application's `sp` — if `sp` is corrupt (stack overflow) saving to it will fault again. Use the `mscratch`-based trap stack instead.
- Forgetting to restore `t0` last — since `t0` holds the frame pointer during restoration, restoring it early corrupts subsequent loads.
- Not re-enabling interrupts for nested interrupt handling — by default `mret` restores `mstatus.MIE` from `mstatus.MPIE`, which is what you want for a simple non-nested handler.
