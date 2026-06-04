# Factorial via Recursion

Read a single non-negative integer **N** from standard input.

Compute and print **N!** (N factorial) using a **recursive function**.

- 0! = 1 (by definition)
- N! = N × (N − 1)! for N ≥ 1

N is guaranteed to be between 0 and 12 inclusive.

## Input format

A single integer `N` (0 ≤ N ≤ 12).

## Output format

A single integer: the value of N!.

## Examples

**Input:**
```
6
```
**Output:**
```
720
```

**Input:**
```
0
```
**Output:**
```
1
```

## Constraints

- Your solution MUST use a recursive function (a function that calls itself).
- You may NOT use `math.factorial` or any import.
- N ≤ 12, so overflow is not a concern in Python.
