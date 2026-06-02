# Quiz: RISC-V Boot Process and Firmware

Test your understanding of the RISC-V boot sequence, firmware layers, and hardware initialization concepts covered in this module.

---

**Q1. When a RISC-V hart exits reset, which register holds the address of the first instruction to execute?**

- [ ] `mtvec` — the machine trap vector
- [ ] `mepc` — the machine exception program counter
- [x] `pc` — the program counter, loaded with the reset vector address
- [ ] `ra` — the return address register

The program counter (PC) is set to the implementation-defined reset vector address when the reset signal is deasserted. `mepc` and `mtvec` are only relevant after a trap occurs. `ra` is undefined after reset.

---

**Q2. What is the correct order of the classic RISC-V boot stages?**

- [ ] FSBL → ZSBL → OpenSBI → Kernel
- [ ] OpenSBI → ZSBL → FSBL → Kernel
- [x] ZSBL → FSBL → OpenSBI → Kernel
- [ ] ZSBL → OpenSBI → FSBL → Kernel

ZSBL (Zero Stage Boot Loader) runs from on-chip mask ROM, then FSBL (First Stage) initializes DRAM, then OpenSBI provides M-mode SBI firmware, and finally the kernel runs in S-mode.

---

**Q3. What values must be in registers `a0` and `a1` when the bootloader jumps to the Linux RISC-V kernel entry point?**

- [ ] `a0` = FDT address, `a1` = hart ID
- [x] `a0` = hart ID, `a1` = physical address of the Device Tree Blob (DTB)
- [ ] `a0` = kernel load address, `a1` = hart ID
- [ ] `a0` = hart ID, `a1` = SBI version number

The RISC-V Linux boot protocol specifies `a0` = hart ID of the booting hart and `a1` = the physical address of the Flattened Device Tree. The kernel reads both immediately at entry.

---

**Q4. Which CSR must be written to enable Sv39 paging on a 64-bit RISC-V hart?**

- [ ] `mstatus` with the MPRV bit set
- [ ] `medeleg` with paging delegation enabled
- [x] `satp` with MODE=8 and the PPN of the root page table
- [ ] `pmpcfg0` with the read and execute bits set

The `satp` (Supervisor Address Translation and Protection) CSR controls virtual memory mode. Writing MODE=8 (Sv39) and the physical page number of the L2 page table enables address translation. An `sfence.vma` must follow to flush the TLB.

---

**Q5. In a multi-hart RISC-V system, what should secondary harts do immediately after reset to avoid corrupting shared initialization?**

- [ ] Configure their own `mtvec` and begin executing the FSBL
- [ ] Spin in a busy loop reading `mhartid` until released
- [x] Park themselves in a `wfi` (Wait For Interrupt) loop after confirming they are not hart 0
- [ ] Jump directly to the kernel entry point and wait on a spinlock

Secondary harts should enter a `wfi` loop as soon as they detect `mhartid != 0`. This saves power and avoids bus contention. The OS later wakes them via the SBI Hart State Management (HSM) extension.

---

**Q6. Why must the BSS section be cleared by boot code before calling any C function?**

- [ ] The linker fills BSS with `0xFF` and the boot code must overwrite it
- [ ] BSS is stored in flash and must be copied to DRAM before C code can access it
- [ ] C functions cannot access BSS memory that has not been flushed from the cache
- [x] The C standard requires zero-initialized global variables, but BSS contains no data in the binary — boot code must zero it at runtime

BSS (Block Started by Symbol) is a no-load section — the binary does not store zeros for it to save space. Boot code is responsible for zeroing the BSS region so that C's guarantee of zero-initialization for uninitialized globals and statics is upheld.
