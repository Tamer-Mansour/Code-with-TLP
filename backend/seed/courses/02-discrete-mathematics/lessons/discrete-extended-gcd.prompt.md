# Extended Euclidean GCD

## Problem

Given two positive integers `a` and `b`, use the **Extended Euclidean Algorithm** to find:

1. `gcd(a, b)`
2. Integers `x` and `y` satisfying **Bezout's identity**: `a·x + b·y = gcd(a, b)`

## Input Format

A single line with two space-separated positive integers: `a b`.

## Output Format

Two lines:
- Line 1: `gcd(a, b)`
- Line 2: `x y` (space-separated)

Note: there are infinitely many Bezout coefficient pairs; output the unique pair returned by the standard recursive extended Euclidean algorithm.

## Constraints

- `1 <= a, b <= 10^9`

## Examples

| Input | Output |
|-------|--------|
| `35 15` | `5`<br>`1 -2` |
| `48 18` | `6`<br>`-1 3` |
| `7 13` | `1`<br>`2 -1` |

## Verification

You can verify your answer: compute `a*x + b*y` and check that it equals the gcd you output.

## Algorithm

```
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1
```

## Hint

The recursive structure mirrors the standard Euclidean algorithm. At each level, update coefficients so that the Bezout identity remains satisfied for the current `(a, b)` pair.
