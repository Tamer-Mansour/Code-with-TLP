# Quiz: Computer Architecture Foundations for OS

Test your understanding of the hardware model that operating systems are built on.

---

**Q1. Which register on x86-64 holds the address of the *next* instruction to be fetched?**

- [ ] RSP
- [ ] RAX
- [x] RIP
- [ ] RFLAGS

*RIP (Instruction Pointer) is incremented during the fetch stage to point to the next instruction. RSP is the stack pointer, RAX is a general-purpose register, and RFLAGS holds status flags.*

---

**Q2. A process's working set is larger than available physical RAM. What phenomenon occurs?**

- [ ] Segmentation fault
- [ ] Cache coherence violation
- [x] Thrashing
- [ ] Stack overflow

*Thrashing occurs when the OS spends more time swapping pages between RAM and disk than executing process instructions, because the working set does not fit in memory. This causes severe performance degradation.*

---

**Q3. On a little-endian system, the 32-bit value `0x12345678` is stored starting at address `0x2000`. What byte value is at address `0x2000`?**

- [ ] `0x12`
- [ ] `0x34`
- [ ] `0x56`
- [x] `0x78`

*Little-endian stores the least significant byte at the lowest address. The least significant byte of `0x12345678` is `0x78`, so it appears at address `0x2000`.*

---

**Q4. What is the primary reason CPU caches use SRAM rather than DRAM?**

- [ ] SRAM is cheaper to manufacture
- [ ] SRAM can store more data per chip area
- [x] SRAM is significantly faster and requires no refresh cycles
- [ ] SRAM consumes less power than DRAM

*SRAM stores bits using 6-transistor flip-flop cells that retain state without periodic refresh. This gives access latencies of 1–4 ns versus DRAM's 60–100 ns. SRAM is more expensive and less dense than DRAM — the trade-off accepted for cache-level performance.*

---

**Q5. In the Von Neumann architecture, what is the "Von Neumann bottleneck"?**

- [ ] The CPU cannot perform floating-point arithmetic
- [x] Instructions and data share the same bus, preventing simultaneous instruction fetch and data access
- [ ] All memory accesses must go through the L1 cache
- [ ] The ALU can only process one operand at a time

*The Von Neumann bottleneck arises because a single shared bus carries both instructions and data, so the CPU cannot fetch the next instruction while simultaneously reading or writing data memory. Modified Harvard designs solve this with a split L1 cache.*

---

**Q6. A user process wants to write data to a file. Which mechanism allows it to request this service from the OS?**

- [ ] A direct call to a kernel function pointer
- [ ] Modifying the page table directly
- [ ] Issuing a privileged HLT instruction
- [x] Executing a system call (e.g., the `syscall` instruction on x86-64)

*System calls are the controlled interface between user-mode (ring 3) code and the kernel (ring 0). The `syscall` instruction traps into the kernel, which validates the request, performs the privileged operation, and returns to user mode. Direct kernel function calls, page-table modifications, and privileged instructions are not accessible from ring 3.*
