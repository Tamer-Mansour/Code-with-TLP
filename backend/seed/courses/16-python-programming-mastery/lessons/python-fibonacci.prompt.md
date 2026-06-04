# Fibonacci Sequence

Read a single non-negative integer `N` from standard input. Print the first `N` Fibonacci numbers separated by single spaces on one line.

The Fibonacci sequence is defined as:
- F(0) = 0
- F(1) = 1
- F(n) = F(n-1) + F(n-2) for n ≥ 2

The sequence starts: `0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...`

If `N` is 0, print an empty line.

## Input

A single non-negative integer `N` (0 ≤ N ≤ 30).

## Output

A single line with the first `N` Fibonacci numbers separated by spaces. If N is 0, print an empty line.

## Examples

**Example 1**
```
Input:  8
Output: 0 1 1 2 3 5 8 13
```

**Example 2**
```
Input:  1
Output: 0
```

**Example 3**
```
Input:  0
Output: 
```

## Hints

- Maintain two variables `a` and `b` starting at 0 and 1.
- Each step: append `a`, then update `a, b = b, a + b`.
- Use `' '.join(map(str, result))` to format the output.
- Do **not** use recursion — an iterative approach is expected here.
