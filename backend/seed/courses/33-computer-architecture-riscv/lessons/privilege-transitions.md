# Transitions Between Privilege Modes

Privilege levels are not static — software and hardware constantly move between them. Understanding exactly when and how these transitions occur is essential for writing correct boot code, OS kernels, and hypervisors.

## Two Directions of Transition

| Direction | Mechanism | Example |
|---|---|---|
| Lower → Higher (elevation) | Trap (exception, interrupt, or `ecall`) | System call from user process |
| Higher → Lower (descent) | Return-from-trap (`mret` or `sret`) | Kernel returning to user process |

There is no instruction that directly elevates privilege without going through the trap mechanism. This is a deliberate security property: every privilege gain is hardware-mediated.

## Trap-Driven Elevation

When a trap occurs, the CPU performs the following steps atomically (using M-Mode as the example):

1. **Save return address** — The PC of the trapping instruction is written to `mepc`.
2. **Record cause** — `mcause` is written with the exception or interrupt code.
3. **Save trap-specific info** — `mtval` receives additional context (faulting address, etc.).
4. **Snapshot privilege level** — The current privilege level is stored in `mstatus.MPP`.
5. **Disable interrupts** — `mstatus.MIE` is cleared to prevent nested traps (unless configured otherwise).
6. **Jump to handler** — The PC is set to the address in `mtvec`.

If M-Mode has delegated the trap (via `medeleg`/`mideleg`), the same sequence happens using S-Mode CSRs (`sepc`, `scause`, `stval`, `sstatus.SPP`, `stvec`).

## The mstatus.xPP Fields

The "Previous Privilege" fields in `mstatus` record where the CPU was before the trap:

```
mstatus layout (partial):
  Bit 12:11  MPP   — Mode that was active when M-Mode trap occurred
  Bit  8     SPP   — Mode that was active when S-Mode trap occurred
             (1 = S-Mode, 0 = U-Mode)
```

These fields are critical: `mret` and `sret` use them to decide which privilege level to restore.

## Descent: Returning from a Trap

`mret` in M-Mode:
1. Sets privilege level to `mstatus.MPP`.
2. Sets `mstatus.MIE` to `mstatus.MPIE` (restores pre-trap interrupt enable).
3. Sets `mstatus.MPP` to U-Mode (principle of least privilege — reset to minimum).
4. Jumps to `mepc`.

`sret` in S-Mode mirrors this process with `sstatus.SPP` and `sepc`.

## Worked Example: Full U-Mode → S-Mode → U-Mode Round Trip

```asm
#-------- User program (U-Mode) --------
li    a7, 64          # sys_write
li    a0, 1
la    a1, buf
li    a2, 5
ecall                 # ← trap here; PC saved to sepc

#-------- Kernel trap handler (S-Mode) --------
trap_entry:
    # Registers a0–a7 hold syscall arguments
    # scause == 8 means "environment call from U-Mode"
    csrr  t0, scause
    li    t1, 8
    bne   t0, t1, not_syscall

    # Dispatch syscall
    call  do_syscall        # result in a0

    # Advance sepc past the ecall instruction
    csrr  t0, sepc
    addi  t0, t0, 4
    csrw  sepc, t0

    # Restore user registers, then:
    sret                    # ← descend back to U-Mode at sepc
```

## Delegation and the Trap Route

```
Trap occurs in U-Mode
        │
        ▼
Is the cause delegated by medeleg/mideleg?
    ├─ YES → deliver to S-Mode (stvec, sepc, scause, sstatus)
    └─ NO  → deliver to M-Mode (mtvec, mepc, mcause, mstatus)
```

Delegation is set once at boot by M-Mode firmware. Changing delegation while the system is running is possible but unusual.

## Nested Traps

By default, taking a trap disables interrupts (clears `xIE`). A trap handler that needs to support nested traps must explicitly re-enable interrupts after saving state. Kernels typically do this carefully to avoid unbounded stack growth.

```c
// Simplified Linux-style re-enabling of interrupts in trap handler
void trap_handler(void) {
    save_registers();
    enable_interrupts();    // csrsi sstatus, SIE
    dispatch_trap();
    disable_interrupts();   // csrci sstatus, SIE
    restore_registers();
    // sret
}
```

## Common Pitfall

A common bug is forgetting to advance `sepc` by 4 after an `ecall`. Unlike exceptions (page fault, illegal instruction) where you typically want to re-execute or skip to a handler, after an `ecall` you must resume at the instruction *after* the `ecall`. Failing to increment `sepc` causes an infinite trap loop.

> **Interview answer:** Privilege transitions in RISC-V are hardware-mediated: elevation happens through traps (which save the return address in mepc/sepc and jump to a handler), and descent happens through mret/sret (which restore the previous privilege level and jump to mepc/sepc).
