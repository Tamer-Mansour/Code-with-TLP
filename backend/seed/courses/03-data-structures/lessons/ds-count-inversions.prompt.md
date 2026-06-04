# Count Inversions

Given an array of integers, count the number of **inversions**: pairs (i, j) where i < j and A[i] > A[j].

## Input Format

- Line 1: N — number of integers (1 ≤ N ≤ 100000)
- Line 2: N space-separated integers (−10⁹ ≤ each ≤ 10⁹)

## Output Format

Print a single integer — the total number of inversions.

## Examples

**Example 1:**
```
Input:
5
3 1 2 5 4

Output:
3
```
Inversions: (3,1), (3,2), (5,4).

**Example 2:**
```
Input:
4
4 3 2 1

Output:
6
```
All 6 pairs are inverted (fully reverse-sorted array).

**Example 3:**
```
Input:
4
1 2 3 4

Output:
0
```
Already sorted — no inversions.

## Constraints

- Your solution must run in O(n log n) time
- Do not use Python's built-in `sort` or `sorted` (implement the merge yourself)

## Hint

Augment merge sort: during the merge step, every time you take an element from the **right** half before the remaining elements in the **left** half, add `len(left) - i` to your inversion count (where `i` is the current left pointer). This counts all inversions between the left and right halves in O(n) per merge.
