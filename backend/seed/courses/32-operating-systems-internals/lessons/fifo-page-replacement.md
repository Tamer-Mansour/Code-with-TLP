# FIFO Page Replacement and Belady's Anomaly

**First-In, First-Out (FIFO)** is the simplest page replacement algorithm: when a victim must be chosen, evict the page that has been in memory the longest.

## How FIFO Works

Maintain a queue of pages in the order they were loaded into memory. When a page fault occurs and all frames are full, remove the page at the front of the queue (the oldest resident) and load the new page at the back.

### Worked Example

Reference string: `1 2 3 4 1 2 5 1 2 3 4 5`  
Frames: **3**

```
Ref  Frame0  Frame1  Frame2  Fault?
 1     1       -       -       YES
 2     1       2       -       YES
 3     1       2       3       YES
 4     4       2       3       YES  (evict 1, oldest)
 1     4       1       3       YES  (evict 2, oldest)
 2     4       1       2       YES  (evict 3, oldest)
 5     5       1       2       YES  (evict 4, oldest)
 1     5       1       2       NO
 2     5       1       2       NO
 3     5       3       2       YES  (evict 1, oldest)
 4     5       3       4       YES  (evict 2, oldest)
 5     5       3       4       NO
```

**Total page faults: 9**

## Implementation

A queue (circular buffer or linked list) of frame contents is sufficient:

```python
from collections import deque

def fifo(pages, n_frames):
    queue = deque()       # tracks insertion order
    in_memory = set()
    faults = 0
    for page in pages:
        if page not in in_memory:
            faults += 1
            if len(queue) == n_frames:
                victim = queue.popleft()
                in_memory.remove(victim)
            queue.append(page)
            in_memory.add(page)
    return faults
```

FIFO is O(1) per access and requires no extra hardware support, making it attractive for systems with tight implementation budgets.

## Belady's Anomaly

Most people assume that giving a process more frames always reduces (or at worst keeps the same) page faults. FIFO violates this intuition.

**Belady's anomaly**: for FIFO (and some other algorithms), increasing the number of frames can **increase** the number of page faults on certain reference strings.

### Classic Demonstration

Reference string: `1 2 3 4 1 2 5 1 2 3 4 5`

| Frames | Page Faults (FIFO) |
|--------|-------------------|
| 3      | 9                 |
| 4      | 10                |

With 4 frames, FIFO produces **more** faults than with 3 frames for this exact sequence.

### Why It Happens

FIFO evicts based purely on age, not usefulness. With more frames, the "oldest" page at any eviction point may differ in a way that happens to knock out a heavily reused page that a 3-frame policy happened to retain.

Algorithms that do **not** suffer from Belady's anomaly are called **stack algorithms**. A stack algorithm has the property that the set of pages in memory with `n+1` frames is always a superset of the set with `n` frames. LRU and OPT are stack algorithms; FIFO is not.

## Pros and Cons

| Aspect | Detail |
|---|---|
| Simplicity | Trivial to implement — just a queue |
| Hardware support | None required |
| Performance | Often poor; ignores recency |
| Belady's anomaly | Yes — more frames can hurt |
| Used in practice? | Rarely alone; used as a fallback or baseline |

## Common Pitfall

Students often forget that FIFO does **not** reset a page's position in the queue when it is accessed again. Accessing page `3` five times in a row does not make it "newer" — it was loaded once and stays at its original queue position.

> **Interview answer:** FIFO evicts the page that has been in memory the longest. It is simple but performs poorly because it ignores recency of use. It also suffers from Belady's anomaly — adding more frames can paradoxically increase page faults — unlike stack algorithms such as LRU and OPT.
