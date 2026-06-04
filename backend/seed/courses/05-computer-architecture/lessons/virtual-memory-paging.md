# Virtual Memory and Page Replacement

Virtual memory is one of the most elegant abstractions in computer science: it gives each process the illusion of having its own large, contiguous address space while the physical RAM is shared, fragmented, and potentially much smaller.

## How Virtual Memory Works

The OS divides the virtual address space into fixed-size **pages** (typically 4 KB). Physical memory is divided into the same-sized **page frames**. A **page table** maintained by the OS maps each virtual page number to a physical frame number.

```
Virtual Address:  | VPN (virtual page number) | Page Offset |
Physical Address: | PFN (physical frame number) | Page Offset |

Page Table:  VPN → PFN  (one entry per virtual page)
```

The **Translation Lookaside Buffer (TLB)** is a fast, fully-associative cache of recent VPN→PFN translations. On a TLB hit, address translation costs just 1–2 cycles. On a TLB miss, the hardware (or OS) walks the page table.

## Demand Paging

Pages are loaded from disk into physical RAM **only when first accessed** — this is called a **page fault**. When a page fault occurs:

1. The OS traps the faulting instruction.
2. It finds a free frame (or evicts an existing page).
3. It reads the requested page from disk into the frame.
4. It updates the page table and TLB.
5. It restarts the faulting instruction.

Page fault cost is enormous — ~1 ms (millions of cycles) — so the choice of **which page to evict** matters greatly.

## Page Replacement Algorithms

When all physical frames are occupied and a new page must be loaded, the OS must evict an existing page. The goal: minimize future page faults.

### Optimal (OPT / Belady's Algorithm)

Evict the page that will not be referenced for the longest time in the future. This is provably optimal but requires future knowledge — it is used only as a theoretical benchmark.

### FIFO (First In, First Out)

Evict the page that has been in memory the longest. Simple to implement (just a queue), but suffers from **Belady's anomaly**: more frames can sometimes cause more page faults.

```
3 frames, reference string: 1 2 3 4 1 2 5 1 2 3 4 5
FIFO faults: 9
```

### LRU (Least Recently Used)

Evict the page that was **least recently used**. Approximates the optimal algorithm based on the principle that recently used pages are likely to be used again soon (temporal locality).

```python
from collections import OrderedDict

def lru_cache(frames, pages):
    cache = OrderedDict()  # most recently used at the END
    faults = 0
    for page in pages:
        if page in cache:
            cache.move_to_end(page)   # mark as most recently used
        else:
            faults += 1
            if len(cache) == frames:
                cache.popitem(last=False)  # evict LRU (leftmost)
            cache[page] = True
    return faults
```

LRU does not suffer from Belady's anomaly. However, exact LRU tracking requires hardware support (a timestamp or stack per page).

### Clock Algorithm (Approximate LRU)

The clock algorithm is a practical approximation used in real OS kernels (Linux uses a variant). Each page frame has a **reference bit** set to 1 when the page is accessed. The OS clock hand sweeps through frames:

- If reference bit = 1: clear it (give the page a second chance) and advance.
- If reference bit = 0: evict this page.

This is O(1) per page fault and achieves performance close to LRU.

## AMAT with Virtual Memory

Adding virtual memory introduces an extra layer to the memory hierarchy:

```
AMAT = TLB_hit_time + TLB_miss_rate × (page_table_walk_time + page_fault_rate × disk_time)
```

With a 1% TLB miss rate and 0.001% page fault rate:

```
TLB hit: 1 cycle
Page table walk on TLB miss: 100 cycles
Disk access on page fault: 10,000,000 cycles

AMAT = 1 + 0.01 × (100 + 0.00001 × 10,000,000)
     = 1 + 0.01 × (100 + 100)
     = 1 + 0.01 × 200
     = 1 + 2 = 3 cycles
```

Even a tiny page fault rate dominates the AMAT calculation. This is why minimizing page faults is critical for performance.

## Further Reading

- **MIT 6.004 Computation Structures** (https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/) — Lectures on virtual memory, paging, and TLB design.
- **Nand2Tetris** (https://www.nand2tetris.org/) — Chapter on memory management provides foundational context for how physical and virtual memory layers interact.
