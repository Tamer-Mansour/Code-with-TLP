# Exercise: Compute Speedup with Amdahl's Law

In this exercise you will implement Amdahl's Law calculator that takes a parallel fraction and a speedup factor, then outputs the overall speedup rounded to four decimal places.

## Background

Amdahl's Law gives the theoretical maximum speedup for a system when only part of it is improved:

```
Speedup = 1 / ((1 - p) + p / s)
```

Where:
- `p` is the fraction of execution time that benefits from the improvement (0.0 to 1.0)
- `s` is the speedup factor applied to that fraction (s >= 1.0)

## What You Will Implement

Read multiple test cases from standard input. For each case, compute the overall speedup using Amdahl's Law and print it rounded to **4 decimal places**.

Your solution must handle edge cases correctly:
- When `p = 0.0`, the speedup is always 1.0000 regardless of `s`.
- When `p = 1.0`, the speedup equals `s`.
- When `s = 1.0`, the speedup is always 1.0000 regardless of `p`.

## Input Format

- Line 1: integer `n` — the number of test cases.
- Next `n` lines: two space-separated floats `p s` on each line.

## Output Format

For each test case, print the overall speedup on its own line, rounded to exactly 4 decimal places.

## Sample

**Input:**
```
3
0.70 8
0.90 16
0.50 2
```

**Output:**
```
2.5806
6.4000
1.3333
```

## Starter Code

```python
import sys

def amdahl(p, s):
    # TODO: implement Amdahl's Law
    pass

def solve():
    data = sys.stdin.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    for _ in range(n):
        p = float(data[idx]); idx += 1
        s = float(data[idx]); idx += 1
        result = amdahl(p, s)
        # TODO: print result rounded to 4 decimal places
    
solve()
```

Complete the `amdahl` function and the print statement. Use only the Python standard library.
