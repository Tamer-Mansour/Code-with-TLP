# Interview Drill: Segmentation and Fragmentation

This lesson compiles the most frequently asked interview questions on segmentation and memory fragmentation. For each question you will find a concise answer that demonstrates depth without rambling — the key skill interviewers evaluate.

## Q1: What is the difference between segmentation and paging?

**Concise answer:** Paging divides both virtual and physical memory into fixed-size units (pages/frames), eliminating external fragmentation at the cost of internal fragmentation and a loss of logical program structure. Segmentation divides virtual memory into variable-length logical units (code, data, heap, stack) that match the programmer's view, introducing external fragmentation but enabling fine-grained per-segment protection.

**Depth add-on:** Modern x86-64 systems use pure paging (segments are flat) but the OS loader still creates separate VMA regions corresponding to the old segment concepts — enforcing permissions via page-table bits rather than segment descriptors.

---

## Q2: What causes a segmentation fault (SIGSEGV)?

**Concise answer:** A segmentation fault is raised by the CPU's memory protection unit when a process accesses an address outside its valid address space — either beyond the limit of a segment (in segmented systems) or via a page-table entry marked not-present or no-access (in paged systems). Common triggers: dereferencing a null pointer, stack overflow, writing to read-only memory, accessing freed memory (use-after-free).

**Pitfall:** Many candidates say "it's because of segmentation" — but on Linux/x86-64 (which uses paging, not segmentation), SIGSEGV is a page-fault that the kernel converts to a signal. The name is historical.

---

## Q3: Explain internal vs. external fragmentation.

**Concise answer:** Internal fragmentation is wasted space *inside* an allocated block — the allocator gave more than was requested (e.g., a 6 KB request in a 4 KB-page system wastes 2 KB inside the second page). External fragmentation is wasted space *between* allocations — total free memory exceeds the request size but no single contiguous region is large enough.

**Key rule:** Paging causes internal fragmentation; segmentation causes external fragmentation.

---

## Q4: Which allocation strategy is best in practice — First-Fit, Best-Fit, or Worst-Fit?

**Concise answer:** First-Fit generally performs best in practice. It is faster (stops scanning at the first suitable hole) and its fragmentation behavior is comparable to Best-Fit. Best-Fit minimizes immediate waste per allocation but creates many tiny, unusable holes over time. Worst-Fit performs worst — it quickly breaks large blocks into medium ones with no lasting benefit.

**Nuance:** Next-Fit (a First-Fit variant that resumes where it last stopped) spreads allocations evenly and avoids clustering small holes at the front of the address space.

---

## Q5: How does free-block coalescing work, and why is boundary tagging needed?

**Concise answer:** When a block is freed, the allocator checks whether the immediately preceding or following block is also free and merges them into one larger block. Without this, repeated alloc/free cycles produce ever-smaller holes that can never satisfy large requests. Boundary tags (a size+status word at the *end* of each block, mirroring the header) allow checking the previous block's status in O(1) without traversing the entire list.

---

## Q6: How does the Buddy System reduce external fragmentation?

**Concise answer:** The Buddy System only allocates blocks whose sizes are powers of two. When a block is freed, it merges with its "buddy" (the adjacent block of the same size, found via XOR) to form a block of size 2×. This controlled splitting and merging keeps the free list organized into size classes and eliminates fragmentation *between* blocks of the same order. The remaining fragmentation is internal — a 5 KB request wastes 3 KB in an 8 KB block.

---

## Q7: Why can't the Linux kernel use compaction to eliminate external fragmentation?

**Concise answer:** Compaction requires moving live data and updating all references to it. For user-space pages, the kernel can remap virtual addresses via the page table. For kernel memory (especially pinned DMA buffers and memory-mapped I/O regions), the physical address is fixed and cannot be changed without breaking device drivers. The Linux kernel therefore relies on the Buddy System plus SLUB/SLOB rather than compaction to manage kernel memory.

---

## Q8: How does the Slab Allocator avoid both internal fragmentation and constructor overhead?

**Concise answer:** The Slab Allocator pre-allocates fixed-size slots for a specific object type (e.g., `task_struct`). Each slot is the exact size of that object — no rounding to a larger power of two (unlike the Buddy System). Objects are initialized once when the slab is created; on free, the object returns to the slab *without* being zeroed. The next allocation reuses the already-initialized object, skipping the constructor — a significant win for objects with complex initialization like kernel spinlocks or list heads.

---

## Quick Reference Cheat Sheet

| Concept | One-liner |
|---|---|
| Segmentation | Variable-length logical regions; seg# + offset → base + offset |
| Paging | Fixed-size pages; page# + offset → frame# + offset |
| Internal fragmentation | Wasted space inside an allocated block |
| External fragmentation | Enough total free space but no contiguous block |
| First-Fit | First hole ≥ size; fastest, best overall |
| Best-Fit | Smallest hole ≥ size; many tiny leftovers |
| Worst-Fit | Largest hole; worst real-world performance |
| Coalescing | Merge adjacent free blocks on free(); O(1) with boundary tags |
| Compaction | Move all live data to eliminate all holes; expensive, needs relocation |
| Buddy System | Power-of-2 blocks; O(log n) alloc/free; used by Linux page allocator |
| Slab Allocator | Fixed-size object caches; O(1) alloc; caches initialized state |
