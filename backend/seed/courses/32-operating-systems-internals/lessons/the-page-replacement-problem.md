# The Page Replacement Problem

When physical memory fills up, the OS must decide which page to evict to make room for an incoming page. This decision — choosing the victim page — is the **page replacement problem**.

## Why Page Replacement Exists

Modern systems run more processes than physical RAM can hold at once. Virtual memory allows this by keeping only active pages in RAM and the rest on disk (the swap space or page file). When a process accesses a page not currently in RAM, a **page fault** occurs:

1. The CPU traps to the OS.
2. The OS finds a free frame, or selects a victim page to evict.
3. If the victim page is **dirty** (modified), it is written back to disk first.
4. The requested page is loaded from disk into the freed frame.
5. The page table is updated and the faulting instruction is retried.

The cost of a page fault is enormous — disk I/O takes millions of CPU cycles — so minimizing page faults is the primary goal of any replacement algorithm.

## Key Metrics

| Metric | Meaning |
|---|---|
| Page fault rate | Fraction of memory accesses that miss in RAM |
| Effective access time (EAT) | Weighted average of hit and fault cost |
| Dirty page ratio | How often victim pages must be written back |

**Effective access time formula:**

```
EAT = (1 - p) * memory_time + p * page_fault_time
```

With `p = 0.001` (1 fault per 1000 accesses), `memory_time = 100 ns`, and `page_fault_time = 8 ms`:

```
EAT = 0.999 * 100ns + 0.001 * 8,000,000ns ≈ 8,100 ns
```

A tiny fault rate blows EAT up 81×. Algorithms must keep `p` as close to zero as possible.

## The Reference String

Algorithms are evaluated against a **reference string**: the sequence of page numbers a process accesses over time.

```
Reference string: 7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1
Frames available: 3
```

We count how many references cause a page fault for each algorithm. Repeated accesses to the same page back-to-back count as a single event (the second hit costs nothing).

## What Makes a Good Replacement Algorithm?

A replacement algorithm should:

- **Minimize page faults** — above all else.
- **Prefer clean pages** over dirty pages (avoiding a write-back).
- **Run fast** — the algorithm itself must not add significant overhead.
- **Work well with locality of reference** — most programs exhibit temporal and spatial locality, so recently used pages and pages near currently used pages should be kept.

## Locality of Reference

Programs do not access memory randomly. Two key principles:

- **Temporal locality**: a page used recently is likely to be used again soon (loops, hot data).
- **Spatial locality**: if page `n` is used, pages `n±1` are likely to be used soon (sequential scans, arrays).

Good replacement algorithms exploit temporal locality by protecting recently used pages from eviction.

## Frame Allocation Affects Fault Rate

The number of frames (physical page slots) given to a process directly impacts its fault rate. More frames generally means fewer faults — but not always. The **Belady anomaly** (covered in the next lesson) shows that for some algorithms, giving a process *more* frames can actually *increase* faults.

## The Goal: Approximate Omniscience

The theoretically optimal algorithm (covered later) would need to know the **future** reference string to make perfect decisions. Real systems cannot do that, so practical algorithms approximate optimal behavior using past access history as a proxy for future behavior.

> **Interview answer:** A page replacement algorithm selects a victim page to evict when a page fault occurs and no free frame is available. The goal is to minimize future page faults; algorithms approximate this by tracking recency or frequency of access, since future references cannot be known.
