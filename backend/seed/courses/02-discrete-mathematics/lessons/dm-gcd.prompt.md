# Greatest Common Divisor (Euclid's Algorithm)

## Problem

Given two positive integers `a` and `b`, compute `gcd(a, b)` — the greatest common divisor.

Use Euclid's algorithm:
```
gcd(a, b) = gcd(b, a mod b)   for b != 0
gcd(a, 0) = a
```

## Input Format

A single line with two space-separated positive integers `a` and `b`.

## Output Format

A single integer — `gcd(a, b)`.

## Constraints

- `1 <= a, b <= 10^12`

## Examples

| Input | Output |
|-------|--------|
| `48 18` | `6` |
| `100 75` | `25` |
| `7 13` | `1` |
| `1000000000000 999999999999` | `1` |

## Hint

Implement the algorithm iteratively to avoid potential recursion depth issues for large inputs.
