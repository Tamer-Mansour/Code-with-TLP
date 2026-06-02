# Exercise: Transform and Reduce a Numeric Stream

In this exercise you will practice the core ideas from this module — iterating over a sequence, applying a mapping transformation, filtering by a predicate, and reducing to a single result — using only the standard library.

## What You Will Implement

You are given a list of integers. Your task is to:

1. **Square** each integer.
2. **Keep** only the squares that are strictly greater than a given threshold `K`.
3. **Sum** the remaining squares.

This mirrors the `transform → filter → accumulate` pattern that appears constantly in real systems code (processing sensor readings, pipeline stages, numeric analytics).

## Input Format

```
N K
a1 a2 ... aN
```

- First line: two integers `N` (count of numbers, 1 ≤ N ≤ 1000) and `K` (threshold, 0 ≤ K ≤ 10^6).
- Second line: N space-separated integers, each in the range [-1000, 1000].

## Output Format

A single integer: the sum of squares greater than K. If no square exceeds K, output `0`.

## Sample

**Input**
```
6 10
-3 1 4 -1 5 2
```

**Step-by-step**
- Squares: 9, 1, 16, 1, 25, 4
- Squares > 10: 16, 25
- Sum: 41

**Output**
```
41
```

## Starter Code (Python)

```python
def solve():
    import sys
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1])
    nums = [int(x) for x in data[2:2+n]]
    # TODO: square each number, keep those > k, sum the rest
    print(0)

solve()
```

## Hints

- Use a list comprehension or `map()` for the transformation step.
- Combine the filter and sum in one pass: `sum(x*x for x in nums if x*x > k)`.
- No external libraries needed.
- Think about whether negative inputs affect the result (they do not, because squaring makes them positive).
