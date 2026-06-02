# Quiz: RISC-V Privilege Modes

Test your understanding of RISC-V privilege levels, trap handling, and the Supervisor Binary Interface.

---

**Q1. Which privilege level does a RISC-V processor always start in after a hardware reset?**

- [ ] U-Mode (User Mode)
- [ ] S-Mode (Supervisor Mode)
- [x] M-Mode (Machine Mode)
- [ ] H-Mode (Hypervisor Mode)

The processor always resets into Machine Mode and begins executing at the reset vector address. No lower-privilege software exists yet to run in S-Mode or U-Mode.

---

**Q2. A Linux user process calls `write()`. Which sequence of privilege-level transitions correctly describes what happens?**

- [ ] U-Mode → M-Mode → U-Mode
- [x] U-Mode → S-Mode → M-Mode → S-Mode → U-Mode
- [ ] U-Mode → S-Mode → U-Mode
- [ ] U-Mode → M-Mode → S-Mode → U-Mode

The `ecall` from U-Mode enters the Linux kernel in S-Mode; the kernel may then issue an SBI `ecall` to OpenSBI in M-Mode for hardware access; M-Mode returns via `mret` to S-Mode, which returns via `sret` to U-Mode.

---

**Q3. What value is stored in `scause` when a U-Mode program executes `ecall`?**

- [ ] 3
- [ ] 5
- [ ] 11
- [x] 8

Cause code 8 means "Environment call from U-Mode." Cause 9 is from S-Mode, cause 11 is from M-Mode, and cause 3 is a Breakpoint (from `ebreak`).

---

**Q4. After handling a system call (triggered by `ecall` from U-Mode), the S-Mode handler must do which of the following before issuing `sret`?**

- [ ] Write 0 to `sepc`
- [ ] Set `sstatus.SPP` to 1 (S-Mode) so execution returns to the kernel
- [x] Add 4 to `sepc` so execution resumes at the instruction after `ecall`
- [ ] Clear `satp` to disable virtual memory

`sepc` is set to the `ecall` instruction itself (not the next one). Failing to add 4 causes the CPU to re-execute `ecall` in an infinite trap loop.

---

**Q5. Which CSR does the OS kernel write to enable Sv39 virtual memory and specify the root page-table physical page number?**

- [ ] `mstatus`
- [ ] `pmpaddr0`
- [x] `satp`
- [ ] `mtvec`

`satp` (Supervisor Address Translation and Protection) holds the paging mode, an ASID, and the physical page number of the root page table. Writing it from S-Mode activates address translation.

---

**Q6. What is the purpose of the `medeleg` CSR?**

- [ ] It stores the address of the M-Mode trap handler
- [ ] It enables physical memory protection regions
- [x] It delegates specific exception causes to be handled directly by S-Mode
- [ ] It holds the physical address of the device tree blob

`medeleg` is written by M-Mode firmware to specify which synchronous exception causes (identified by bit position matching the cause code) should bypass M-Mode and be delivered directly to S-Mode's `stvec` handler.
