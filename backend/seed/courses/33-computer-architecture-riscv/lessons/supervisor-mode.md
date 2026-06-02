# Supervisor Mode (S-Mode)

Supervisor Mode is the privilege level designed for operating system kernels. It sits between the all-powerful M-Mode firmware and the restricted U-Mode user processes. On any RISC-V system running Linux, the kernel executes entirely in S-Mode.

## The Role of S-Mode

S-Mode exists to give the kernel:

- **Virtual memory control** — S-Mode can load the page-table base register (`satp`) and thus control the address space of every user process.
- **Trap handling for user processes** — Once M-Mode delegates traps, system calls from U-Mode land directly in the kernel's S-Mode handler.
- **Controlled isolation from U-Mode** — S-Mode code can access any virtual address it has mapped; U-Mode code cannot access S-Mode-only pages.

S-Mode cannot, however, read or write M-Mode CSRs, configure PMP, or perform any operation reserved for M-Mode. It relies on the Supervisor Binary Interface (SBI) to request M-Mode services.

## Key S-Mode CSRs

| CSR | Purpose |
|---|---|
| `sstatus` | Subset of `mstatus` visible to S-Mode (interrupt enable, SPP, etc.) |
| `stvec` | S-Mode trap vector base address |
| `sepc` | Return PC saved when a trap hits S-Mode |
| `scause` | Cause of the most recent S-Mode trap |
| `stval` | Trap-specific value (faulting VA for page faults) |
| `satp` | Page-table base register; enables/controls virtual memory |
| `sie` / `sip` | S-Mode interrupt enable / pending |

Note: `sstatus` is not a separate physical register — it is a restricted view of `mstatus`. Some bits in `mstatus` are simply not visible when accessed via `sstatus`.

## Virtual Memory: The satp Register

```asm
# Enable Sv39 paging with PPN of root page table in t0
# Mode=8 (Sv39) lives in bits [63:60]; ASID in [59:44]; PPN in [43:0]
li    t1, (8UL << 60)
or    t0, t0, t1           # root_ppn already in t0
csrw  satp, t0
sfence.vma                 # flush TLB after changing satp
```

Once `satp` is written with a valid mode and root page-table physical address, all subsequent U-Mode (and optionally S-Mode) address references go through the page-table walker. This is the mechanism behind process isolation.

## Handling System Calls in S-Mode

When a U-Mode program executes `ecall`, control transfers to the address in `stvec`. A minimal syscall dispatcher:

```c
// C representation of what the assembly trap handler does
void s_mode_trap_handler(struct trapframe *tf) {
    long cause = csr_read(scause);

    if (cause == CAUSE_USER_ECALL) {
        // tf->a7 holds the syscall number
        tf->a0 = do_syscall(tf->a7, tf->a0, tf->a1, tf->a2);
        tf->epc += 4;   // advance past the ecall instruction
    } else if (cause & CAUSE_INTERRUPT) {
        handle_interrupt(cause);
    } else {
        handle_exception(cause, csr_read(stval));
    }
}
```

## S-Mode Interrupt Handling

S-Mode can handle the three standard interrupt types when delegated by M-Mode:

| Interrupt | Bit in sie/sip |
|---|---|
| Software interrupt | 1 |
| Timer interrupt | 5 |
| External interrupt | 9 |

The kernel arms the timer via an SBI call (`sbi_set_timer`), which M-Mode then configures in `mtimecmp`. When the timer fires, the interrupt — if delegated — arrives in S-Mode's handler.

## Common Pitfall

A frequent mistake is forgetting the `sfence.vma` instruction after modifying page tables or writing `satp`. Without it, the TLB may hold stale translations, causing page faults or — worse — silent security violations where old mappings remain accessible. Always issue `sfence.vma` after any page-table change.

## Worked Example: Switching to U-Mode from S-Mode

```asm
# Kernel is about to run a user program
la    t0, user_entry
csrw  sepc, t0

# Set SPP=0 (return to U-Mode) in sstatus
csrr  t1, sstatus
li    t2, ~(1 << 8)        # clear SPP bit
and   t1, t1, t2
csrw  sstatus, t1

# Restore user registers from trapframe ...
sret                        # jumps to user_entry in U-Mode
```

> **Interview answer:** Supervisor Mode is the RISC-V privilege level for OS kernels; it controls virtual memory via satp, handles system calls delegated from M-Mode, and is fully isolated from both M-Mode internals and U-Mode user processes.
