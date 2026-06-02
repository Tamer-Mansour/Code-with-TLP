# Prompt: Transform and Reduce a Numeric Stream

## Problem Statement

Given a list of N integers and a threshold K, compute the **sum of the squares** of all integers whose square is **strictly greater than K**.

## Input Format

```
N K
a1 a2 ... aN
```

- Line 1: two integers `N` and `K` separated by a space.
  - `1 ≤ N ≤ 1000`
  - `0 ≤ K ≤ 1,000,000`
- Line 2: `N` space-separated integers, each in the range `[-1000, 1000]`.

## Output Format

A single integer on its own line: the sum of all `a_i^2` where `a_i^2 > K`.

If no square is greater than K, output `0`.

## Constraints

- All arithmetic fits in a 32-bit signed integer (max sum ≤ 1000 × 1,000,000 = 10^9 < 2^31 − 1).
- No external libraries permitted; use only the standard library / built-ins.
- Read from stdin, write to stdout.

## Sample

**Input**
```
6 10
-3 1 4 -1 5 2
```

**Output**
```
41
```

**Explanation**
- Squares: 9, 1, 16, 1, 25, 4
- Squares > 10: 16, 25
- Sum: 41

## Additional Sample

**Input**
```
4 100
3 5 7 10
```

**Output**
```
0
```

**Explanation**
- Squares: 9, 25, 49, 100
- None is strictly greater than 100.
- Sum: 0
