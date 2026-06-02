# Prompt: Simulate LRU Page Replacement and Count Faults

## Problem Description

Simulate the **LRU (Least Recently Used)** page replacement algorithm on a given reference string and report the total number of page faults.

### Rules

- A **page fault** occurs when the referenced page is not in any frame.
- On a fault with free frames: load the page (no eviction).
- On a fault with a full frame set: evict the page that was accessed least recently (oldest last-use time), then load the new page.
- A **hit** occurs when the referenced page is already in memory. No fault is counted, but the page's recency is updated — it becomes the most recently used page.

## Input Format

```
Line 1: f          (integer, number of frames, 1 ≤ f ≤ 10)
Line 2: p1 p2 ...  (space-separated page numbers, 1 ≤ pi ≤ 100, 1 ≤ length ≤ 50)
```

## Output Format

```
<integer>
```

A single integer: the total number of page faults.

## Constraints

- `1 ≤ f ≤ 10`
- `1 ≤ number of pages in reference string ≤ 50`
- `1 ≤ page number ≤ 100`
- Tie-breaking (two pages last used at the same step) will not appear in test cases.

## Sample Input 1

```
3
7 0 1 2 0 3 0 4 2 3 0 3
```

## Sample Output 1

```
8
```

## Sample Input 2

```
4
7 0 1 2 0 3 0 4 2 3 0 3
```

## Sample Output 2

```
6
```

## Sample Input 3

```
2
1 2 3 1 2 3
```

## Sample Output 3

```
6
```

*(With only 2 frames and a 3-page cycle, every reference is a fault.)*

## Sample Input 4

```
3
1 2 3 1 2 3
```

## Sample Output 4

```
3
```

*(With 3 frames, all 3 pages fit after the first 3 faults; subsequent references are all hits.)*

## Notes for Implementers

- Use `collections.OrderedDict` with `move_to_end` for O(1) LRU tracking.
- On a fault, call `popitem(last=False)` to remove the LRU entry (front of the ordered dict).
- On a hit, call `move_to_end(page)` to mark it as most recently used.
- Do NOT forget to update recency on hits — this is the key difference from FIFO.
