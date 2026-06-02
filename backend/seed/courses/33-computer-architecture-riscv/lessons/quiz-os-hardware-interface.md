# Quiz: OS-Hardware Interface and Scheduling

**Q1. On RISC-V, what is stored in the `sepc` CSR when an `ecall` instruction is executed from user mode?**

- [ ] The address of the `stvec` trap handler
- [x] The address of the `ecall` instruction itself
- [ ] The address of the instruction after `ecall`
- [ ] The value of `scause` at the time of the trap

The hardware saves the PC of the faulting/trapping instruction into `sepc`. For `ecall`, that is the address of the `ecall` itself — the kernel must increment `sepc` by 4 before returning so the user program does not re-execute `ecall` on `sret`.

---

**Q2. Which of the following is NOT saved automatically by the RISC-V hardware on a trap?**

- [ ] The current privilege mode (stored in `sstatus.SPP`)
- [ ] The address of the trapping instruction (stored in `sepc`)
- [x] The values of all 32 integer registers
- [ ] The cause of the trap (stored in `scause`)

RISC-V hardware saves only the PC, privilege mode, and interrupt-enable state on a trap. All 32 integer registers must be saved by the trap handler in software (typically to a per-process trapframe).

---

**Q3. In the xv6-riscv `swtch()` function, why does it only save and restore callee-saved registers (`ra`, `sp`, `s0`–`s11`) instead of all 32 registers?**

- [ ] The other registers are saved automatically by the hardware
- [ ] Caller-saved registers are not needed for correct execution
- [x] `swtch()` is a C function call, so the C ABI guarantees caller-saved registers are already saved by the caller
- [ ] RISC-V has only 14 registers that matter for context switching

Because `swtch()` is called like a normal C function, the compiler-generated calling code has already saved any caller-saved registers it needs. Only callee-saved registers (`ra`, `sp`, `s0`–`s11`) must be explicitly preserved by `swtch()` itself.

---

**Q4. A RISC-V system uses `mtime` and `mtimecmp` for timer interrupts. Which statement is correct for a dual-core (2-hart) system?**

- [ ] Both harts share a single `mtimecmp` register
- [x] Each hart has its own `mtimecmp` at `CLINT_MTIMECMP_BASE + 8 * hartid`
- [ ] `mtime` is per-hart but `mtimecmp` is global
- [ ] Timer interrupts are only deliverable to hart 0

The CLINT provides one `mtimecmp` register per hart, offset by 8 bytes per hart ID. `mtime` itself is a single global counter, but each hart's interrupt fires independently based on its own `mtimecmp` value.

---

**Q5. Which CPU scheduling algorithm is optimal for minimizing average waiting time when all burst times are known in advance?**

- [ ] First Come First Served (FCFS)
- [ ] Round Robin with a small quantum
- [x] Shortest Job First (SJF) / Shortest Remaining Time (SRT)
- [ ] Multilevel Feedback Queue (MLFQ)

SJF (non-preemptive) minimizes average waiting time when all burst times are known. Its preemptive variant SRT is optimal even when jobs arrive dynamically. The drawback is that burst times are rarely known in practice, leading to starvation of long jobs.

---

**Q6. On RISC-V, a page table entry for a kernel data page has `U=0` and `W=1`. What happens if user-mode code tries to write to the corresponding virtual address?**

- [ ] The write succeeds if `sstatus.SUM` is set
- [ ] The write succeeds but a dirty-bit fault is raised
- [ ] The write is silently ignored
- [x] The MMU raises a store page-fault exception regardless of `sstatus.SUM`

`sstatus.SUM` allows S-mode (kernel) to access U-mode pages, not the reverse. A U-mode access to a page without the `U` bit always raises a page fault — `SUM` has no effect on U-mode permission checks.
