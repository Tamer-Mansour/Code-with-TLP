# Recurrence Relations

A **recurrence relation** defines each term of a sequence in terms of earlier terms, plus a set of **initial conditions** that anchor the sequence at a starting point. Recurrences arise naturally from recursive algorithms: the running time of any divide-and-conquer or recursive program can be expressed as a recurrence.

## Why Recurrences Matter

- `Binary search` halves the problem each step: `T(n) = T(n/2) + 1`.
- `Merge sort` splits and merges: `T(n) = 2T(n/2) + n`.
- `Fibonacci` is defined recursively: `F(n) = F(n−1) + F(n−2)`.
- `Tower of Hanoi` moves n disks by solving n−1 twice plus one move: `T(n) = 2T(n−1) + 1`.

Solving these recurrences gives exact or asymptotic closed-form expressions for algorithm running times.

## Common Recurrences

| Recurrence | Initial condition(s) | Closed form | Describes |
|-----------|---------------------|------------|-----------|
| `T(n) = T(n−1) + 1` | `T(0) = 0` | `T(n) = n` | Loop counting one step per iteration |
| `T(n) = T(n−1) + n` | `T(0) = 0` | `T(n) = n(n+1)/2` | Triangular sums, selection sort |
| `T(n) = 2T(n−1) + 1` | `T(0) = 0` | `T(n) = 2^n − 1` | Tower of Hanoi |
| `T(n) = 2T(n/2) + n` | `T(1) = 0` | `T(n) = Θ(n log n)` | Merge sort |
| `F(n) = F(n−1) + F(n−2)` | `F(0)=0, F(1)=1` | Binet's formula (below) | Fibonacci numbers |
| `a(n) = r·a(n−1)` | `a(0) = c` | `a(n) = c·rⁿ` | Geometric growth |

## Method 1: Iteration / Unrolling

Repeatedly substitute the recurrence into itself until a pattern emerges. Then sum using a known formula.

**Example — `T(n) = T(n−1) + n`, `T(0) = 0`:**
```
T(n) = T(n−1) + n
     = T(n−2) + (n−1) + n
     = T(n−3) + (n−2) + (n−1) + n
     = …
     = T(0) + 1 + 2 + … + n
     = 0 + n(n+1)/2
```
So `T(n) = n(n+1)/2`.

**Example — `T(n) = 2T(n−1) + 1`, `T(0) = 0` (Tower of Hanoi):**
```
T(n) = 2T(n−1) + 1
     = 2[2T(n−2) + 1] + 1 = 4T(n−2) + 2 + 1
     = 4[2T(n−3) + 1] + 3 = 8T(n−3) + 4 + 2 + 1
     = …
     = 2^k T(n−k) + (2^k − 1)
```
Setting `k = n`: `T(n) = 2^n · T(0) + (2^n − 1) = 2^n − 1`.

To move 64 Tower of Hanoi disks requires `2^64 − 1 ≈ 1.8 × 10^{19}` moves — at one move per second, over 580 billion years.

## Method 2: Characteristic Root Method (Homogeneous Linear Recurrences)

For linear recurrences with constant coefficients:
```
a(n) = c₁·a(n−1) + c₂·a(n−2) + … + cₖ·a(n−k)
```

**Step 1:** Substitute the **ansatz** `a(n) = rⁿ` and divide by `r^(n−k)` to get the **characteristic equation**:
```
r^k = c₁·r^(k−1) + c₂·r^(k−2) + … + cₖ
```

**Step 2:** Find the roots `r₁, r₂, …, rₖ`.

**Step 3:** Write the general solution:
- **Distinct roots:** `a(n) = A₁·r₁ⁿ + A₂·r₂ⁿ + … + Aₖ·rₖⁿ`
- **Repeated root r of multiplicity m:** contributes `(A₀ + A₁·n + … + A_{m−1}·n^(m−1))·rⁿ`

**Step 4:** Use initial conditions to solve for the constants A₁, A₂, …

### Worked Example — Fibonacci

`F(n) = F(n−1) + F(n−2)`, `F(0) = 0, F(1) = 1`.

**Characteristic equation:** `r² − r − 1 = 0`.

**Roots:** `r = (1 ± √5) / 2`.

Let `φ = (1+√5)/2 ≈ 1.618` (the golden ratio) and `ψ = (1−√5)/2 ≈ −0.618`.

**General solution:** `F(n) = A·φⁿ + B·ψⁿ`.

**Apply initial conditions:**
```
F(0) = A + B = 0     ⟹  B = −A
F(1) = Aφ + Bψ = 1
     = A(φ − ψ) = 1
     = A·√5 = 1
     ⟹  A = 1/√5
```

**Binet's Formula:**
```
F(n) = (φⁿ − ψⁿ) / √5
```

Since `|ψ| < 1`, `ψⁿ → 0`, and `F(n)` rounds to the nearest integer for all n. This shows that Fibonacci numbers grow exponentially as `Θ(φⁿ)`.

### Worked Example — 2nd Order with Repeated Root

`a(n) = 4a(n−1) − 4a(n−2)`, `a(0) = 1, a(1) = 4`.

Characteristic equation: `r² − 4r + 4 = (r−2)² = 0`. Repeated root `r = 2`.

General solution: `a(n) = (A + Bn)·2ⁿ`.

Apply conditions: `a(0) = A = 1` ⟹ `A = 1`. `a(1) = (1 + B)·2 = 4` ⟹ `B = 1`.

Answer: `a(n) = (1 + n)·2ⁿ = (n+1)·2ⁿ`.

## Method 3: The Master Theorem

For **divide-and-conquer** recurrences of the form `T(n) = a·T(n/b) + f(n)` where `a ≥ 1, b > 1`:

Let `c* = log_b(a)`. Compare the work `f(n)` at each level to `nᶜ*` (the work of the recursion tree "pure" part):

| Case | Condition | Solution |
|------|-----------|---------|
| 1 (recursion dominates) | `f(n) = O(n^(c*−ε))` for ε > 0 | `T(n) = Θ(n^c*)` |
| 2 (equal work at each level) | `f(n) = Θ(n^c*)` | `T(n) = Θ(n^c* · log n)` |
| 3 (top level dominates) | `f(n) = Ω(n^(c*+ε))` + regularity | `T(n) = Θ(f(n))` |

**Worked Applications:**

| Algorithm | Recurrence | a, b, c* | f(n) vs n^c* | Result |
|-----------|-----------|----------|-------------|--------|
| Binary search | `T=T(n/2)+1` | 1, 2, 0 | `1=Θ(n⁰)` → Case 2 | `Θ(log n)` |
| Merge sort | `T=2T(n/2)+n` | 2, 2, 1 | `n=Θ(n¹)` → Case 2 | `Θ(n log n)` |
| Karatsuba multiply | `T=3T(n/2)+n` | 3, 2, log₂3≈1.585 | `n=O(n^(1.585−ε))` → Case 1 | `Θ(n^log₂3)` |
| Strassen's matrix | `T=7T(n/2)+n²` | 7, 2, log₂7≈2.807 | `n²=O(n^(2.807−ε))` → Case 1 | `Θ(n^log₂7)` |

**Limitations:** The Master Theorem does NOT apply when: `f(n)` is not a polynomial (e.g., `f(n) = n log n` is technically Case 2 extended), or the recurrence is `T(n) = 2T(n/2) + n/log n` (falls in the gap between Cases 1 and 2).

## Generating Functions (Sketch)

For more complex recurrences, **generating functions** encode the entire sequence as coefficients of a power series:
```
G(x) = Σₙ aₙ xⁿ = a₀ + a₁x + a₂x² + …
```

The recurrence relation becomes an equation on G(x), which you solve algebraically and expand to extract aₙ. This is a powerful technique used in combinatorics and probability.

## Summary

- **Iteration (unrolling):** Directly substitute and sum — best for simple recurrences.
- **Characteristic roots:** Systematic method for linear constant-coefficient homogeneous recurrences.
- **Master Theorem:** Quick asymptotic solution for divide-and-conquer recurrences.
- **Generating functions:** Most general method, required for advanced cases.

Recognizing and solving recurrences is an essential skill for algorithm analysis: it converts algorithm structure into a mathematical equation, and solving that equation gives the algorithm's running time.
