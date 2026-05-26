# Quiz: Memory Management

**Q1. What problem does paging solve that variable partitioning does not?**

- [ ] Internal fragmentation — paging wastes no space inside a page
- [x] External fragmentation — any free physical frame can hold any virtual page regardless of location
- [ ] TLB thrashing — paging eliminates TLB misses entirely
- [ ] The need for multi-level page tables on 64-bit systems

**Q2. What is stored in a page table entry (PTE)?**

- [ ] The full virtual address of the page and its size
- [ ] The process ID that owns the page and the creation timestamp
- [x] The physical frame number plus status bits: present, dirty, referenced, and protection bits
- [ ] The page's byte offset within the swap file for quick restoration

**Q3. The Translation Lookaside Buffer (TLB) is:**

- [ ] A disk cache that buffers recently-swapped pages to reduce swap I/O latency
- [ ] A kernel data structure in RAM that stores the complete page table for fast access
- [x] A fast hardware cache inside the CPU that stores recent virtual-to-physical address translations
- [ ] A write buffer in the MMU that batches dirty page write-backs to main memory

**Q4. Why does Linux use a 4-level page table on x86-64?**

- [ ] To allow four different processes to share a single physical page simultaneously
- [x] To support 48-bit virtual address spaces without allocating a single flat table that would be hundreds of GB in size
- [ ] To spread TLB entries across multiple CPU cores for better cache performance
- [ ] Because x86-64 processors do not have a Memory Management Unit

**Q5. Bélády's anomaly is the observation that:**

- [ ] LRU always outperforms FIFO for any reference string
- [x] FIFO replacement can produce more page faults when given more physical frames
- [ ] OPT and LRU always produce the same number of faults for any reference string
- [ ] Adding physical frames always reduces page faults for every replacement algorithm

**Q6. Thrashing occurs when:**

- [ ] The TLB hit rate drops below 50% due to a large working set
- [ ] Too many threads are created simultaneously, exhausting kernel stack space
- [x] A process has fewer physical frames than its working set, causing nearly every memory access to trigger a page fault
- [ ] The kernel's swap partition fills up completely and new pages cannot be written out
