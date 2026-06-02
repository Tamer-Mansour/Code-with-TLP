# Prompt: Simulate FIFO Page Replacement and Count Faults

## Problem Description

Simulate the **FIFO (First-In, First-Out)** page replacement algorithm on a given reference string and report the total number of page faults.

### Rules

- A **page fault** occurs when the referenced page is not in any frame.
- On a fault with a full frame set: evict the page loaded earliest (longest in memory).
- On a fault with free frames: simply load the page — no eviction needed.
- A reference to a page already in memory is a **hit** (no fault, no queue change).

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
- No blank lines in input.

## Sample Input 1

```
3
1 2 3 4 1 2 5 1 2 3 4 5
```

## Sample Output 1

```
9
```

## Sample Input 2

```
4
1 2 3 4 1 2 5 1 2 3 4 5
```

## Sample Output 2

```
10
```

*(This is the classic Belady's anomaly example — more frames, more faults with FIFO.)*

## Sample Input 3

```
1
7 7 7 7 7
```

## Sample Output 3

```
1
```

*(Only the very first reference faults; all subsequent are hits.)*

## Notes for Implementers

- Use a `collections.deque` for O(1) enqueue/dequeue and a `set` for O(1) membership testing.
- The queue and the set must always stay in sync.
- Do not reset a page's queue position when it is accessed as a hit.
