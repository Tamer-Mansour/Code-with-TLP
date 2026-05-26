# Pigeonhole Principle and the Binomial Theorem

## The Pigeonhole Principle

**Basic form:** If `n+1` or more objects (pigeons) are distributed among `n` containers (holes), then at least one container must hold 2 or more objects.

**Formal statement:** If `f: A → B` is a function with `|A| > |B|`, then f is not injective — at least two elements of A map to the same element of B.

The proof is by contradiction: if every hole held at most 1 pigeon, the total number of pigeons would be at most `n < n+1` — contradiction.

### Simple Examples

| Pigeons | Holes | Conclusion |
|---------|-------|-----------|
| 13 people | 12 months | At least 2 share a birth month |
| 27 English words | 26 first letters | At least 2 share the same first letter |
| 5 integers | 4 remainders mod 4 | At least 2 have the same remainder |
| n+1 integers from {1,…,n} | n possible values | At least one value is repeated |

### Generalized Pigeonhole Principle

If n items are distributed among k boxes, at least one box contains **at least** `⌈n/k⌉` items:
```
At least one box has ≥ ⌈n/k⌉ items
```

**Proof:** If every box had at most `⌈n/k⌉ − 1` items, the total would be at most `k · (⌈n/k⌉ − 1) < k · (n/k) = n` — a contradiction since there are n items.

**Example:** Among 100 people, at least `⌈100/12⌉ = 9` were born in the same month.

**Example:** Among 500 items hashed into a table of 100 buckets, at least one bucket holds `⌈500/100⌉ = 5` items.

### Non-Trivial Applications

**Geometry example:** Among any 5 points chosen inside (or on) a 2×2 square, some two points are within `√2` of each other.

*Proof:* Divide the square into 4 unit sub-squares (the "holes"). With 5 points (the "pigeons"), by the Pigeonhole Principle, some unit square contains at least 2 points. The maximum distance within a unit square is its diagonal `√2`. QED.

**Sequence example (Erdős–Szekeres):** Every sequence of more than `(r−1)(s−1)` distinct integers contains either an increasing subsequence of length r or a decreasing subsequence of length s.

*Sketch for r=s=3 (total > 4 numbers):* Assign each element a pair `(i, d)` where i is the length of the longest increasing subsequence ending there, and d is the longest decreasing. If no increasing subsequence reaches 3 and no decreasing one reaches 3, then all pairs are in `{1,2}×{1,2}` — only 4 distinct pairs for 5 elements, so two elements share the same pair, which leads to a contradiction.

**CS — Birthday Attack in Cryptography:**

A hash function produces h-bit digests. The birthday paradox says: with approximately `√(2^h) = 2^(h/2)` random inputs, you have a 50% chance of finding a collision (two inputs with the same hash). For MD5 (128-bit): `2^64 ≈ 1.8 × 10^19` attempts suffice — feasible with distributed computing, which is why MD5 is broken for security use.

**CS — Compression:** The Pigeonhole Principle proves that no compression algorithm can compress every input. If a compressor maps all n-bit strings to shorter strings, its outputs form a set of size less than `2^n`, but the inputs number exactly `2^n` — a collision is inevitable.

## The Binomial Theorem

The **Binomial Theorem** gives the expansion of `(x + y)^n` for non-negative integer n:

```
(x + y)^n = Σ(k=0 to n) C(n,k) · x^(n−k) · y^k
```

The coefficients `C(n,k)` are called **binomial coefficients** — exactly the entries of Pascal's Triangle (row n).

### Combinatorial Derivation

Why does `C(n,k)` appear as the coefficient of `x^(n−k) y^k`?

When you expand `(x+y)^n = (x+y)(x+y)⋯(x+y)` (n factors), you choose either `x` or `y` from each factor. A term `x^(n−k) y^k` arises when you pick `y` from exactly k of the n factors. The number of ways to choose which k factors contribute `y` is `C(n,k)`.

### Worked Expansion

```
(x + y)^4 = C(4,0)x⁴ + C(4,1)x³y + C(4,2)x²y² + C(4,3)xy³ + C(4,4)y⁴
           = x⁴ + 4x³y + 6x²y²+ 4xy³ + y⁴
```

**Verify with specific values:** Set `x = y = 1`: `(1+1)^4 = 16 = 1+4+6+4+1`. ✓

### Key Special Cases

**Setting `x = y = 1`:**
```
2^n = Σ(k=0 to n) C(n,k)
```
The sum of all binomial coefficients in row n equals `2^n` — the number of subsets of an n-element set.

**Setting `x = 1, y = −1`:**
```
0 = Σ(k=0 to n) (−1)^k · C(n,k)     for n ≥ 1
```
The alternating sum is 0: the even-indexed binomial coefficients sum to the same value as the odd-indexed ones. This identity is used in inclusion-exclusion proofs and generating functions.

**Setting `x = 1, y = 2`:**
```
3^n = Σ(k=0 to n) C(n,k) · 2^k
```
This counts the number of functions from an n-element set to {choice-for-x, choice-for-2y-possibilities} — a combinatorial interpretation.

### Pascal's Triangle Identities

From the Binomial Theorem one can derive many identities:

| Identity | Formula | Meaning |
|----------|---------|---------|
| Row sum | `Σ C(n,k) = 2^n` | Subsets of an n-set |
| Alternating | `Σ (−1)^k C(n,k) = 0` | |
| Vandermonde | `C(m+n, r) = Σ C(m,k)C(n,r−k)` | Selecting from two groups |
| Hockey stick | `Σ(i=r to n) C(i,r) = C(n+1,r+1)` | Diagonal sum in Pascal's Triangle |
| Symmetry | `C(n,k) = C(n,n−k)` | |

### Multinomial Coefficients (Extension)

Extending to more than 2 terms:
```
(x₁ + x₂ + … + xₘ)^n = Σ  [n! / (k₁! k₂! … kₘ!)] · x₁^k₁ · x₂^k₂ · … · xₘ^kₘ
```
where the sum is over all non-negative integer tuples `(k₁,…,kₘ)` with `k₁ + k₂ + … + kₘ = n`.

The coefficient `n! / (k₁! k₂! … kₘ!)` is the **multinomial coefficient**, counting the number of ways to arrange n objects where type i appears `kᵢ` times.

**Example:** `(a+b+c)^2 = a² + b² + c² + 2ab + 2ac + 2bc`. The coefficient of `ab` is `2!/(1!1!0!) = 2`.

**Application:** Multinomial coefficients count rearrangements of strings — e.g., "MISSISSIPPI" has `11!/(4!4!2!1!) = 34,650` distinct arrangements.

## Summary

| Topic | Key formula |
|-------|------------|
| Pigeonhole (basic) | n+1 items, n boxes ⟹ some box has ≥ 2 |
| Pigeonhole (generalized) | n items, k boxes ⟹ some box has ≥ ⌈n/k⌉ |
| Binomial theorem | `(x+y)^n = Σ C(n,k) x^(n−k) y^k` |
| Sum of row n | `Σ C(n,k) = 2^n` |
| Alternating sum | `Σ (−1)^k C(n,k) = 0` (n ≥ 1) |

The Pigeonhole Principle appears in proving the existence of hash collisions (birthday attacks), impossibility of universal compression, and many elegant combinatorial existence proofs. The Binomial Theorem is foundational to probability generating functions and polynomial identities used throughout algorithm analysis.
