# Virtual Memory and Page Replacement

**Virtual memory** allows a process to use more memory than is physically available by storing infrequently-used pages on a **swap device** (disk or SSD). The illusion is maintained by demand paging: only load a page when it is actually accessed. When RAM is full, a **page replacement algorithm** chooses which page to evict to make room.

## The Page Fault Sequence

When the CPU accesses a virtual address whose page table entry has the **present bit = 0**:

```
Step 1: MMU raises a page fault exception (hardware)
        CPU → kernel mode (ring 0)
        Saves: VA that caused fault (CR2 register on x86)

Step 2: OS page fault handler runs
   a. Check: is the VA within a valid VMA (virtual memory area)?
      NO  → SIGSEGV to the process (segmentation fault — program bug)
      YES → continue

   b. Check: is this the process's first access to a demand-paged region?
      YES → allocate a free frame, zero-fill it, update PTE, return
      NO  → page was evicted to swap

   c. Find the page on the swap device (swap address stored in PTE)

   d. Is there a free frame?
      YES → load the page into it
      NO  → SELECT A VICTIM FRAME using the replacement policy:
            - If victim page is CLEAN (not modified): discard it
            - If victim page is DIRTY (modified, dirty bit set):
              write it to swap first, then reuse the frame

   e. Load the requested page from swap into the (now-free) frame

   f. Update the PTE: set frame number, set present bit=1

Step 3: Return to user mode
        The faulting instruction re-executes — this time the TLB hits
```

**Cost breakdown:**
- Clean eviction + load from SSD: ~100 µs
- Dirty eviction + load from SSD: ~200 µs (two SSD operations)
- Load from spinning HDD: ~10 ms
- TLB hit (no fault): ~1 ns

Page fault cost is ~100,000× more than a normal memory access. Minimizing faults is critical.

## Page Replacement Algorithms

### Optimal (OPT / Bélády's Algorithm)

Replace the page whose **next use is furthest in the future**. This is provably optimal (fewest page faults possible) but requires knowing the entire future reference string — impossible in practice. Used only as a theoretical lower bound.

**Trace with 3 frames, reference string: 7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1**

(We will use the classic 3-frame example from Silberschatz):

```
Reference string: 7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1
Frames = 3

Ref  Frames      Fault?
 7   [7,-,-]      F
 0   [7,0,-]      F
 1   [7,0,1]      F
 2   [2,0,1]      F  (evict 7: next use of 7 is far away)
 0   [2,0,1]      -
 3   [2,0,3]      F  (evict 1: next use of 1 is at step 14)
 0   [2,0,3]      -
 4   [4,0,3]      F  (evict 2: next use of 2 is at step 9)
 2   [4,0,2]      F  (evict 3: next use of 3 is at step 10 vs 4 at ?)
... (continuing)

Total OPT faults: 9
```

### FIFO (First-In, First-Out)

Evict the page that has been in memory the **longest** (oldest arrival). Simple to implement with a queue.

**Trace with 3 frames, reference string: 1 2 3 4 1 2 5 1 2 3 4 5**

```
Ref  Queue (oldest→newest)  Frames    Fault?  Evicted
 1   [1]                    {1}        F
 2   [1,2]                  {1,2}      F
 3   [1,2,3]                {1,2,3}    F
 4   [2,3,4]                {2,3,4}    F  (evict 1, oldest)
 1   [3,4,1]                {3,4,1}    F  (evict 2)
 2   [4,1,2]                {4,1,2}    F  (evict 3)
 5   [1,2,5]                {1,2,5}    F  (evict 4)
 1   [1,2,5]                {1,2,5}    -  (hit)
 2   [1,2,5]                {1,2,5}    -  (hit)
 3   [2,5,3]                {2,5,3}    F  (evict 1)
 4   [5,3,4]                {5,3,4}    F  (evict 2)
 5   [5,3,4]                {5,3,4}    -  (hit)

Total FIFO faults: 9
```

**Bélády's Anomaly:** FIFO can produce MORE page faults with MORE frames. For the string `1 2 3 4 1 2 5 1 2 3 4 5`:
- 3 frames: 9 faults
- 4 frames: 10 faults  ← MORE faults with more memory!

This counter-intuitive result does not affect LRU or OPT — they are **stack algorithms** that always improve (or stay same) with more frames.

### LRU (Least Recently Used)

Evict the page that was used **least recently**. Exploits temporal locality: pages used recently are likely to be used again soon.

**Same trace, 3 frames:**

```
Ref  LRU order (MRU→LRU)   Frames    Fault?  Evicted
 1   [1]                    {1}        F
 2   [2,1]                  {1,2}      F
 3   [3,2,1]                {1,2,3}    F
 4   [4,3,2]                {2,3,4}    F  (evict 1, LRU)
 1   [1,4,3]                {1,3,4}    F  (evict 2, LRU)
 2   [2,1,4]                {1,2,4}    F  (evict 3, LRU)
 5   [5,2,1]                {1,2,5}    F  (evict 4, LRU)
 1   [1,5,2]                {1,2,5}    -  (hit — promote 1 to MRU)
 2   [2,1,5]                {1,2,5}    -  (hit)
 3   [3,2,1]                {1,2,3}    F  (evict 5, LRU)
 4   [4,3,2]                {2,3,4}    F  (evict 1, LRU)
 5   [5,4,3]                {3,4,5}    F  (evict 2, LRU)

Total LRU faults: 10  (worse than FIFO on this string — illustrates no algorithm dominates!)
```

LRU is **not trivially cheap**: true LRU requires updating a sorted data structure on every single memory access — millions of times per second. Hardware support (like a counter incremented on each access) would be prohibitively expensive. Real OSes use approximations.

### Clock Algorithm (Second Chance)

A practical O(1) approximation of LRU using a single **reference bit** per page (hardware sets it on access, OS reads and clears it):

```
Data structure: circular list of page frames, "clock hand" pointer

On page fault (need to evict a victim):
  Loop:
    Page at clock hand:
      reference bit = 1? → clear it (give it a "second chance"), advance hand
      reference bit = 0? → evict this page, load new page here, advance hand
```

**Example trace:**

```
Frames: A(ref=1), B(ref=1), C(ref=0), D(ref=1)  ← hand points at A

Fault arrives (need to evict):
  A: bit=1 → clear (A.ref=0), hand → B
  B: bit=1 → clear (B.ref=0), hand → C
  C: bit=0 → EVICT C, load new page here, hand → D

If the new page is accessed again before the next fault,
  its reference bit gets set to 1 — it won't be evicted next time.
```

Linux uses an enhanced version: pages start in the **active list** and move to the **inactive list** when their reference bit is cleared. Pages on the inactive list are eviction candidates. This is the **two-list clock** (or LRU/2 variant) in the Linux page reclaim code.

### Least Frequently Used (LFU)

Evict the page with the lowest **access count** since it was loaded. Intuition: frequently used pages are likely to remain needed. Downside: old pages with a historically high count but no recent use are protected, polluting the cache. Rarely used in practice.

## Full Algorithm Comparison

```
Reference string: 7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1  (3 frames)

Algorithm   Page Faults   Notes
OPT              9        Theoretical minimum
LRU             12        Good approximation; high exact implementation cost
Clock           ~12       Near-LRU with O(1) overhead; used in Linux
FIFO            15        Simple; Bélády's anomaly; not recommended
LFU             ~14       Penalizes bursty patterns
```

## Working Set Model

The **working set** W(t, Δ) of a process at time t is the set of pages it has referenced in the window of Δ most recent accesses. If the OS cannot provide a process with frames equal to its working set size, the process will continuously page-fault.

```
Working set size over time:
  Phase 1 (loading):     W = 10–30 pages   (many new pages accessed)
  Phase 2 (steady):      W = 5–8 pages     (working on a small dataset)
  Phase 3 (transition):  W = 15–25 pages   (switching between tasks)
```

The OS monitors working set sizes and reduces **multiprogramming degree** if the aggregate working set exceeds available frames.

## Thrashing

If a process has fewer frames than its working set, it will continuously page-fault:

```
Every memory access faults → OS spends all time on page I/O → CPU utilization crashes to near 0%

CPU utilization vs. degree of multiprogramming:
  100% |         ●●●●
       |       ●       ●
       |     ●           ●
       |   ●               ●●●● ← thrashing begins here
     0%+──────────────────────────►
            degree of multiprogramming
```

**Prevention:**
- Monitor page fault rate per process; if too high, reduce multiprogramming (swap out or suspend a process).
- Linux's **Out-Of-Memory (OOM) killer** selects and kills a process when virtual memory is exhausted, freeing frames for survivors.

## Practical Linux Tuning

```bash
# Check page fault counters for a process
cat /proc/<pid>/stat | awk '{print "minor_faults="$10, "major_faults="$12}'

# View virtual memory stats (page fault rate system-wide)
vmstat 1    # pgflt/s column

# Check swap usage
free -h
swapon --show

# Adjust swappiness (0=swap last resort, 100=swap aggressively)
sysctl vm.swappiness=10
```

## Key Takeaways

- **Virtual memory** allows processes to exceed physical RAM by paging infrequently-used pages to a swap device.
- A **page fault** triggers the OS to load the missing page (possibly evicting a victim), costing ~100 µs to ~10 ms.
- **OPT** is the theoretical minimum but requires knowing the future.
- **FIFO** is simple but suffers from Bélády's anomaly (more frames → more faults).
- **LRU** approximates optimal well but is expensive to implement exactly.
- The **Clock algorithm** approximates LRU with O(1) overhead using a reference bit — this is what Linux uses.
- **Thrashing** occurs when aggregate working sets exceed available frames; the OS must reduce multiprogramming.
