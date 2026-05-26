# FIFO Page Replacement

Simulate the **FIFO (First-In, First-Out)** page replacement algorithm and output the total number of page faults.

In FIFO, when a page fault occurs and all frames are full, the page that has been in memory the **longest** (arrived earliest) is evicted.

## Input Format

- Line 1: two integers `f` and `n` — the number of frames and the number of page references.
- Line 2: `n` space-separated integers representing the page reference string.

## Output Format

Print a single integer: the total number of **page faults**.

## Constraints

- `1 <= f <= 10`
- `1 <= n <= 100`
- `0 <= page number <= 9`

## Examples

**Example 1**
```
Input:
3 12
1 2 3 4 1 2 5 1 2 3 4 5

Output:
9
```

**Example 2**
```
Input:
2 6
1 2 1 3 1 2

Output:
5
```

Explanation:
- ref=1: FAULT [1]
- ref=2: FAULT [1,2]
- ref=1: HIT
- ref=3: FAULT [2,3] (evict 1)
- ref=1: FAULT [3,1] (evict 2)
- ref=2: FAULT [1,2] (evict 3)

Total: 5 faults.
