# Binary Search

Read three lines from standard input:

1. **Line 1:** An integer `N` — the count of sorted integers.
2. **Line 2:** `N` space-separated integers in **ascending sorted order**.
3. **Line 3:** A target integer to search for.

Print the **0-based index** of the target if found, or `-1` if not found.

You MUST implement binary search — a linear scan will not receive credit.

## Input format

```
N
num_0 num_1 ... num_{N-1}
target
```

## Output format

A single integer: the index of `target`, or `-1`.

## Example

**Input:**
```
7
2 5 8 12 16 23 38
23
```

**Output:**
```
5
```

**Input:**
```
5
1 3 5 7 9
4
```

**Output:**
```
-1
```

## Constraints

- 1 ≤ N ≤ 10000
- All elements are distinct integers
- The list is guaranteed to be sorted in ascending order
- Your solution must implement binary search: O(log N) comparisons
