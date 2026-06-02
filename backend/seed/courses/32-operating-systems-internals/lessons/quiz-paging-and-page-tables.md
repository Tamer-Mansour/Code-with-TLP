# Quiz: Paging and Page Tables

**Q1. A system has a 32-bit virtual address space and a page size of 8 KB. How many bits are used for the page offset?**
- [ ] 10
- [ ] 12
- [x] 13
- [ ] 16

8 KB = 2^13 bytes, so the offset field requires 13 bits. The VPN uses the remaining 19 bits.

---

**Q2. Which hardware register on x86 holds the physical base address of the current process's page table?**
- [ ] EIP
- [ ] ESP
- [x] CR3
- [ ] CR0

CR3 stores the physical address of the top-level page table (PML4 on x86-64, Page Directory on x86-32). It is updated on every context switch to switch address spaces.

---

**Q3. What happens when the MMU encounters a page table entry with the Present bit set to 0?**
- [ ] The MMU returns all zeros for that address
- [ ] The OS immediately terminates the process
- [x] A page fault exception is raised and the OS fault handler runs
- [ ] The TLB is flushed and the walk is retried

A Present=0 PTE causes a page fault (interrupt 14 on x86). The OS handler decides whether to load the page from swap, allocate a zero page, or deliver SIGSEGV.

---

**Q4. Why do multilevel page tables use less memory than a flat single-level page table for a typical process?**
- [x] They only allocate inner and leaf tables for virtual address regions the process actually uses
- [ ] Each entry is smaller in a multilevel table
- [ ] Multilevel tables compress entries using run-length encoding
- [ ] The physical frame number is shared across all levels

With a flat table every entry exists even for unmapped regions. Multilevel tables use NULL pointers at inner levels to skip entire regions, so only used regions consume memory.

---

**Q5. The Dirty bit in a page table entry is set by:**
- [ ] The operating system when it maps a page
- [ ] The programmer explicitly via a system call
- [ ] The TLB miss handler in software
- [x] The MMU hardware on any write to the page

The MMU automatically sets the Dirty bit on any write operation. The OS reads (and clears) it to determine whether an evicted page must be written back to disk.

---

**Q6. Virtual address 0x00205010 is in a system with 4 KB pages. What is the virtual page number?**
- [ ] 0x00205
- [x] 0x205
- [ ] 0x010
- [ ] 0x2050

With 4 KB = 2^12 bytes per page, the VPN = 0x00205010 >> 12 = 0x205 = 517. The offset = 0x010.

---
