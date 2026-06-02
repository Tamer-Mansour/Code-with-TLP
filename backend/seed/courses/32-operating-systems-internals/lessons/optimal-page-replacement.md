# Optimal (OPT) Page Replacement

The **Optimal algorithm (OPT)**, also called MIN or Belady's optimal algorithm, always evicts the page that will not be used for the longest time in the future. It produces the minimum possible number of page faults for any given reference string and frame count.

## How OPT Works

On a page fault, scan the future of the reference string for each page currently in memory. Evict the one whose next use is farthest away. If a page in memory is never used again, it is the perfect victim.

### Worked Example

Reference string: `7 0 1 2 0 3 0 4 2 3 0 3`  
Frames: **3**

```
Step  Ref  Frames          Next use of each page   Evict?   Fault?
  1    7   [7,-,-]         —                        —         YES
  2    0   [7,0,-]         —                        —         YES
  3    1   [7,0,1]         —                        —         YES
  4    2   [7,0,1] full!   7→never, 0→5th, 1→9th   7         YES
           [2,0,1]
  5    0   [2,0,1]         hit                      —         NO
  6    3   [2,0,1] full!   2→8th, 0→7th, 1→9th     1         YES
           [2,0,3]
  7    0   [2,0,3]         hit                      —         NO
  8    4   [2,0,3] full!   2→9th, 0→11th, 3→10th   0         YES
           [2,4,3]
  9    2   [2,4,3]         hit                      —         NO
 10    3   [2,4,3]         hit                      —         NO
 11    0   [2,4,3] full!   2→never, 4→never, 3→12th 2 or 4   YES
           [0,4,3]
 12    3   [0,4,3]         hit                      —         NO
```

**Total page faults: 6** — no algorithm can do better on this string with 3 frames.

## Implementation (Simulation Only)

Because OPT requires knowledge of future references, it can only be implemented as a simulator with the full reference string available in advance:

```python
def opt(pages, n_frames):
    frames = []
    faults = 0
    for i, page in enumerate(pages):
        if page in frames:
            continue                         # hit
        faults += 1
        if len(frames) < n_frames:
            frames.append(page)
        else:
            # find the page whose next use is farthest
            future = pages[i+1:]
            def next_use(p):
                try:
                    return future.index(p)
                except ValueError:
                    return float('inf')      # never used again
            victim = max(frames, key=next_use)
            frames[frames.index(victim)] = page
    return faults
```

Time complexity is O(n × f) where `n` is the reference string length and `f` is the number of frames — acceptable for benchmarking but impractical at runtime.

## Why OPT Matters

OPT cannot be used in a real OS — you cannot know the future. Its value is as a **benchmark**:

- Run OPT on a workload trace and compare real algorithms against it.
- The gap between OPT and a practical algorithm quantifies how much room for improvement exists.
- If LRU achieves 7 faults vs OPT's 6 on a trace, LRU is near-optimal for that workload.

## OPT is a Stack Algorithm

OPT satisfies the stack property: the set of pages in memory with `n+1` frames always includes all pages that would be in memory with `n` frames. Consequently, OPT **never** exhibits Belady's anomaly — more frames always means equal or fewer faults.

## Common Pitfall

When two pages in memory are both "never used again" in the future, either can be the victim — the choice is arbitrary and does not affect the total fault count. In simulations, picking the first one found is fine.

## OPT vs. FIFO vs. LRU (quick comparison)

| Property | OPT | FIFO | LRU |
|---|---|---|---|
| Fault count | Minimum possible | Often high | Near-optimal in practice |
| Needs future info? | Yes | No | No |
| Belady's anomaly | No | Yes | No |
| Implementable? | No (offline only) | Yes | Yes (with cost) |

> **Interview answer:** OPT evicts the page that will not be needed for the longest time in the future, giving the minimum possible page faults. It cannot be implemented in a real OS because it requires future knowledge, but it serves as the theoretical lower bound against which practical algorithms are compared.
