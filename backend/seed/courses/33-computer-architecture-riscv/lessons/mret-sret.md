# Returning from Traps: MRET and SRET

`mret` and `sret` are the instructions that close the trap loop and restore software to a lower privilege level. They are the mirror image of trap entry: where a trap elevates privilege and saves state, `mret`/`sret` restore state and descend.

## Why Dedicated Return Instructions?

Returning from a trap is not a simple function return. The CPU must simultaneously:

1. Restore the previous privilege level.
2. Restore the previous interrupt-enable state.
3. Jump to the saved exception program counter.

All three must happen atomically. A regular `jalr` or `ret` cannot do this — it only changes the PC. Using a plain return would leave the CPU in the wrong privilege level or with the wrong interrupt state. `mret` and `sret` perform all three steps in one indivisible operation.

## MRET — Machine-Mode Return

`mret` is executed in M-Mode to return from a machine-mode trap. It is encoded as:

```asm
mret   # encoding: 0x30200073
```

### MRET Operation (step by step)

```
Before mret:
  mstatus.MPP  = privilege level before trap  (00=U, 01=S, 11=M)
  mstatus.MPIE = interrupt-enable before trap
  mstatus.MIE  = 0 (disabled during trap)
  mepc         = return address

mret executes:
  1. privilege_level  ← mstatus.MPP
  2. mstatus.MIE      ← mstatus.MPIE    (re-enable interrupts)
  3. mstatus.MPIE     ← 1               (reset for next trap)
  4. mstatus.MPP      ← U-Mode (00)     (security: reset to minimum)
  5. PC               ← mepc
```

Step 4 is a security measure: if the next trap happens before `mstatus.MPP` is updated, it defaults to the least-privileged mode rather than retaining elevated authority.

## SRET — Supervisor-Mode Return

`sret` mirrors `mret` but operates on S-Mode CSRs. It is only available when the processor is in S-Mode or M-Mode.

```asm
sret   # encoding: 0x10200073
```

### SRET Operation

```
Before sret:
  sstatus.SPP  = privilege level before S-Mode trap (1=S, 0=U)
  sstatus.SPIE = interrupt-enable before trap
  sstatus.SIE  = 0 (disabled during trap)
  sepc         = return address

sret executes:
  1. privilege_level  ← sstatus.SPP
  2. sstatus.SIE      ← sstatus.SPIE
  3. sstatus.SPIE     ← 1
  4. sstatus.SPP      ← U-Mode (0)
  5. PC               ← sepc
```

## Comparison Table

| Property | `mret` | `sret` |
|---|---|---|
| Available from | M-Mode | S-Mode, M-Mode |
| Restores privilege from | `mstatus.MPP` | `sstatus.SPP` |
| Restores interrupt enable from | `mstatus.MPIE` | `sstatus.SPIE` |
| Jumps to | `mepc` | `sepc` |
| Resets privilege field to | U-Mode | U-Mode |

## Worked Example: Kernel Returning to a User Process

```asm
# Kernel syscall handler is finishing (in S-Mode)
# a0 already contains the return value

# 1. Advance sepc past the ecall instruction
csrr  t0, sepc
addi  t0, t0, 4
csrw  sepc, t0

# 2. Ensure SPP=0 (return to U-Mode) in sstatus
csrr  t1, sstatus
li    t2, ~(1 << 8)     # mask to clear SPP bit
and   t1, t1, t2
csrw  sstatus, t1

# 3. Restore user general-purpose registers from trapframe
# ... (ld ra, 0(sp); ld gp, 16(sp); etc.)

# 4. Return to U-Mode
sret
```

## Worked Example: Firmware Launching the Kernel

```asm
# M-Mode firmware (OpenSBI) transferring control to Linux kernel

# Kernel expects to start in S-Mode
la    t0, linux_kernel_entry
csrw  mepc, t0

# Set MPP=01 (S-Mode) so mret drops to S-Mode
csrr  t1, mstatus
li    t2, 0x1800           # bits [12:11]
and   t1, t1, ~t2          # clear MPP
li    t2, 0x0800           # MPP=01 (Supervisor)
or    t1, t1, t2
csrw  mstatus, t1

# Pass device tree pointer in a1 (Linux boot convention)
mv    a1, s0               # s0 = DTB physical address

mret                        # jumps to linux_kernel_entry in S-Mode
```

## Common Pitfalls

**Pitfall 1: Wrong MPP/SPP value.** If `MPP` is set to M-Mode (11) before `mret`, the CPU stays in M-Mode. Always verify the privilege bits before executing the return instruction.

**Pitfall 2: Forgetting to advance sepc for ecall.** `mret`/`sret` jump to whatever is in `mepc`/`sepc`. If you handle an `ecall` without adding 4, the CPU will re-execute the `ecall` instruction and trap again immediately — an infinite loop.

**Pitfall 3: Executing sret with TSR set.** If `mstatus.TSR` (Trap SRET) is set by M-Mode, executing `sret` from S-Mode raises an illegal-instruction exception in M-Mode. This bit exists to let hypervisors intercept `sret`.

> **Interview answer:** MRET and SRET atomically restore the previous privilege level (from MPP/SPP), re-enable interrupts (from MPIE/SPIE), and jump to the saved return address (mepc/sepc); atomicity is essential because no intermediate state with wrong privilege or interrupt enable should be observable.
