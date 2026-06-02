# Quiz: Control and Status Registers

Test your understanding of the RISC-V CSR mechanism and the key M-mode registers.

---

**Q1. Which CSR instruction performs a pure read of a CSR with no write side effect?**

- [ ] CSRRW rd, csr, x0
- [x] CSRRS rd, csr, x0
- [ ] CSRRW x0, csr, rs1
- [ ] CSRRWI rd, csr, 0

Using x0 as the source register in CSRRS or CSRRC suppresses the write. CSRRW with x0 source would zero the CSR, and CSRRW with x0 destination skips the read but still writes.

---

**Q2. A trap fires while the processor is in U-mode. What value does the hardware write into mstatus.MPP?**

- [ ] 0b11 (Machine)
- [ ] 0b01 (Supervisor)
- [x] 0b00 (User)
- [ ] 0b10 (Hypervisor)

MPP stores the privilege level that was active before the trap. U-mode is encoded as 0b00. The handler reads MPP to know which mode was interrupted.

---

**Q3. An mcause value of 0x80000007 (decimal 2147483655) on RV32 indicates which trap?**

- [ ] Exception: Store/AMO access fault (code 7)
- [ ] Exception: Breakpoint (code 3)
- [x] Interrupt: Machine timer interrupt (code 7, interrupt bit set)
- [ ] Interrupt: Machine software interrupt (code 3, interrupt bit set)

Bit 31 is 1 (interrupt bit set), so it is an interrupt. The lower 31 bits give code 7, which maps to the machine timer interrupt.

---

**Q4. What happens if software attempts to write to a read-only CSR (bits [11:10] == 0b11)?**

- [ ] The write is silently ignored
- [ ] The CSR is cleared to zero
- [x] An illegal instruction exception is raised
- [ ] A machine software interrupt fires

The RISC-V privileged spec mandates that any attempt to write a read-only CSR raises an illegal instruction exception, regardless of privilege level. Reads of such CSRs succeed normally.

---

**Q5. In mtvec vectored mode (MODE=1), where does an illegal instruction exception (mcause code 2) jump?**

- [ ] BASE + 4*2 = BASE + 8
- [x] BASE (the base address, not offset)
- [ ] BASE + 4*3 = BASE + 12
- [ ] The address stored in mtval

In vectored mode, only **interrupts** are vectored to BASE + 4*N. All exceptions, including illegal instruction, always jump to BASE regardless of the cause code.

---

**Q6. Which statement about mepc is correct?**

- [ ] mepc always points to the instruction after the faulting instruction
- [ ] mepc is read-only and cannot be modified by the trap handler
- [ ] mepc holds the faulting virtual address for load/store faults
- [x] For exceptions, mepc points to the faulting instruction; for interrupts it points to the next instruction to execute

This distinction determines whether the handler must advance mepc (exceptions, if the instruction should be skipped) or leave it unchanged (interrupts, to resume normally). The faulting virtual address for loads/stores is in mtval, not mepc.
