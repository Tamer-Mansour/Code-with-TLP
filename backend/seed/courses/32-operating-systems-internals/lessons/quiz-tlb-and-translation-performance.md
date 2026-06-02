# Quiz: The TLB and Address Translation Performance

**Q1. What does the TLB store?**
- [ ] Physical page frames and their contents
- [x] Recent virtual-to-physical page number mappings
- [ ] The full page table for the current process
- [ ] CPU register values during a context switch

_The TLB caches recent VPN→PFN translations so the hardware can skip the page-table walk on subsequent accesses to the same page._

---

**Q2. Using the formula EMAT = h × t_mem + (1-h) × (k+1) × t_mem, what is EMAT when h=0.90, t_mem=100 ns, and k=2 (2-level page table)?**
- [ ] 100 ns
- [ ] 270 ns
- [x] 120 ns
- [ ] 300 ns

_EMAT = 0.90×100 + 0.10×3×100 = 90 + 30 = 120 ns._

---

**Q3. On x86-64, what triggers a page fault (as opposed to a normal TLB miss handled transparently)?**
- [ ] Any access to a virtual address not currently in the TLB
- [ ] Accessing the same page more than 64 times
- [x] A page-table entry is found with the Present (P) bit clear during the hardware walk
- [ ] The TLB capacity is exceeded

_The hardware walks the 4-level page table silently on a TLB miss. Only when a Present bit is clear (page not in physical memory or access violation) does it raise a page fault to the OS._

---

**Q4. What problem do Address Space Identifiers (ASIDs) solve?**
- [ ] They eliminate the need for page tables entirely
- [ ] They allow the TLB to store more entries per physical page
- [x] They allow TLB entries from different processes to coexist, avoiding a full flush on context switch
- [ ] They make the TLB walk faster by reducing the number of levels

_Without ASIDs, every context switch requires flushing all TLB entries because VPNs are only meaningful within one address space. ASIDs tag each entry so multiple address spaces share the TLB simultaneously._

---

**Q5. Which statement correctly describes VIPT (Virtually Indexed, Physically Tagged) cache design?**
- [ ] The cache index and tag both come from the virtual address
- [ ] The TLB must complete before the cache can be accessed
- [x] The cache set is selected using the virtual address while the TLB lookup runs in parallel, and the physical tag is used for comparison
- [ ] VIPT caches always require a full flush on context switch

_VIPT hides TLB latency by indexing the cache with virtual bits simultaneously. The physical tag from the TLB arrives just in time for tag comparison, making the hit path as fast as VIVT without the aliasing problems — provided the index bits fall within the page offset._

---

**Q6. A process accesses 512 MB of heap data with random pointer chasing. The TLB has 64 entries and the page size is 4 KB. Approximately what TLB hit ratio would you expect?**
- [ ] ~99% — the TLB covers most accesses due to temporal locality
- [x] Much less than 99% — the 64-entry TLB covers only 256 KB, far less than the 512 MB working set
- [ ] Exactly 50% — half the accesses hit by chance
- [ ] 0% — random access patterns always miss

_64 entries × 4 KB = 256 KB of coverage. A 512 MB random working set is ~2000× larger, so nearly every access goes to a different page and misses. This is classic TLB thrashing on pointer-heavy workloads._
