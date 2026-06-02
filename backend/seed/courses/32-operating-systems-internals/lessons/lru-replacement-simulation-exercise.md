# Exercise: Simulate LRU Page Replacement and Count Faults

In this exercise you will implement the **LRU (Least Recently Used)** page replacement algorithm and count the total number of page faults for a given reference string and frame count.

## What You Will Implement

You are given:
- A number of frames `f` (physical memory capacity in pages).
- A reference string of page numbers.

Your program must simulate exact LRU page replacement and output the total number of page faults.

**LRU rule:** when a page fault occurs and all frames are full, evict the page whose most recent access is the oldest (i.e., the page that has been unused for the longest time).

On a **hit** (page already in memory): update that page's "last used" timestamp — it is now the most recently used page.

On a **fault**: load the new page and record its timestamp. If frames are full, evict the page with the smallest timestamp first.

## Skills Practiced

- `OrderedDict` or counter-based LRU tracking
- Distinguishing hit (update recency) vs. fault (evict + load)
- Comparing LRU performance to FIFO on the same inputs

## Key Insight

LRU exploits **temporal locality**: pages used recently are likely to be used again soon. Unlike FIFO, a hit on a page moves it to the "most recently used" position, protecting it from near-term eviction.

## Getting Started

Read frames count and reference string from stdin, output a single integer.

## Sample Trace (3 frames)

```
Reference: 7 0 1 2 0 3 0 4 2 3 0 3
Frames:    3

Step  Frames [oldest→newest by LRU]  Fault?
  1   [7]                             YES
  2   [7,0]                           YES
  3   [7,0,1]                         YES
  4   [0,1,2]   evict 7               YES
  5   [1,2,0]   hit 0, move to front  NO
  6   [2,0,3]   evict 1               YES
  7   [2,3,0]   hit 0, move to front  NO
  8   [3,0,4]   evict 2               YES
  9   [0,4,2]   evict 3               YES
 10   [4,2,3]   evict 0               YES
 11   [2,3,0]   evict 4               YES
 12   [2,0,3]   hit 3, move to front  NO

Total faults: 8
```
