# FIFO vs LRU Page Replacement: Side-by-Side Comparison

When studying page replacement, it is illuminating to run both **FIFO** and **LRU** on the same reference string at the same time. The comparison sharpens intuition about why recency information matters.

## Recap: The Two Algorithms

**FIFO (First-In, First-Out)** evicts the page that has been resident in memory the longest, regardless of how recently it was used. It maintains a queue ordered by load time.

**LRU (Least Recently Used)** evicts the page whose last access was furthest in the past. On every access — hit or miss — LRU notes the current time for the referenced page.

## Classic Reference String Demonstration

Reference string: `7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1`
Frames: **3**

### FIFO Trace

```
Ref  Frame Set (FIFO queue)          Fault?
 7   [7]                              YES
 0   [7, 0]                           YES
 1   [7, 0, 1]                        YES
 2   [0, 1, 2]  evict 7 (oldest)      YES
 0   [0, 1, 2]  hit                   NO
 3   [1, 2, 3]  evict 0 (oldest)      YES
 0   [2, 3, 0]  evict 1               YES
 4   [3, 0, 4]  evict 2               YES
 2   [0, 4, 2]  evict 3               YES
 3   [4, 2, 3]  evict 0               YES
 0   [2, 3, 0]  evict 4               YES
 3   [2, 3, 0]  hit                   NO
 2   [2, 3, 0]  hit                   NO
 1   [3, 0, 1]  evict 2               YES
 2   [0, 1, 2]  evict 3               YES
 0   [0, 1, 2]  hit                   NO
 1   [0, 1, 2]  hit                   NO
 7   [1, 2, 7]  evict 0               YES
 0   [2, 7, 0]  evict 1               YES
 1   [7, 0, 1]  evict 2               YES
```

**FIFO page faults: 15**

### LRU Trace

```
Ref  Frame Set (MRU→LRU order)        Fault?
 7   [7]                               YES
 0   [0, 7]                            YES
 1   [1, 0, 7]                         YES
 2   [2, 1, 0]  evict 7 (LRU)          YES
 0   [0, 2, 1]  hit, 0 moves to MRU    NO
 3   [3, 0, 2]  evict 1 (LRU)          YES
 0   [0, 3, 2]  hit, 0 moves to MRU    NO
 4   [4, 0, 3]  evict 2 (LRU)          YES
 2   [2, 4, 0]  evict 3 (LRU)          YES
 3   [3, 2, 4]  evict 0 (LRU)          YES
 0   [0, 3, 2]  evict 4 (LRU)          YES
 3   [3, 0, 2]  hit                    NO
 2   [2, 3, 0]  hit                    NO
 1   [1, 2, 3]  evict 0 (LRU)          YES
 2   [2, 1, 3]  hit                    NO
 0   [0, 2, 1]  evict 3 (LRU)          YES
 1   [1, 0, 2]  hit                    NO
 7   [7, 1, 0]  evict 2 (LRU)          YES
 0   [0, 7, 1]  hit                    NO
 1   [1, 0, 7]  hit                    NO
```

**LRU page faults: 12**

On this reference string, LRU saves **3 page faults** relative to FIFO.

## Key Differences

| Property | FIFO | LRU |
|---|---|---|
| Eviction criterion | Oldest load time | Oldest access time |
| Belady's anomaly | Yes — more frames can increase faults | No — LRU is a stack algorithm |
| Hardware cost | None | Reference bit or timestamp hardware |
| Accuracy | Age proxy, ignores recency | Good approximation of optimal |

## When LRU Wins

LRU benefits from **temporal locality** — the tendency of programs to reuse recently accessed pages. FIFO ignores whether a page was just accessed: it can evict a hot page simply because it was loaded long ago.

LRU is not always better than FIFO. On a pathological **cyclic scan** pattern (e.g., 1 2 3 4 5 1 2 3 4 5 with 4 frames), both produce the same fault count. The advantage appears on workloads with genuine temporal locality.

## Further Reading

- **OSTEP Chapter 22: Beyond Physical Memory — Policies** (https://pages.cs.wisc.edu/~remzi/OSTEP/) — full worked examples of FIFO, LRU, OPT, and clock approximation.
- **xv6 book Section on page tables** (https://pdos.csail.mit.edu/6.828/2023/xv6/book-riscv-rev3.pdf) — how the reference bit works on real hardware.
