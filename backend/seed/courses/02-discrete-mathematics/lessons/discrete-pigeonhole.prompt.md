# Pigeonhole Checker

## Problem

Given `n` items placed into `k` bins and a target threshold `m`, compute three quantities using the Pigeonhole Principle:

1. **Guaranteed max in one bin:** The minimum guaranteed maximum number of items in any single bin — this is `⌈n/k⌉`.
2. **More than one check:** Whether we can guarantee at least one bin has strictly more than 1 item (`yes` if `n > k`, `no` otherwise).
3. **Items for threshold:** The minimum number of items needed to guarantee at least one bin has at least `m` items — this is `(m − 1) * k + 1`.

## Input Format

A single line with three space-separated integers: `n k m`.

## Output Format

Three lines:
```
Guaranteed max in one bin: <value>
At least one bin has more than 1 item: <yes|no>
Items needed to guarantee at least <m> per bin: <value>
```

## Constraints

- `1 <= n <= 10^9`
- `1 <= k <= 10^6`
- `1 <= m <= 10^6`

## Examples

| Input | Output |
|-------|--------|
| `10 3 3` | `Guaranteed max in one bin: 4`<br>`At least one bin has more than 1 item: yes`<br>`Items needed to guarantee at least 3 per bin: 7` |
| `5 5 2` | `Guaranteed max in one bin: 1`<br>`At least one bin has more than 1 item: no`<br>`Items needed to guarantee at least 2 per bin: 6` |
| `100 12 9` | `Guaranteed max in one bin: 9`<br>`At least one bin has more than 1 item: yes`<br>`Items needed to guarantee at least 9 per bin: 97` |

## Key Formulas

```python
import math
guaranteed_max = math.ceil(n / k)
more_than_one  = 'yes' if n > k else 'no'
min_for_m      = (m - 1) * k + 1
```

## Hint

Use `math.ceil` for the ceiling division. The formula `(m-1)*k + 1` is the worst-case-plus-one counting argument.
