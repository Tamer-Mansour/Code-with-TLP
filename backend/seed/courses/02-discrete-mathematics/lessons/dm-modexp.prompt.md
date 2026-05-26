# Modular Exponentiation

## Problem

Given integers `base`, `exp`, and `mod`, compute:

```
(base ^ exp) mod mod
```

Use the **fast modular exponentiation** (repeated squaring) algorithm so that it runs in `O(log exp)` multiplications — never compute `base^exp` directly.

## Input Format

A single line with three space-separated integers: `base exp mod`.

## Output Format

A single integer — `(base ^ exp) % mod`.

## Constraints

- `0 <= base <= 10^9`
- `0 <= exp <= 10^18`
- `1 <= mod <= 10^9`

## Examples

| Input | Output |
|-------|--------|
| `2 10 1000` | `24` |
| `3 5 7` | `5` |
| `2 0 13` | `1` |
| `7 1000000000 1000000007` | `151008985` |

## Hint

The algorithm:
```
result = 1
base = base mod m
while exp > 0:
    if exp is odd: result = (result * base) mod m
    exp = exp // 2
    base = (base * base) mod m
return result
```
