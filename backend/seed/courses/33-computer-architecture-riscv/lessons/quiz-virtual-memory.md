# Quiz: Virtual Memory and the MMU

Test your understanding of virtual memory, paging, the MMU, address translation, the TLB, and page faults.

---

**Q1. A process issues a load from virtual address `0x00005ABC`. The system uses 4 KiB pages (12-bit offset). Which of the following correctly identifies the Virtual Page Number (VPN) and offset?**

- [ ] VPN = `0xABC`, offset = `0x005`
- [x] VPN = `0x5`, offset = `0xABC`
- [ ] VPN = `0x00005`, offset = `0xABC000`
- [ ] VPN = `0x0000`, offset = `0x5ABC`

*Explanation: With a 12-bit offset, bits 11:0 = `0xABC` are the offset, and bits above that (`0x5`) form the VPN.*

---

**Q2. Why does a flat, single-level page table become impractical for 64-bit virtual address spaces?**

- [ ] 64-bit CPUs do not support page tables.
- [ ] The MMU cannot index more than 32-bit VPNs.
- [x] The table would require trillions of entries, consuming terabytes of memory per process.
- [ ] 64-bit PTEs are too large to fit in cache lines.

*Explanation: A flat table needs one entry per virtual page. A 48-bit VA space with 4 KiB pages needs 2^36 entries — at 8 bytes each that is 512 GiB per process, which is obviously infeasible.*

---

**Q3. After a context switch to a new process, the OS writes a new value to the `satp` register. What additional step is mandatory on RISC-V if the new process does NOT have a distinct ASID?**

- [ ] Disable the MMU until the first instruction of the new process executes.
- [ ] Write zero to all PTEs of the old process.
- [x] Execute `sfence.vma` to flush the TLB, preventing stale translations from the previous process.
- [ ] Set the D (dirty) bit on all pages of the new process.

*Explanation: The TLB caches (ASID, VPN) → PFN mappings. Without ASIDs, the same VPN in a new process would incorrectly hit on an old entry. `sfence.vma` flushes stale entries.*

---

**Q4. A program calls `malloc(1 GB)` on Linux. The call returns almost instantly even though only 16 MiB of RAM is free. Which mechanism explains this?**

- [ ] The kernel copies data from disk into RAM before returning from malloc.
- [ ] malloc stores the 1 GB in the CPU register file temporarily.
- [x] Demand paging: virtual pages are allocated but physical frames are only assigned on first access.
- [ ] The kernel compresses existing data to make room immediately.

*Explanation: Linux uses demand paging and overcommitment. Virtual memory is reserved but physical frames are only allocated (via minor page faults) when each page is first touched.*

---

**Q5. A page table entry has `V=1, R=1, W=0, X=0, U=1`. A user-mode store instruction targets this page. What happens?**

- [ ] The store succeeds because V=1 and U=1.
- [x] The MMU raises a store page fault because W=0.
- [ ] The MMU raises an instruction page fault because X=0.
- [ ] The store is silently dropped and execution continues.

*Explanation: W=0 means the page is read-only. A store to a read-only page causes a store/AMO page fault (scause=15 on RISC-V). This is how the OS enforces copy-on-write and read-only code segments.*

---

**Q6. Which page replacement policy is theoretically optimal (minimum page faults) but cannot be implemented in practice?**

- [ ] LRU (Least Recently Used)
- [ ] Clock (Second Chance)
- [ ] FIFO (First In, First Out)
- [x] OPT (Optimal) — evict the page that will be accessed furthest in the future

*Explanation: OPT requires knowing the future access sequence, which is impossible at runtime. It serves as a theoretical lower bound to evaluate practical policies like LRU and Clock.*
