# Exercise: Inclusion-Exclusion Counter

The **inclusion-exclusion principle** is a counting technique for unions of overlapping sets. Its two-set form states:

```
|A ∪ B| = |A| + |B| − |A ∩ B|
```

The subtraction corrects for double-counting: elements that belong to both A and B are added once in `|A|`, added again in `|B|`, then subtracted once to give a net count of one.

**Critical pitfall:** `|A ∪ B| ≠ |A| + |B|` unless A and B are disjoint. Forgetting to subtract `|A ∩ B|` is the most common inclusion-exclusion error.

## Application: Counting Multiples

To count integers in `{1, …, n}` divisible by `a` or `b`:

- `|A|` = `⌊n/a⌋` (multiples of a)
- `|B|` = `⌊n/b⌋` (multiples of b)
- `|A ∩ B|` = `⌊n/lcm(a,b)⌋` (multiples of both = multiples of lcm)
- `|A ∪ B|` = `|A| + |B| − |A ∩ B|`

Where `lcm(a, b) = a * b // gcd(a, b)`.

## Python Snippet

```python
import math
lcm = a * b // math.gcd(a, b)
count_a = n // a
count_b = n // b
count_both = n // lcm
count_either = count_a + count_b - count_both
```

## Three-Set Extension

For three sets: `|A ∪ B ∪ C| = |A| + |B| + |C| − |A∩B| − |A∩C| − |B∩C| + |A∩B∩C|`.

The alternating sign pattern (add singles, subtract pairs, add triples, …) generalises to any number of sets and is fundamental to combinatorics, probability, and compiler register allocation.

## Further Reading

- *Discrete Mathematics: An Open Introduction* by Oscar Levin — Section 1.1 on counting: https://discrete.openmathbooks.org/dmoi4/
- *Book of Proof* by Richard Hammack — https://richardhammack.github.io/BookOfProof/
