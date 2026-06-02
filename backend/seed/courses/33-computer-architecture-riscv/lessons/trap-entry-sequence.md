# The Trap Entry Sequence Step by Step

Understanding exactly what the hardware does — and in what order — before your first handler instruction executes is essential for writing correct, race-free trap handlers. This lesson walks through every atomic step the RISC-V processor performs when a trap is taken at M-mode.

## Prerequisites

The trap entry sequence applies when:
- A trap is not delegated away (via `medeleg`/`mideleg`), **or**
- The current privilege level is already M-mode.

For S-mode delegation the same sequence applies with the `s`-prefixed CSRs.

## The Seven Atomic Steps

When a trap is taken in M-mode the hardware performs all of the following **before** fetching the first instruction of the handler:

### Step 1 — Save the Return Address in mepc

```
mepc ← PC of the trapping instruction (exceptions)
mepc ← PC of the next instruction    (interrupts)
```

For exceptions `mepc` points **at** the instruction that caused the trap, giving the handler the option to fix the cause and retry. For interrupts it points to the instruction that would have executed next, so `mret` resumes seamlessly.

### Step 2 — Encode the Cause in mcause

```
mcause[XLEN-1] ← 1 (interrupt) or 0 (exception)
mcause[XLEN-2:0] ← cause code
```

The handler reads this immediately to dispatch to the correct sub-handler.

### Step 3 — Write Auxiliary Info to mtval

```
mtval ← faulting address (page faults, misaligned access)
mtval ← bad instruction  (illegal instruction, if it fits)
mtval ← 0               (causes with no relevant extra info)
```

### Step 4 — Save Previous Privilege and Interrupt State in mstatus

```
mstatus.MPP  ← current privilege level (2-bit field)
mstatus.MPIE ← mstatus.MIE   (save current interrupt-enable bit)
mstatus.MIE  ← 0             (disable machine-level interrupts)
```

This is a three-field update in one register. `MPP` lets `mret` know which privilege level to return to. `MPIE` saves the prior interrupt-enable state so `mret` can restore it.

### Step 5 — Elevate Privilege to M-mode

The processor's internal privilege register is set to M-mode. This grants the handler full access to all CSRs and physical memory.

### Step 6 — Jump to the Handler Address from mtvec

```
if mtvec.MODE == 0 (Direct):
    PC ← mtvec.BASE
if mtvec.MODE == 1 (Vectored, interrupts only):
    PC ← mtvec.BASE + 4 × cause_code
```

The lowest two bits of `mtvec` encode the mode; the BASE is 4-byte aligned.

### Step 7 — Fetch and Execute the First Handler Instruction

Normal pipeline operation resumes at the new PC. All six steps above have already completed.

## Visual Summary

```
Normal execution
       │
       ▼
  Trap detected
       │
       ├─ mepc    ← return address
       ├─ mcause  ← cause code
       ├─ mtval   ← auxiliary data
       ├─ mstatus ← save MPP, MPIE; clear MIE
       ├─ privilege ← M-mode
       └─ PC      ← mtvec (direct or vectored)
       │
       ▼
  Handler executes
```

## The Handler's Responsibilities

The hardware only saves four things (mepc, mcause, mtval, partial mstatus). It does **not** save any general-purpose registers. The handler must:

1. Save all registers it uses (typically all of them for a full OS context switch) to the stack or a per-hart scratch area pointed to by `mscratch`.
2. Read `mcause` to identify the trap.
3. Dispatch to the appropriate sub-handler.
4. Restore all saved registers.
5. Execute `mret`.

```asm
_trap_entry:
    # Swap t0 with mscratch to get a free register
    csrrw  t0, mscratch, t0

    # Save the rest of the registers (simplified)
    sw     ra,  0(t0)
    sw     sp,  4(t0)
    # ... save all other registers ...

    # Dispatch
    csrr   t1, mcause
    bltz   t1, handle_interrupt
    j      handle_exception

handle_interrupt:
    # ...
    j      trap_exit

handle_exception:
    # Advance mepc past the faulting instruction
    csrr   t1, mepc
    addi   t1, t1, 4
    csrw   mepc, t1
    # ...

trap_exit:
    # Restore registers
    lw     ra,  0(t0)
    lw     sp,  4(t0)
    # ...
    csrrw  t0, mscratch, t0   # restore t0
    mret
```

## Why mstatus.MIE Is Cleared Automatically

If interrupts were not disabled on trap entry, a second interrupt arriving before the handler saved any state would overwrite `mepc`, corrupting the return address with no backup. The hardware disables interrupts as an atomic part of trap entry to give the handler time to save its state safely.

> **Interview answer:** On a RISC-V trap the hardware atomically saves the return PC to `mepc`, writes `mcause` and `mtval`, saves privilege and interrupt-enable state into `mstatus`, raises privilege to M-mode, and jumps to `mtvec`. General-purpose registers are not saved — that is the handler's job.

## Common Pitfalls

- Using `t0` before saving it — on entry `t0` has the caller's value. Use `csrrw t0, mscratch, t0` first.
- Assuming `mtval` is always a valid address — it is only meaningful for specific causes.
- Returning from an exception handler without advancing `mepc` causes the same exception to re-trigger immediately.
