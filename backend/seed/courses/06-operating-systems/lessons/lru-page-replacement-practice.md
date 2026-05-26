# Practice: LRU Page Replacement

Least Recently Used (LRU) page replacement evicts the page that has not been accessed for the longest time. It closely approximates the optimal algorithm by exploiting temporal locality.

## What You'll Practice

Given a frame count and a reference string, simulate LRU page replacement and count the total number of page faults.

## How LRU Works

Maintain the set of pages currently in memory. On each reference:
- **Hit:** page is already in memory → no fault, but mark it as most recently used.
- **Miss (page fault):** page is NOT in memory → fault!
  - If frames are available: load the page.
  - If all frames are full: evict the **least recently used** page (the one whose last access was furthest in the past).

## Example Walkthrough

3 frames, reference string: `1 2 3 4 1 2 5 1 2 3 4 5`

```
Ref  Memory (LRU→MRU)   Fault?  Evicted
 1   [1]                  F
 2   [1,2]                F
 3   [1,2,3]              F
 4   [2,3,4]              F      (evict 1, LRU)
 1   [3,4,1]              F      (evict 2, LRU)
 2   [4,1,2]              F      (evict 3, LRU)
 5   [1,2,5]              F      (evict 4, LRU)
 1   [2,5,1]              -      (hit)
 2   [5,1,2]              -      (hit)
 3   [1,2,3]              F      (evict 5, LRU)
 4   [2,3,4]              F      (evict 1, LRU)
 5   [3,4,5]              F      (evict 2, LRU)

Total faults: 10
```

Output: `10`

Now implement LRU page replacement in the coding exercise!
