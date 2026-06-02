# LRU Page Replacement and Approximations

**Least Recently Used (LRU)** evicts the page that has not been accessed for the longest time. It uses the past as a proxy for the future: a page unused for a long time is likely to remain unused.

## How LRU Works

On every memory access, record the time (or sequence number) of the access for that page. On a page fault, evict the page with the oldest last-access timestamp.

### Worked Example

Reference string: `7 0 1 2 0 3 0 4 2 3 0 3`  
Frames: **3**

```
Ref  Frames (sorted oldest→newest)   Fault?
 7   [7]                              YES
 0   [7,0]                            YES
 1   [7,0,1]                          YES
 2   [0,1,2]  — evict 7 (oldest)      YES
 0   [1,2,0]  — 0 bumped to newest    NO
 3   [2,0,3]  — evict 1 (oldest)      YES
 0   [2,3,0]  — 0 bumped to newest    NO
 4   [3,0,4]  — evict 2 (oldest)      YES
 2   [0,4,2]  — evict 3 (oldest)      YES
 3   [4,2,3]  — evict 0 (oldest)      YES
 0   [2,3,0]  — evict 4 (oldest)      YES
 3   [2,0,3]  — 3 bumped to newest    NO
```

**Total page faults: 8** (vs OPT's 6, vs FIFO's 9 on the same string)

## Exact LRU Implementation Options

### 1. Counter / Timestamp

Each frame stores the time of last access. On a fault, scan all frames and pick the one with the smallest timestamp.

```c
// Pseudocode — O(n_frames) per fault
struct Frame { int page; uint64_t last_used; };

int lru_victim(Frame frames[], int n) {
    int victim = 0;
    for (int i = 1; i < n; i++)
        if (frames[i].last_used < frames[victim].last_used)
            victim = i;
    return victim;
}
```

Downside: requires a hardware clock read on **every** memory access — unacceptably slow on most architectures.

### 2. Stack (Doubly Linked List + Hash Map)

Maintain pages in a doubly linked list ordered by recency. On every access, move the page to the head. The tail is always the LRU victim.

```python
from collections import OrderedDict

def lru(pages, n_frames):
    cache = OrderedDict()   # key=page, ordered by access time
    faults = 0
    for page in pages:
        if page in cache:
            cache.move_to_end(page)   # mark as most recently used
        else:
            faults += 1
            if len(cache) == n_frames:
                cache.popitem(last=False)   # evict LRU (front)
            cache[page] = True
    return faults
```

O(1) per access with a hash map for lookups. This is the standard software LRU implementation.

## Why Exact LRU is Expensive in Hardware

The OS cannot afford to update a linked list on every single memory reference — those happen billions of times per second. Hardware must track accesses, and doing so precisely requires dedicated logic that most real CPUs do not provide.

## LRU Approximations

Real OSes approximate LRU using a single **reference bit** (also called the accessed bit) provided by the MMU hardware:

- The MMU sets the reference bit to 1 whenever a page is accessed.
- The OS periodically clears all reference bits.
- Pages whose bit is still 0 at the next inspection have not been used recently — good candidates for eviction.

### Additional-Reference-Bits Algorithm

Record the reference bit into an 8-bit shift register on a timer interrupt. The page with the smallest integer value of its shift register is LRU:

```
Page A: 00000000  — not accessed in any of the last 8 intervals (best victim)
Page B: 11000100  — accessed recently
Page C: 01110111  — accessed very frequently
```

### NFU (Not Frequently Used)

Count the total number of references. Evict the page with the smallest count. Suffers from "page aging" — a page heavily used months ago still has a high count.

## LRU is a Stack Algorithm

Like OPT, LRU satisfies the stack property and therefore does **not** exhibit Belady's anomaly. More frames always means equal or fewer faults.

## Summary

| Implementation | Overhead | Accuracy |
|---|---|---|
| Counter/timestamp | High (clock per access) | Exact |
| Doubly linked list | Moderate (pointer ops) | Exact |
| Reference bit (single) | Low | Very rough |
| Shift register bits | Low | Good approximation |
| NFU with aging | Low | Good approximation |

> **Interview answer:** LRU evicts the page least recently used, exploiting temporal locality. Exact LRU is too expensive for hardware to track on every reference, so real OSes approximate it using the reference bit set by the MMU — for example, via shift-register aging or the clock algorithm.
