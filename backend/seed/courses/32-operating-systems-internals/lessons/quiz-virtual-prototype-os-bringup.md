# Quiz: Virtual Prototype and OS Bring-Up Capstone

**Q1. What is the primary advantage of a loosely-timed TLM model over a cycle-accurate RTL simulation?**

- [ ] It produces bit-exact results for every clock cycle.
- [x] It runs orders of magnitude faster, enabling full OS boot in seconds.
- [ ] It requires no SystemC license.
- [ ] It eliminates all timing bugs before tape-out.

*Loosely-timed TLM sacrifices cycle-exact fidelity for speed (100 MHz+ vs ~1 KHz RTL), making it practical to boot a full OS and run application tests.*

---

**Q2. In a RISC-V RV32I instruction, which bits carry the opcode field used to determine the instruction format?**

- [ ] Bits [31:25]
- [ ] Bits [19:15]
- [x] Bits [6:0]
- [ ] Bits [14:12]

*The 7-bit opcode in bits [6:0] determines the instruction format (R, I, S, B, U, or J); funct3 (bits [14:12]) and funct7 (bits [31:25]) further distinguish instructions within a format.*

---

**Q3. In RISC-V Sv32 two-level page table translation, what does a PTE with V=0 indicate?**

- [ ] The page is read-only.
- [ ] The physical page number is zero.
- [x] The page table entry is invalid; the MMU must raise a page fault.
- [ ] The page is in the page cache and must be fetched from disk.

*The Valid bit (V=0) means no mapping exists for this virtual address. The hardware raises a page fault, which the OS handles by either allocating a physical page or terminating the process.*

---

**Q4. During OS bring-up on RISC-V, what are the two values a bootloader passes to the kernel entry point by convention?**

- [ ] Stack pointer and program counter
- [ ] Physical DRAM base and kernel size
- [x] Hart ID in a0 and Device Tree Blob physical address in a1
- [ ] Page table root in satp and interrupt vector in mtvec

*The RISC-V boot convention requires a0 = booting hart ID and a1 = DTB physical address. The kernel uses these to configure SMP and parse the hardware description.*

---

**Q5. Why must a JIT-based ISS (such as QEMU) invalidate Translation Blocks when self-modifying code is detected?**

- [ ] JIT code runs slower than interpreted code after the first execution.
- [ ] The host CPU cache may contain stale data from a previous simulation run.
- [x] The compiled host code for that region is now stale and would execute incorrect instructions.
- [ ] Self-modifying code is illegal in RISC-V and must raise an illegal instruction exception.

*A JIT ISS compiles target instructions to host code. If the target program writes to that same address range, the cached host code no longer reflects the current target instructions. The TB must be flushed and recompiled on next execution.*

---

**Q6. When modeling an interrupt controller in a virtual prototype, what is the consequence of omitting the End-of-Interrupt (EOI / Complete) acknowledgment in the model?**

- [ ] The interrupt is silently dropped and never delivered to the CPU.
- [ ] The CPU privilege level remains in machine mode indefinitely.
- [ ] The PLIC resets all pending bits to zero.
- [x] The same interrupt fires repeatedly and the OS interrupt handler loops forever without making progress.

*The PLIC (and most interrupt controllers) suppress re-delivery of a source until the software writes the EOI. Without modeling this, the pending bit is never cleared after claim, so the OS re-enters the handler in an infinite loop.*
