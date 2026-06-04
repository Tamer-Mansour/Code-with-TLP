# FIFO vs LRU Page Replacement Simulator

## Problem Description

Given a sequence of page references and a fixed number of physical frames, compute the number of page faults produced by both the **FIFO** and **LRU** page replacement algorithms and print the results.

### FIFO Rules

- On a page fault with free frames: load the page.
- On a page fault with a full frame set: evict the page loaded earliest (the one that has been in memory the longest).
- A hit does **not** change any page's position in the FIFO queue.

### LRU Rules

- On a page fault with free frames: load the page.
- On a page fault with a full frame set: evict the page whose last access was furthest in the past.
- A **hit** updates the page's recency — it becomes the most recently used page.

## Input Format

```
Line 1: f          (integer, number of frames, 1 <= f <= 10)
Line 2: p1 p2 ...  (space-separated page numbers, integers)
```

## Output Format

```
FIFO page faults: <integer>
LRU page faults: <integer>
```

## Constraints

- `1 <= f <= 10`
- `1 <= number of pages in reference string <= 60`
- `0 <= page number <= 100`
- No tie-breaking ambiguity will appear in the LRU test cases.

## Sample Input 1

```
3
7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1
```

## Sample Output 1

```
FIFO page faults: 15
LRU page faults: 12
```

## Sample Input 2

```
4
1 2 3 4 5 1 2 3 4 5
```

## Sample Output 2

```
FIFO page faults: 10
LRU page faults: 10
```

*(On a pure cyclic scan with exactly as many frames as unique pages minus one, both algorithms perform equally.)*

## Sample Input 3

```
3
1 2 3 4 1 2 5 1 2 3 4 5
```

## Sample Output 3

```
FIFO page faults: 9
LRU page faults: 10
```

*(This is the classic Belady's anomaly example in reverse — with 3 frames, FIFO happens to be 9 while LRU is 10 on this particular string. Note LRU is NOT always better.)*

## Notes for Implementers

- For FIFO: use `collections.deque` and a `set`. Enqueue on load; dequeue-left on eviction.
- For LRU: use `collections.OrderedDict`. On a hit call `move_to_end(page)`; on a fault call `popitem(last=False)` to remove the LRU entry before inserting the new page.
- Both simulations are **independent** — run them on the same input separately.
