# Trap Delegation: medeleg and mideleg

By default, all traps are taken in M-mode regardless of where they originate. A page fault in a U-mode application would cause a round-trip through M-mode firmware before reaching the OS kernel in S-mode. Trap delegation eliminates this overhead by routing selected traps directly to S-mode.

## The Two Delegation Registers

| CSR | Delegates | Controls |
|---|---|---|
| `medeleg` | Exceptions | Which exception codes go to S-mode |
| `mideleg` | Interrupts | Which interrupt codes go to S-mode |

Both registers have the same bit layout as `mcause`: bit N corresponds to exception/interrupt code N. Setting bit N in `medeleg` or `mideleg` means "when this trap occurs, handle it in S-mode instead of M-mode."

```
medeleg bit 13 = 1  →  Load page fault (code 13) handled in S-mode
mideleg bit  5 = 1  →  Supervisor timer interrupt (code 5) handled in S-mode
```

## How Delegation Changes the Trap Sequence

When a trap is delegated to S-mode the hardware uses the **S-mode CSR set** instead of the M-mode set:

| M-mode CSR | S-mode equivalent |
|---|---|
| `mepc` | `sepc` |
| `mcause` | `scause` |
| `mtval` | `stval` |
| `mtvec` | `stvec` |
| `mstatus.MPP/MPIE/MIE` | `mstatus.SPP/SPIE/SIE` |

The M-mode CSRs are **not touched** for a delegated trap. Return from a delegated trap uses `sret`, not `mret`.

## Setting Up Delegation

```asm
# Delegate all page faults and ecalls from U-mode to S-mode
li    t0, (1 << 12) | (1 << 13) | (1 << 15) | (1 << 8)
      # bit 12: instruction page fault
      # bit 13: load page fault
      # bit 15: store page fault
      # bit 8:  environment call from U-mode
csrw  medeleg, t0

# Delegate supervisor timer and external interrupts to S-mode
li    t0, (1 << 5) | (1 << 9)
      # bit 5: supervisor timer interrupt
      # bit 9: supervisor external interrupt
csrw  mideleg, t0
```

In C using a helper macro:

```c
// Set delegation (typically done in M-mode firmware before jumping to OS)
write_csr(medeleg, MEDELEG_LOAD_PAGE_FAULT   |
                   MEDELEG_STORE_PAGE_FAULT  |
                   MEDELEG_INSTR_PAGE_FAULT  |
                   MEDELEG_ECALL_U);

write_csr(mideleg, MIDELEG_STIMER | MIDELEG_SEXT);
```

## Delegation Rules and Restrictions

**Rule 1: Delegation cannot go to a lower privilege level.**  
A trap in M-mode is never delegated — M-mode always handles its own traps. Delegation only affects traps that originate in S-mode or U-mode.

**Rule 2: Traps taken in S-mode cannot be delegated further to U-mode.**  
RISC-V has no U-mode trap CSRs in the base spec (the N extension added them but it is rare).

**Rule 3: If a trap is delegated but S-mode is not implemented, the trap is still taken in M-mode.**

**Rule 4: `medeleg` and `mideleg` can only be written from M-mode.**  
S-mode cannot modify delegation — the OS cannot promote itself to handle traps it was not granted.

## The Linux/UNIX Boot Sequence Example

A typical RISC-V boot flow using delegation:

```
1. Firmware (M-mode, e.g., OpenSBI) starts.
2. Firmware sets medeleg and mideleg to route OS traps to S-mode.
3. Firmware sets up PMP, then executes mret to jump into S-mode OS.
4. OS (S-mode) sets stvec, enables interrupts via sstatus.SIE.
5. OS enters U-mode to run user applications.
6. User ecall → delegated to S-mode → OS syscall handler.
7. Page fault → delegated to S-mode → OS page-fault handler.
8. Timer interrupt → delegated to S-mode → OS scheduler.
```

## What Happens to M-mode During a Delegated Trap

When a trap is delegated, M-mode CSRs (`mepc`, `mcause`, `mtval`) are **not updated**. The hardware writes only the S-mode CSRs. `mstatus.MPP` is also untouched; only `mstatus.SPP` is updated.

This means firmware can safely sit in M-mode and handle its own traps (e.g., machine timer for watchdog) independently of the OS.

## Checking Delegation at Runtime

```asm
csrr  t0, medeleg
li    t1, (1 << 13)   # load page fault bit
and   t0, t0, t1
bnez  t0, lpf_delegated
# else: M-mode handles load page faults
```

> **Interview answer:** `medeleg` and `mideleg` are M-mode CSRs where each bit corresponds to an exception or interrupt code. Setting a bit causes that trap to be taken in S-mode (using `sepc`, `scause`, `stval`, `stvec`) instead of M-mode. Delegation reduces round-trip latency for OS-level traps like page faults and system calls.

## Common Pitfalls

- Setting `mideleg` bit 7 (machine timer interrupt) — machine interrupts cannot be delegated; the hardware ignores writes to those bits.
- Forgetting to set `stvec` before enabling delegation — a delegated trap with an invalid `stvec` jumps to an undefined address.
- Delegating M-mode ecalls (code 11) — this is illegal since M-mode cannot delegate its own traps downward.
