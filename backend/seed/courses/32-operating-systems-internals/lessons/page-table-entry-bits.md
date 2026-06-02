# Page Table Entry Bits: Valid, Dirty, Accessed, Protection

Every page table entry (PTE) is more than just a frame number. The lower bits carry metadata that the hardware and OS cooperate to maintain. Understanding each bit is essential for implementing virtual memory, demand paging, copy-on-write, and memory-mapped files.

## Anatomy of an x86-32 PTE

```
 31                    12 11  9  8  7  6  5  4  3  2  1  0
+------------------------+----+--+--+--+--+--+--+--+--+--+
|  Physical Frame Number |IGN |G |PS|D |A |CD|WT|U |W |P |
+------------------------+----+--+--+--+--+--+--+--+--+--+
```

## Bit-by-Bit Breakdown

### Present (P) — bit 0

The most important bit. `P=1` means the page is resident in physical RAM. `P=0` means it is not.

- When the MMU reads a PTE with `P=0`, it raises a **page fault** (interrupt 14 on x86).
- The OS fault handler decides what to do: load from swap, allocate a zeroed frame, or deliver `SIGSEGV`.
- The OS *intentionally* clears this bit to evict a page to disk — the remaining bits can be repurposed to store the swap location.

### Writable (W) — bit 1

Controls write permission for this page.

- `W=0` on a write → protection fault (`SIGSEGV`).
- **Copy-on-write (COW)**: `fork()` marks shared pages `W=0`. On the first write, a fault fires; the handler copies the page, sets `W=1` on the copy, and retries the instruction.

### User (U) — bit 2

`U=0` means kernel-only; a user-mode access raises a protection fault. This is the hardware enforcer of the kernel/user boundary. Kernel memory is mapped in every process's page table with `U=0`, making kernel addresses inaccessible from user mode.

### Write-Through (WT) — bit 3 and Cache Disable (CD) — bit 4

Control the CPU cache policy for this page:

| WT | CD | Policy |
|----|----|----|
| 0 | 0 | Write-back (default, highest performance) |
| 1 | 0 | Write-through |
| 0 | 1 | Uncacheable (used for memory-mapped I/O registers) |

Device drivers set `CD=1` for MMIO regions to ensure every read/write reaches the device immediately.

### Accessed (A) — bit 5

**Set by the MMU** on any read or write to the page. The OS clears it periodically (e.g., on a clock tick) and uses it to approximate LRU:

```
Not accessed recently → candidate for eviction
Recently accessed      → keep in RAM
```

This is the hardware foundation of the **Clock (Second-Chance)** page replacement algorithm.

### Dirty (D) — bit 6

**Set by the MMU** on any write. Tells the OS whether the page has been modified since it was loaded:

```python
if pte.dirty:
    write_page_to_swap(page)   # must write back
else:
    discard(page)              # clean — just reuse the frame
```

Without this bit, every evicted page would need to be written to disk, doubling I/O traffic.

### Global (G) — bit 8

`G=1` prevents the TLB entry from being flushed on a CR3 reload (context switch). Used for kernel pages that are the same in every process. Avoids TLB pollution from repeated kernel entry/exit.

### Page Size (PS) — bit 7

In a PD or PDPT entry, `PS=1` short-circuits the walk: the entry maps a 2 MB (PD) or 1 GB (PDPT) huge page directly. The "frame number" field then refers to the huge-page-aligned frame.

## OS–Hardware Cooperation

| Bit | Who sets it | Who reads it |
|-----|------------|-------------|
| Present | OS | MMU (raises fault if 0) |
| Writable | OS | MMU (raises fault on write if 0) |
| User | OS | MMU (raises fault if user-mode and 0) |
| Accessed | MMU (hardware) | OS (page replacement policy) |
| Dirty | MMU (hardware) | OS (eviction write-back decision) |
| CD/WT | OS | CPU cache |

## Common Pitfalls

- Assuming the OS sets the Accessed and Dirty bits — the MMU sets them; the OS only *clears* them.
- Forgetting to flush the TLB after changing a PTE — stale TLB entries can cause the CPU to use an outdated mapping for many cycles.
- Overlooking that a cleared Present bit leaves 31 bits free for OS use (e.g., storing a swap block number) — a common optimization.

> **Interview answer:** A PTE holds the physical frame number plus control bits: Present (page in RAM), Writable and User (protection), Accessed and Dirty (set by hardware to support LRU approximation and skip unnecessary disk writes), and cache control bits. The OS sets protection bits and reads hardware-maintained Accessed/Dirty bits to implement page replacement and copy-on-write.
