# Interview Drill: Paging and Address Translation

Paging is a near-universal topic in systems interviews at companies that care about OS internals — compilers, kernel teams, hypervisors, game engines, high-frequency trading, and database firms. Use this drill to sharpen your answers before an interview.

## Core Concepts You Must Own

Before practicing the questions below, make sure you can define these cold:

- Virtual page number (VPN), physical frame number (PFN), page offset
- Page table, page table entry (PTE), Present/Dirty/Accessed/Writable bits
- TLB: what it is, hit vs miss, flush on context switch
- Multilevel page tables: why needed, how x86-64 uses 4 levels
- Page fault: what triggers it, what the OS does

## Drill Questions

### Q1: What is a page table and what problem does it solve?

**Crisp answer:** A page table is a per-process array that maps every virtual page number to a physical frame number. It solves the problem of giving each process its own illusion of a large, contiguous address space while actually scattering the process's data across non-contiguous physical frames, eliminating external fragmentation.

---

### Q2: Given a 32-bit virtual address `0x0040107C` and a page size of 4 KB, what are the VPN and offset?

**Work through it:**

```
4 KB = 2^12 bytes → 12 offset bits
VPN    = 0x0040107C >> 12  = 0x00401 = 1025
Offset = 0x0040107C & 0xFFF = 0x07C  = 124
```

**Crisp answer:** VPN = 1025, offset = 124 (0x07C). The split is always a right-shift by log2(page size) for the VPN, and a bitwise AND with (page_size − 1) for the offset.

---

### Q3: Why does a context switch require flushing the TLB?

**Crisp answer:** The TLB caches VPN→PFN mappings but does not store the process ID. After a context switch, the new process has a different page table (CR3 changes), so old TLB entries map to the wrong frames. Failing to flush would allow a process to read another process's memory — a security violation. Tagged TLBs (ASIDs on ARM/x86) avoid a full flush by tagging each entry with an address-space ID.

---

### Q4: What is a page fault and how does the OS handle it?

**Crisp answer:** A page fault fires when the MMU reads a PTE with Present=0. The OS fault handler checks: (1) is the address valid for this process? (2) Is the page in swap? If valid, the handler allocates a free frame, reads the page from swap or disk, updates the PTE (sets Present=1, PFN), and retries the faulting instruction. If invalid, it delivers SIGSEGV.

---

### Q5: Why does x86-64 use a 4-level page table instead of a flat array?

**Crisp answer:** A flat array for a 64-bit virtual address space with 4 KB pages would need 2^52 entries. At 8 bytes per entry that is 32 petabytes per process — clearly impossible. A 4-level tree only allocates tables for regions the process actually uses, keeping memory overhead proportional to the working set.

---

### Q6: What is the difference between the Dirty bit and the Accessed bit?

**Crisp answer:** Both are set by the MMU hardware, not software. The Accessed bit is set on any read or write; the OS clears it periodically to detect recently unused pages for eviction. The Dirty bit is set only on a write; the OS checks it before evicting a page — a dirty page must be written back to disk, a clean page can just be discarded.

---

### Q7: How does copy-on-write use the page table?

**Crisp answer:** After `fork()`, both parent and child share the same physical frames but all shared pages are marked Writable=0. On the first write by either process, a protection fault fires. The fault handler copies the page to a new frame, maps the copy for the faulting process with Writable=1, and retries. Only pages that are actually written are duplicated — unmodified pages are never copied.

---

## Common Mistakes to Avoid

- Saying the OS sets the Dirty/Accessed bits — the hardware does.
- Saying "page fault = crash" — most page faults are routine (demand paging, COW, stack growth).
- Forgetting that the offset is always passed through unchanged from virtual to physical address.
- Confusing page size with page table size — they are different: page size is 4 KB, a single-level 32-bit page table is 4 MB.
- Describing a TLB flush as "slow" without quantifying — a full TLB flush can cost thousands of cycles because the cold TLB forces page-table walks for every subsequent memory access.

> **Interview answer (meta):** Always start with the definition, state the problem it solves, give the formula or algorithm, then note one trade-off or pitfall. Interviewers reward structured thinking over rote memorization.
