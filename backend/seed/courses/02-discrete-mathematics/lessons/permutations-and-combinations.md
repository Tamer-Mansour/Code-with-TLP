# Permutations and Combinations

When selecting from a collection of objects, the two key questions are: **does order matter?** and **can we repeat selections?** The answers determine which formula to use.

## Permutations (Order Matters, No Repetition)

A **permutation** of `r` objects chosen from `n` distinct objects is an ordered arrangement (sequence) of those r objects. The notation is `P(n, r)` or `nPr`.

```
P(n, r) = n! / (n − r)!  =  n × (n−1) × (n−2) × … × (n−r+1)
```

**Reasoning:** n choices for the first position, `n−1` for the second (one is used), ..., `n−r+1` for the rth. Multiply via the Product Rule.

| n | r | P(n,r) | Calculation |
|---|---|--------|------------|
| 5 | 3 | 60 | 5 × 4 × 3 |
| 8 | 2 | 56 | 8 × 7 |
| 6 | 6 | 720 | 6! |
| 10 | 1 | 10 | 10 |

**Example:** How many ways can 8 runners finish 1st, 2nd, and 3rd? `P(8,3) = 8×7×6 = 336`.

**Example:** How many 3-letter initials (like "A.B.C.") can be formed from 26 distinct letters? `P(26,3) = 26×25×24 = 15,600`.

### Full Permutations

When `r = n`, `P(n,n) = n!`. There are `n!` ways to arrange n distinct objects.

- `5! = 120`: arrangements of {a,b,c,d,e}
- `10! = 3,628,800`: arrangements of 10 items
- `20! ≈ 2.4 × 10^18`: infeasibly large — brute-force search over 20-element permutations is impossible

**CS note:** Permutations arise in sorting (how many orderings to consider?), scheduling (job order), and password generation (no-repeat passwords).

### Permutations with Repeated Elements

If the n objects are **not** all distinct (some appear multiple times), the full permutations formula overcounts. If object type i appears `kᵢ` times:
```
Permutations = n! / (k₁! × k₂! × … × kₘ!)
```

**Example:** How many distinct arrangements of "MISSISSIPPI" (4 S, 4 I, 2 P, 1 M)?
```
11! / (4! × 4! × 2! × 1!) = 39,916,800 / (24 × 24 × 2 × 1) = 34,650
```

**Example:** How many bit strings of length 8 have exactly three 1s?
```
8! / (3! × 5!) = C(8, 3) = 56
```
This connects permutations with repetition directly to combinations.

## Combinations (Order Doesn't Matter, No Repetition)

A **combination** is an unordered selection of r objects from n distinct objects. Written `C(n, r)`, `nCr`, or `(n choose r)`:

```
C(n, r) = n! / (r! × (n−r)!)
```

**Reasoning:** Start with `P(n,r) = n!/(n−r)!` ordered arrangements. Each unordered set of r items was counted `r!` times (once per permutation of those r items). Divide to eliminate over-counting.

| n | r | C(n,r) | Calculation |
|---|---|--------|------------|
| 5 | 2 | 10 | 5!/(2!3!) |
| 10 | 3 | 120 | 10!/(3!7!) |
| 6 | 0 | 1 | Exactly one empty selection |
| 7 | 7 | 1 | Select all — only one way |
| 52 | 5 | 2,598,960 | Poker hands |

**Example:** From 10 students, choose a committee of 3: `C(10,3) = 120`.

**Example:** How many ways to choose 2 endpoints for an edge in a graph on n vertices? `C(n,2) = n(n−1)/2`. This is exactly why `K_n` has `n(n−1)/2` edges.

### Symmetry Property

```
C(n, r) = C(n, n−r)
```

Choosing r items to **include** is the same as choosing `n−r` items to **exclude**. This is often the fastest computational shortcut: use `C(n, min(r, n−r))`.

**Example:** `C(100, 97) = C(100, 3) = 161,700`. Far easier to compute with r=3 than r=97.

### Pascal's Recurrence

Combinations satisfy the recurrence:
```
C(n, r) = C(n−1, r−1) + C(n−1, r)
```

**Combinatorial proof:** When choosing r items from `{a₁, …, aₙ}`, either:
- We **include** `aₙ`: choose the remaining `r−1` from the other `n−1` items → `C(n−1, r−1)`.
- We **exclude** `aₙ`: choose all r from the other `n−1` items → `C(n−1, r)`.

This recurrence generates Pascal's Triangle:
```
        C(0,0) = 1
     C(1,0) C(1,1) = 1 1
  C(2,0) C(2,1) C(2,2) = 1 2 1
1 3 3 1
1 4 6 4 1
1 5 10 10 5 1
```

Each entry is the sum of the two directly above it. Row n lists `C(n,0), C(n,1), …, C(n,n)`.

## Permutations with Repetition

If we **can** reuse objects, an ordered sequence of length r from n types:
```
n^r
```

**Example:** 4-digit PINs from `{0,…,9}` with repetition: `10^4 = 10,000`.

**Example:** Counting all n-bit strings: `2^n`.

## Combinations with Repetition (Stars and Bars)

Choosing r items from n types where repetition is allowed (order doesn't matter) — how many multisets of size r can be formed from n types?
```
C(n + r − 1, r)
```

**Stars and Bars argument:** Represent r selections as `r` stars and use `n−1` bars to separate the n types. You need to arrange `r + (n−1)` symbols, choosing which `r` positions are stars:
```
C(r + n − 1, r) = C(n + r − 1, n − 1)
```

**Example:** Choose 3 scoops from 5 ice cream flavors (repeats allowed):
`C(5+3−1, 3) = C(7,3) = 35`

**Example:** How many ways to distribute 10 identical balls among 4 distinct boxes?
`C(10+4−1, 10) = C(13, 10) = C(13, 3) = 286`

**CS application:** Counting multisets of size k from an n-character alphabet — e.g., how many 5-word "bags" can be formed from a vocabulary of 1000 words? `C(1004, 5)`.

## Summary Table

| Repetition? | Order matters? | Count |
|-------------|---------------|-------|
| No | Yes | `P(n,r) = n!/(n−r)!` |
| No | No | `C(n,r) = n!/(r!(n−r)!)` |
| Yes | Yes | `n^r` |
| Yes | No | `C(n+r−1, r)` |

## Worked Example — Lottery Analysis

A lottery draws 6 numbers from {1, …, 49} without repetition; order doesn't matter.

- Total tickets: `C(49,6) = 13,983,816` — about 14 million possible outcomes.
- Probability of winning with one ticket: `1/13,983,816 ≈ 7 × 10⁻⁸`.

If a player buys 10 tickets, the probability of winning is approximately `10 / 13,983,816` — still tiny, illustrating why lottery odds are calculated purely mathematically.

## The Key Insight

Always ask yourself: "Does **order** matter here?" before writing any formula.

- Arranging books on a shelf: order matters → permutation.
- Choosing a committee: order doesn't matter → combination.
- Combination lock (despite the name): order matters → permutation (it should be called a "permutation lock"!).
