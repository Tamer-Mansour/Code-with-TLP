# Quiz: RISC-V Trap and Interrupt Handling

**Q1. When a trap is taken in M-mode, which CSR holds the address the processor will return to after mret?**

- [ ] mtvec
- [x] mepc
- [ ] mscratch
- [ ] mcause

The `mepc` (Machine Exception Program Counter) is loaded with the address of the trapping instruction (for exceptions) or the next instruction (for interrupts). `mret` reads `mepc` to resume execution.

---

**Q2. A 64-bit mcause value has its most significant bit set to 1. What does this indicate?**

- [ ] An unrecoverable machine error
- [ ] An exception caused by the current instruction
- [x] An interrupt (asynchronous event)
- [ ] A delegated trap

The MSB of `mcause` is the interrupt bit. When it is 1 the trap was caused by an asynchronous interrupt; when it is 0 the trap was a synchronous exception.

---

**Q3. In Vectored mode (mtvec.MODE = 1), where does the processor jump when an exception occurs?**

- [x] mtvec.BASE (same as Direct mode)
- [ ] mtvec.BASE + 4 × exception_code
- [ ] mtvec.BASE + 4 × 0
- [ ] The address stored in mepc

In Vectored mode only **interrupts** are vectored to BASE + 4 × code. Exceptions **always** jump to BASE, identical to Direct mode behavior.

---

**Q4. What must a trap handler do to clear a machine timer interrupt?**

- [ ] Write 0 to mip.MTIP
- [ ] Write 0 to mie.MTIE
- [x] Write a new future value to mtimecmp
- [ ] Execute mret with mstatus.MIE cleared

`mip.MTIP` is a read-only hardware bit set when `mtime >= mtimecmp`. The only way to clear it is to write a new `mtimecmp` value greater than the current `mtime`. `mip.MTIP` then clears automatically.

---

**Q5. An OS kernel runs in S-mode and needs to handle page faults without going through M-mode. Which CSR must M-mode firmware configure to achieve this?**

- [ ] mstatus.SIE
- [ ] stvec
- [x] medeleg
- [ ] mideleg

`medeleg` (Machine Exception Delegation register) delegates specific exception codes to S-mode. Setting the bit corresponding to the page fault code causes those exceptions to use `sepc`, `scause`, and `stvec` instead of their M-mode counterparts.

---

**Q6. What is the correct sequence to claim and service an external interrupt arriving through the PLIC?**

- [ ] Read mip, service device, clear mip.MEIP
- [ ] Write to PLIC enable register, service device, write to PLIC priority register
- [ ] Read mcause, service device, write 0 to PLIC pending register
- [x] Read PLIC claim register (gets IRQ ID), service device, write IRQ ID to PLIC complete register

The PLIC uses a claim/complete protocol. Reading the claim register atomically acknowledges the interrupt and returns the source ID. After servicing, writing that ID to the complete register (same address) unmasks the source for future interrupts.
