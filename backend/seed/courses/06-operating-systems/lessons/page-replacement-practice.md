# Practice: FIFO Page Replacement

Understanding page replacement is essential for reasoning about virtual memory performance. This exercise has you implement the FIFO page replacement simulator.

## Review: FIFO Algorithm

```
Initialize: queue = empty, in_memory = empty set, faults = 0

For each page reference p:
    if p is in in_memory:
        # HIT — do nothing
    else:
        faults += 1
        if len(queue) == num_frames:
            victim = queue.popleft()   # oldest page
            in_memory.remove(victim)
        queue.append(p)
        in_memory.add(p)

Output faults
```

## Key Observations

- A **page fault** occurs every time a referenced page is not currently in memory.
- FIFO uses a queue: the front is the oldest page (eviction candidate).
- Pages already in memory never change position in the queue on a hit.

## Worked Example (3 frames)

```
Reference: 7 0 1 2 0 3 0 4 2 3

Step  Page  Action  Frames
  1    7    FAULT   [7]
  2    0    FAULT   [7,0]
  3    1    FAULT   [7,0,1]
  4    2    FAULT   [0,1,2]   evict 7
  5    0    HIT     [0,1,2]
  6    3    FAULT   [1,2,3]   evict 0
  7    0    FAULT   [2,3,0]   evict 1
  8    4    FAULT   [3,0,4]   evict 2
  9    2    FAULT   [0,4,2]   evict 3
 10    3    FAULT   [4,2,3]   evict 0

Total page faults: 9
```

Now implement the FIFO page replacement simulator.
