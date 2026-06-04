# Exercise: Pigeonhole Checker

The **Pigeonhole Principle** guarantees existence without constructing an explicit example. Its generalised form states:

> If `n` items are distributed into `k` bins, at least one bin must contain at least `⌈n/k⌉` items.

This follows by contradiction: if every bin held at most `⌈n/k⌉ − 1` items, the total would be at most `k · (⌈n/k⌉ − 1) < n` — impossible since there are `n` items.

## Guaranteeing a Minimum Per Bin

To **guarantee** that some bin contains at least `m` items, you need enough items that even the best-case distribution forces it. In the best case for an adversary, items are spread as evenly as possible:

- Fill each of the `k` bins with `m − 1` items: uses `k · (m−1)` items with no bin reaching `m`.
- Add one more item: it must go somewhere, pushing that bin to `m`.

Therefore the **minimum number of items** needed to guarantee at least one bin has `m` or more is:

```
(m - 1) * k + 1
```

## Classic Applications

| Pigeons | Holes | Conclusion |
|---------|-------|-----------|
| 13 people | 12 months | At least 2 share a birth month |
| n+1 integers from {1,…,n} | n values | At least one is repeated |
| 2^64 hash inputs | 2^64 − 1 hash outputs | A collision must exist |
| Any 5 points in a 2×2 square | 4 unit sub-squares | Two points within √2 of each other |

## Further Reading

- *Discrete Mathematics: An Open Introduction* by Oscar Levin — https://discrete.openmathbooks.org/dmoi4/
- *Mathematics for Computer Science* (MIT) — https://people.csail.mit.edu/meyer/mcs.pdf
