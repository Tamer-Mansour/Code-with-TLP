# Quiz: Segmentation and Fragmentation

**Q1. A process makes a 6 KB memory request in a system that allocates memory in 4 KB pages. How much internal fragmentation results?**
- [ ] 0 KB — pages are exactly 4 KB
- [ ] 4 KB — the entire second page is wasted
- [x] 2 KB — the second page is used for 2 KB and 2 KB is wasted
- [ ] 6 KB — the entire request is wasted

Internal fragmentation = allocated size − requested size. The request rounds up to 2 pages (8 KB), so 8 KB − 6 KB = 2 KB is wasted inside the second page.

---

**Q2. Free memory blocks are: 20 KB, 8 KB, 40 KB, 12 KB (in address order). A process requests 10 KB. Which block does First-Fit choose?**
- [x] 20 KB block
- [ ] 8 KB block (too small)
- [ ] 40 KB block
- [ ] 12 KB block

First-Fit scans from the lowest address and picks the **first** block that is large enough. The 20 KB block (first in order) satisfies the 10 KB request.

---

**Q3. Which memory management scheme suffers from external fragmentation but NOT internal fragmentation?**
- [ ] Fixed-partition allocation
- [ ] Pure paging
- [x] Pure segmentation
- [ ] Slab allocation

Pure segmentation allocates exactly as many bytes as requested (zero internal fragmentation) but leaves variable-size holes between segments (external fragmentation). Pure paging does the opposite.

---

**Q4. What is the purpose of a boundary tag (footer) in a heap allocator?**
- [ ] To store the process ID that owns the block
- [ ] To speed up first-fit search by caching recent results
- [x] To allow O(1) coalescing with the previous block when freeing
- [ ] To align blocks on cache-line boundaries

A boundary tag mirrors the block size and status at the *end* of each block. When a block is freed, the allocator reads the previous block's footer to determine its status without traversing the free list.

---

**Q5. In the Buddy System, a block at address 0x2000 of size 4 KB (2^12 bytes) has its buddy at:**
- [ ] 0x1000
- [x] 0x3000
- [ ] 0x4000
- [ ] 0x2800

Buddy address = address XOR size = 0x2000 XOR 0x1000 = 0x3000. The buddy is the adjacent block of the same size whose address differs only in the bit corresponding to the block size.

---

**Q6. Which statement best describes why Best-Fit often performs worse than First-Fit in practice?**
- [ ] Best-Fit is slower because it cannot use a sorted free list
- [ ] Best-Fit allocates more memory than needed, increasing internal fragmentation
- [x] Best-Fit leaves many tiny leftover fragments that are too small to satisfy future requests
- [ ] Best-Fit requires compaction after every allocation

Best-Fit minimizes waste per allocation by choosing the tightest-fitting hole, but the tiny slivers left over accumulate as unusable external fragments, increasing total fragmentation over time.
