# LRU Page Replacement

Simulate **Least Recently Used (LRU)** page replacement and count the total number of page faults.

## Input

```
F N
p1 p2 ... pN
```

- First line: two integers F (1 ≤ F ≤ 10, number of frames) and N (1 ≤ N ≤ 100, number of page references).
- Second line: N space-separated page numbers (1 ≤ page ≤ 50).

## Output

Print a single integer: the total number of page faults.

## Rules

- Initially all frames are empty.
- On each reference: if the page is NOT in any frame, it is a **page fault**.
  - If a free frame exists, load the page there.
  - If all frames are full, evict the page that was accessed **least recently** (i.e., the one whose last use was furthest in the past).
- A reference to a page already in memory is a **hit** (no fault), but update its recency.

## Examples

**Example 1**
```
Input:
3 12
1 2 3 4 1 2 5 1 2 3 4 5

Output:
10
```

**Example 2**
```
Input:
2 6
1 2 1 3 1 2

Output:
4
```
*Explanation:* 1(F), 2(F), 1(hit), 3(F,evict 2), 1(hit), 2(F,evict 3) → 4 faults.

**Example 3**
```
Input:
1 4
1 2 3 4

Output:
4
```
*Explanation:* With 1 frame, every distinct page causes a fault.

## Constraints

- Page numbers are positive integers.
- Output exactly one integer.
