# C(n, r) — Combinations

## Problem

Given two non-negative integers `n` and `r` (with `0 <= r <= n`), compute the binomial coefficient:

```
C(n, r) = n! / (r! * (n-r)!)
```

This is the number of ways to choose `r` items from a set of `n` distinct items when order does not matter.

## Input Format

A single line containing two space-separated integers: `n` and `r`.

## Output Format

A single integer — the value of `C(n, r)`.

## Constraints

- `0 <= r <= n <= 60`

## Examples

| Input | Output |
|-------|--------|
| `5 2` | `10` |
| `10 0` | `1` |
| `6 3` | `20` |
| `20 10` | `184756` |

## Hint

Use Pascal's recurrence `C(n,r) = C(n-1,r-1) + C(n-1,r)` with memoization, or compute directly using integer arithmetic and the `math.comb` function (Python 3.8+), or implement integer factorial division carefully to avoid floating point.
