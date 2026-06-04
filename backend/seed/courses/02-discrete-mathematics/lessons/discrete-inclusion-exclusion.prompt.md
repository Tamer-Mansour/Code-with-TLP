# Inclusion-Exclusion Counter

## Problem

Given a positive integer `n` and two distinct positive integers `a` and `b`, use the **inclusion-exclusion principle** to count integers in `{1, …, n}` divisible by `a`, by `b`, or by both.

Print four results:
1. Count divisible by `a` only (divisible by a but not by lcm(a,b))
2. Count divisible by `b` only (divisible by b but not by lcm(a,b))
3. Count divisible by both (divisible by lcm(a,b))
4. Count divisible by at least one of a or b

## Input Format

A single line with three space-separated integers: `n a b`.

## Output Format

Four lines:
```
Divisible by <a> only: <count>
Divisible by <b> only: <count>
Divisible by both: <count>
Divisible by at least one: <count>
```

## Constraints

- `1 <= n <= 10^9`
- `1 <= a, b <= 10^6`
- `a != b`

## Examples

| Input | Output |
|-------|--------|
| `30 3 5` | `Divisible by 3 only: 8`<br>`Divisible by 5 only: 4`<br>`Divisible by both: 2`<br>`Divisible by at least one: 14` |
| `20 2 4` | `Divisible by 2 only: 5`<br>`Divisible by 4 only: 0`<br>`Divisible by both: 5`<br>`Divisible by at least one: 10` |
| `100 7 11` | `Divisible by 7 only: 13`<br>`Divisible by 11 only: 8`<br>`Divisible by both: 1`<br>`Divisible by at least one: 22` |

## Key Formula

```
lcm(a, b) = a * b // gcd(a, b)
count_both = n // lcm(a, b)
count_a_only = (n // a) - count_both
count_b_only = (n // b) - count_both
count_either = (n // a) + (n // b) - count_both
```

## Hint

Import `math` and use `math.gcd(a, b)` to compute the GCD. The LCM follows directly.
