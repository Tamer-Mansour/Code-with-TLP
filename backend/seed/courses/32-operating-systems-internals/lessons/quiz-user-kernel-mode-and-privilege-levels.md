# Quiz: User Mode, Kernel Mode, and Privilege Levels

Test your understanding of the concepts from this module. Choose the single best answer for each question.

---

**Q1. On a standard Linux x86-64 system, which CPU ring does a user application run in?**

- [ ] Ring 0
- [ ] Ring 1
- [ ] Ring 2
- [x] Ring 3

_Ring 3 is the least-privileged x86 protection level. Linux uses only Ring 0 (kernel) and Ring 3 (user processes); rings 1 and 2 are unused._

---

**Q2. A user-space program executes the `HLT` instruction directly. What happens?**

- [ ] The CPU halts until the next timer interrupt, then resumes the program
- [ ] The OS scheduler is invoked immediately
- [x] The CPU raises a General Protection Fault and the kernel terminates the process
- [ ] Nothing — `HLT` is silently ignored in user mode

_`HLT` is a privileged instruction. Executing it from Ring 3 raises #GP before the instruction takes effect. The kernel's fault handler typically delivers SIGSEGV._

---

**Q3. What is the key difference between a mode switch and a context switch?**

- [ ] A mode switch saves the full register file; a context switch saves only the program counter
- [x] A mode switch changes CPU privilege level without changing the running thread; a context switch replaces the running thread entirely
- [ ] They are the same event described from different perspectives
- [ ] A context switch only occurs between processes, never between threads

_A mode switch (user→kernel→user) keeps the same thread running at a different privilege level. A context switch replaces the thread, saving and restoring full CPU state._

---

**Q4. After Meltdown mitigations (KPTI) were applied, why did syscall-heavy workloads slow down?**

- [ ] The kernel began validating all syscall arguments in software
- [ ] The number of available syscalls was reduced
- [x] Every syscall entry/exit now requires switching the page table (CR3), which can flush the TLB
- [ ] The CPU frequency was throttled to prevent side-channel attacks

_KPTI removed the kernel mapping from user-mode page tables. Entering the kernel requires switching CR3 to the kernel's page table (and back on exit), invalidating TLB entries on CPUs without PCID._

---

**Q5. Which page table entry flag prevents Ring-3 code from accessing a kernel page, even if the virtual address is known?**

- [ ] The Read/Write (R/W) bit set to 0
- [ ] The No-Execute (NX) bit
- [x] The User/Supervisor (U/S) bit set to 0 (supervisor-only)
- [ ] The Present (P) bit set to 0

_The U/S bit in each PTE determines whether user-mode (Ring 3) access is allowed. Kernel pages have U/S=0; the MMU raises a page fault on any Ring-3 access regardless of the virtual address value._

---

**Q6. What does the vDSO mechanism achieve?**

- [ ] It lets the kernel execute user-supplied code in Ring 0 safely
- [ ] It provides a virtual file system for device access without syscalls
- [x] It maps kernel-provided code into user space so certain calls (e.g., `clock_gettime`) require no privilege switch
- [ ] It replaces the IDT with a faster dispatch table for interrupts

_The vDSO exports functions that read kernel-maintained data from a user-accessible page. The call completes entirely in Ring 3, eliminating the SYSCALL instruction and its associated mode-switch overhead._
