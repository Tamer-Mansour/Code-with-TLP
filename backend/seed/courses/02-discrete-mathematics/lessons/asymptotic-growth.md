# Asymptotic Growth and Big-O Notation

When analyzing algorithms, we care about how running time **scales** with input size — not the exact count on a specific machine. **Asymptotic notation** captures the dominant behavior as `n → ∞`, abstracting away hardware constants and lower-order terms.

## Big-O: Upper Bound

`f(n) = O(g(n))` means f grows **no faster** than g (up to a constant factor and beyond some threshold).

**Formal definition:** There exist constants `c > 0` and `n₀` such that for all `n ≥ n₀`:
```
f(n) ≤ c · g(n)
```

**Example:** Show `3n² + 5n + 7 = O(n²)`.

Choose `c = 15` and `n₀ = 1`. For all `n ≥ 1`:
```
3n² + 5n + 7 ≤ 3n² + 5n² + 7n² = 15n²
```
(Each term is at most n² for n ≥ 1.) ✓

**Key insight:** O-notation gives a worst-case guarantee. Saying "the algorithm is O(n²)" means the running time is at most cn² for large inputs — not that it always uses quadratic time.

## Omega: Lower Bound

`f(n) = Ω(g(n))` means f grows **at least as fast** as g.

**Definition:** `∃c > 0, n₀: f(n) ≥ c·g(n)` for all `n ≥ n₀`.

**Example:** `3n² + 5n + 7 = Ω(n²)`. For `n ≥ 1`: `3n² + 5n + 7 ≥ 3n²`. Take `c = 3`.

Ω-notation is used to state lower bounds: "Any comparison-based sorting algorithm requires `Ω(n log n)` comparisons in the worst case."

## Theta: Tight Bound

`f(n) = Θ(g(n))` means f grows at **exactly** the same rate as g — bounded above and below.

`f(n) = Θ(g(n))` iff `f(n) = O(g(n))` AND `f(n) = Ω(g(n))`.

**Example:** `3n² + 5n + 7 = Θ(n²)` — we showed both O(n²) and Ω(n²) above.

When we say "merge sort runs in Θ(n log n)", we mean the running time is both O(n log n) and Ω(n log n) — a tight bound.

## Little-o and Little-omega: Strict Inequalities

- `f = o(g)` means f is **strictly dominated** by g: `lim(n→∞) f(n)/g(n) = 0`.
  - Example: `n = o(n²)` since `n/n² = 1/n → 0`.
- `f = ω(g)` means f **strictly dominates** g: `lim(n→∞) f(n)/g(n) = ∞`.
  - Example: `n² = ω(n)`.

These are used when you want to say one function is asymptotically **strictly** smaller or larger, not just at most or at least.

## Common Complexity Classes

| Class | Name | Typical algorithm | n = 10⁶ time (at 10⁹ ops/sec) |
|-------|------|------------------|-------------------------------|
| `Θ(1)` | Constant | Hash table lookup | <1 ns |
| `Θ(log n)` | Logarithmic | Binary search | ~20 ns |
| `Θ(√n)` | Square root | Trial division | ~1 μs |
| `Θ(n)` | Linear | Linear scan | ~1 ms |
| `Θ(n log n)` | Linearithmic | Merge sort | ~20 ms |
| `Θ(n²)` | Quadratic | Bubble sort | ~1000 s |
| `Θ(n³)` | Cubic | Naive matrix multiply | ~10¹⁰ s |
| `Θ(2^n)` | Exponential | Brute-force subset sum | Infeasible (n=60) |
| `Θ(n!)` | Factorial | Brute-force TSP | Infeasible (n=20) |

The jump from `n log n` to `n²` is dramatic: for `n = 10^6`, merge sort takes milliseconds, bubble sort would take over a thousand seconds.

## Rules for Simplifying Big-O Expressions

1. **Drop lower-order terms:** `n³ + n² + n = O(n³)`
2. **Drop constant factors:** `7n² = O(n²)`
3. **Transitivity:** If `f = O(g)` and `g = O(h)`, then `f = O(h)`.
4. **Sum rule:** `O(f) + O(g) = O(max(f, g))`. E.g., `O(n) + O(n²) = O(n²)`.
5. **Product rule:** `O(f) · O(g) = O(f·g)`. E.g., `O(n) · O(log n) = O(n log n)`.
6. **Polynomial dominance:** For any constants `a > b > 0`: `O(nᵃ)` strictly dominates `O(nᵇ)`.
7. **Exponential vs polynomial:** `O(cⁿ)` for `c > 1` strictly dominates all `O(nᵏ)`.
8. **Log rules:** `log₂(n) = Θ(log₁₀(n)) = Θ(ln(n))` — the base only matters for a constant factor.

## Worked Examples

### Example 1: Nested Loops

```python
for i in range(n):          # n iterations
    for j in range(i):      # i iterations
        process(i, j)       # O(1) work
```

Total: `Σᵢ₌₀^{n−1} i = n(n−1)/2 = Θ(n²)`.

### Example 2: Binary Search

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1
```

Each iteration halves the search space. After k iterations, the space is `n/2^k`. When `n/2^k = 1`, we stop: `k = log₂(n)`. Total: `T(n) = Θ(log n)`.

### Example 3: Logarithmic Mental Math

```
log₂(1,000,000) ≈ 20
log₂(1,000,000,000) ≈ 30
log₂(10^{18}) ≈ 60
```

A `O(log n)` algorithm is barely affected even by astronomical input sizes. This is why binary search on a trillion-element sorted array takes only about 40 comparisons.

### Example 4: Polynomial Evaluation (Horner's Method)

**Naïve evaluation** of `aₙxⁿ + aₙ₋₁xⁿ⁻¹ + … + a₀`: requires `Θ(n²)` multiplications (or `Θ(n)` with precomputed powers).

**Horner's method:** `(…((aₙ·x + aₙ₋₁)·x + aₙ₋₂)·x + …) + a₀` — uses exactly n multiplications and n additions: `Θ(n)`.

## Proving an Asymptotic Bound

**Claim:** `2^n = O(n!)` (factorial grows faster than exponential).

**Proof:** For `n ≥ 1`:
```
n! / 2^n = (n/2) · ((n-1)/2) · … · (2/2) · (1/2)
```
For `n ≥ 4`, every factor `k/2 ≥ 1` for `k ≥ 2`, and there are n−1 factors at least 1. So `n! ≥ 2^n` for `n ≥ 4`. Hence `2^n = O(n!)` (with c=1, n₀=4).

**Claim:** `n log n = o(n²)`.

`n log n / n² = log n / n → 0` as `n → ∞` (logarithms grow slower than any positive power of n). ✓

## Recurrences and Asymptotics Together

Once you solve a recurrence — say `T(n) = 2T(n/2) + n` → `Θ(n log n)` via the Master Theorem — you can rank algorithms:

| Algorithm | Recurrence | Complexity |
|-----------|-----------|-----------|
| Binary search | `T(n)=T(n/2)+1` | `O(log n)` |
| Merge sort | `T(n)=2T(n/2)+n` | `O(n log n)` |
| Karatsuba multiplication | `T(n)=3T(n/2)+n` | `O(n^1.585)` |
| Naive Fibonacci | `T(n)=T(n-1)+T(n-2)` | `O(2^n)` |
| Memoized Fibonacci | `T(n)=T(n-1)+O(1)` | `O(n)` |

## Amortized vs. Worst-Case

Big-O typically refers to **worst-case per operation**. **Amortized analysis** considers the average cost over a sequence of operations:

- Dynamic array (append): single append is O(n) when resizing, but amortized `O(1)` because resizing happens rarely.
- Binary counter: incrementing can flip up to n bits, but amortized `O(1)` per increment (each bit flips at most once per n increments on average).

## Summary

Asymptotic notation lets us compare algorithm efficiency without worrying about hardware speed or small inputs. Mastering O, Ω, and Θ — and knowing the common complexity classes and their practical implications — is the first step toward understanding why algorithm choice matters enormously in practice.

| Notation | Meaning | Analogy |
|----------|---------|---------|
| `O(g)` | f ≤ c·g for large n | ≤ (up to constant) |
| `Ω(g)` | f ≥ c·g for large n | ≥ (up to constant) |
| `Θ(g)` | Both O and Ω | = (up to constant) |
| `o(g)` | f/g → 0 | < (strict) |
| `ω(g)` | f/g → ∞ | > (strict) |
