# Amdahl's Law Calculator

## Problem Statement

Given multiple test cases, compute the overall system speedup using Amdahl's Law for each case.

Amdahl's Law:

```
Speedup = 1 / ((1 - p) + p / s)
```

Where:
- `p` is the fraction of execution time that is improved (0.0 <= p <= 1.0)
- `s` is the speedup factor applied to that fraction (s >= 1.0)

## Input Format

```
n
p1 s1
p2 s2
...
pn sn
```

- Line 1: a single integer `n` (1 <= n <= 100), the number of test cases.
- The next `n` lines each contain two space-separated floating-point numbers `p` and `s`.
  - `0.0 <= p <= 1.0`
  - `1.0 <= s <= 1000000.0`

## Output Format

Print exactly `n` lines. Each line contains the overall speedup for the corresponding test case, rounded to **exactly 4 decimal places**.

## Constraints

- 1 <= n <= 100
- 0.0 <= p <= 1.0
- 1.0 <= s <= 1000000.0
- All inputs are valid floats.
- Use only the Python standard library (no numpy, no scipy).

## Sample Input

```
3
0.70 8
0.90 16
0.50 2
```

## Sample Output

```
2.5806
6.4000
1.3333
```

## Explanation

- Case 1: `1 / (0.30 + 0.70/8) = 1 / 0.3875 = 2.5806`
- Case 2: `1 / (0.10 + 0.90/16) = 1 / 0.15625 = 6.4000`
- Case 3: `1 / (0.50 + 0.50/2) = 1 / 0.75 = 1.3333`

## Edge Cases

- When `p = 0.0`, the entire execution is serial: speedup = 1.0000.
- When `p = 1.0`, the entire execution is improved: speedup = s.
- When `s = 1.0`, no improvement occurs: speedup = 1.0000.
