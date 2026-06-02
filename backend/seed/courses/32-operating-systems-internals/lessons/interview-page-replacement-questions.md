# Interview Drill: Page Replacement Questions

This lesson consolidates the most common interview questions on page replacement algorithms, with crisp, accurate answers you can deliver confidently in 30–60 seconds.

---

## Q1: What is a page fault, and what happens when one occurs?

A page fault is a hardware trap raised by the MMU when the CPU accesses a virtual page that is not currently mapped to a physical frame. The OS page-fault handler:

1. Finds a free frame, or selects a victim using a replacement algorithm.
2. Writes the victim frame to disk if it is dirty (modified bit = 1).
3. Reads the requested page from disk into the now-free frame.
4. Updates the page table entry and clears the fault flag.
5. Restarts the faulting instruction.

**One-liner:** A page fault triggers the OS to load a missing page from disk, optionally evicting a victim page first.

---

## Q2: Compare FIFO, LRU, and OPT.

| Property | FIFO | LRU | OPT |
|---|---|---|---|
| Eviction criterion | Longest in memory | Least recently used | Not needed longest |
| Belady's anomaly | Yes | No | No |
| Stack algorithm? | No | Yes | Yes |
| Needs future info? | No | No | Yes |
| Practical? | Yes (simple) | Yes (approximate) | No (offline only) |
| Typical fault count | High | Near-optimal | Minimum |

**One-liner:** FIFO is simple but poor; LRU approximates optimal via temporal locality; OPT is the theoretical minimum but requires future knowledge.

---

## Q3: What is Belady's anomaly? Which algorithms suffer from it?

Belady's anomaly is the counterintuitive result that **increasing the number of frames can increase page faults** for some algorithms.

Classic example with FIFO on reference string `1 2 3 4 1 2 5 1 2 3 4 5`:
- 3 frames → 9 faults
- 4 frames → 10 faults

**Only non-stack algorithms** exhibit this. FIFO is the canonical example. Stack algorithms (LRU, OPT) guarantee that adding a frame never increases faults.

**One-liner:** Belady's anomaly means more frames can cause more faults with FIFO; it cannot happen with LRU or OPT because they are stack algorithms.

---

## Q4: Why is exact LRU rarely used in real operating systems?

Exact LRU requires tracking the precise order of page accesses. Two approaches exist:

- **Timestamps**: read a clock on every memory access — billions of operations per second — unacceptable overhead.
- **Doubly linked list + hash map**: requires pointer manipulation on every access, which cannot be done efficiently in hardware for every single memory reference.

Real OSes instead approximate LRU using the **reference bit** (set by MMU hardware on each access), cleared periodically by the OS. The **clock algorithm** and its variants (enhanced clock, Linux's two-list active/inactive scheme) deliver near-LRU performance with O(1) cost per fault.

**One-liner:** Exact LRU is too costly because it requires tracking every memory access; the clock algorithm approximates it cheaply using a single hardware reference bit.

---

## Q5: What is thrashing, and how is it prevented?

Thrashing occurs when a process (or the whole system) has fewer frames than its **working set** — the pages actively referenced in a short window. The process continuously faults, the OS spends more time swapping than running code, and CPU utilization collapses.

Prevention strategies:

- **Working set model**: track the active working set; only schedule a process if enough free frames exist to hold its working set.
- **Page fault frequency (PFF)**: add frames if a process's fault rate exceeds an upper threshold; reclaim frames if it drops below a lower threshold.
- **Load control**: reduce the degree of multiprogramming (suspend processes) when system-wide fault rate is too high.

**One-liner:** Thrashing happens when a process lacks enough frames for its working set; it is prevented by tracking working sets or fault rates and adjusting frame allocation or multiprogramming level.

---

## Q6: What is the clock algorithm, and how does it work?

The clock algorithm arranges frames in a circular buffer with a sweeping pointer ("hand"). Each frame has a reference bit set by hardware on access.

On a page fault:
1. Check the frame under the hand.
2. If `ref = 0`: evict this page, load the new page, advance the hand.
3. If `ref = 1`: clear `ref` to 0 (give a second chance), advance the hand, repeat.

Heavily used pages keep getting their bit reset to 1 before the hand returns, so they survive. Cold pages accumulate `ref = 0` and get evicted promptly.

**One-liner:** The clock algorithm sweeps frames in a circle, evicting the first page with a reference bit of 0 and giving pages with a bit of 1 a second chance by clearing the bit.

---

## Q7: Global vs. Local replacement — which does Linux use and why?

Linux uses **global replacement**. Frames are pooled system-wide; any process's page fault handler can steal a frame from any other process's pages. This maximizes memory utilization — idle processes' cold pages are reclaimed automatically and given to active processes.

Local replacement would lock in allocations even when one process is idle, wasting memory.

**One-liner:** Linux uses global replacement to maximize utilization by allowing active processes to reclaim frames from idle ones.
