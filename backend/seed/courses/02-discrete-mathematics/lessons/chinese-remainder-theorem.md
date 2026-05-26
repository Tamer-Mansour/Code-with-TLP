# Chinese Remainder Theorem

The **Chinese Remainder Theorem (CRT)** is a foundational result in number theory that tells us when a system of simultaneous congruences has a unique solution. It is named after the ancient Chinese mathematician Sun Tzu (Sun Zi, c. 3rd century CE), who posed the earliest known version of the problem.

## The Problem

Suppose you want to find an integer x satisfying:
```
x ≡ a₁ (mod m₁)
x ≡ a₂ (mod m₂)
⋮
x ≡ aₖ (mod mₖ)
```

Under what conditions does a solution exist? Is it unique? How do you find it?

## Statement of the Theorem

**Theorem (CRT):** If `m₁, m₂, …, mₖ` are pairwise coprime (i.e., `gcd(mᵢ, mⱼ) = 1` for all `i ≠ j`), then for any integers `a₁, a₂, …, aₖ`, the system has a **unique solution modulo** `M = m₁ · m₂ · ⋯ · mₖ`.

In other words, the solution is unique in `{0, 1, …, M−1}`.

## Algorithm for Two Congruences

Given `x ≡ a (mod m)` and `x ≡ b (mod n)` with `gcd(m, n) = 1`:

1. Write `x = am + k` for some integer k (satisfying the first congruence automatically).
2. Substitute into the second: `am + k ≡ b (mod n)`.
3. Solve for k: `k ≡ (b − am) · m⁻¹ (mod n)` (modular inverse of m mod n exists since gcd(m,n)=1).
4. Substitute back: `x = am + k·m`.
5. Reduce mod M = mn.

## Worked Example

Find x such that `x ≡ 2 (mod 3)` and `x ≡ 3 (mod 5)`.

Here `m = 3, n = 5, a = 2, b = 3, M = 15`.

Write `x = 2 + 3k`. Substitute: `2 + 3k ≡ 3 (mod 5)` ⟹ `3k ≡ 1 (mod 5)`.

Find `3⁻¹ mod 5`: `3 · 2 = 6 ≡ 1 (mod 5)`, so `3⁻¹ ≡ 2`.

Thus `k ≡ 2 (mod 5)`, so `k = 2 + 5j`. Then `x = 2 + 3(2 + 5j) = 8 + 15j`.

**Answer:** `x ≡ 8 (mod 15)`.

**Verification:** `8 mod 3 = 2` ✓, `8 mod 5 = 3` ✓.

## Three Congruences Example

Find x with `x ≡ 1 (mod 3)`, `x ≡ 2 (mod 5)`, `x ≡ 3 (mod 7)`.

`M = 3·5·7 = 105`.

**Construct the CRT solution directly:**

Let `M₁ = 105/3 = 35`, `M₂ = 105/5 = 21`, `M₃ = 105/7 = 15`.

Find inverses:
- `35 ≡ 2 (mod 3)` ⟹ `2⁻¹ mod 3 = 2` (since `2·2=4≡1`), so `y₁ = 2`.
- `21 ≡ 1 (mod 5)` ⟹ `y₂ = 1`.
- `15 ≡ 1 (mod 7)` ⟹ `y₃ = 1`.

CRT solution:
```
x = a₁·M₁·y₁ + a₂·M₂·y₂ + a₃·M₃·y₃
  = 1·35·2 + 2·21·1 + 3·15·1
  = 70 + 42 + 45
  = 157 ≡ 52 (mod 105)
```

**Verification:** `52 mod 3 = 1` ✓, `52 mod 5 = 2` ✓, `52 mod 7 = 3` ✓.

## Why Pairwise Coprimality is Necessary

If the moduli share a common factor, the system may have no solution or infinitely many not captured by one modulus. For example, `x ≡ 1 (mod 4)` and `x ≡ 2 (mod 6)` — since `gcd(4,6) = 2` — has no solution: the first requires x to be odd, the second requires x to be even.

## Proof Sketch

Uniqueness: if x and y both satisfy all congruences, then `mᵢ | (x − y)` for all i. Since the mᵢ are pairwise coprime, `M = m₁⋯mₖ | (x − y)`, so `x ≡ y (mod M)`.

Existence: the general construction (using Mᵢ = M/mᵢ and their inverses) always produces a valid solution when the moduli are pairwise coprime.

## Applications in Computer Science

### Big Integer Arithmetic

Multiplying two large integers can be done faster by working in several small moduli and combining results with CRT. The **Schönhage-Strassen algorithm** (used in GMP/FLINT) applies CRT-like techniques to achieve `O(n log n log log n)` multiplication.

### Secret Sharing

Shamir's secret sharing splits a secret S into k shares such that any t shares reconstruct S using polynomial interpolation over `ℤ_p`. A simpler threshold scheme: compute `S mod m₁, S mod m₂, …` — any combination of enough shares allows CRT reconstruction.

### RSA Optimization (CRT-RSA)

RSA decryption computes `M ≡ Cᵈ (mod n)` with `n = pq`. Using CRT, compute separately:
```
M_p = Cᵈ mod p   and   M_q = Cᵈ mod q
```
Then apply CRT to recover `M mod n`. This reduces the exponentiation from one `d`-bit operation mod n to two `d/2`-bit operations mod p and mod q — roughly 4× speedup.

### Parallel Computation

When computations are done in multiple independent modular rings, CRT lets you merge results. This is used in SIMD integer operations and multi-precision libraries.

## Relationship to Ring Isomorphisms

The CRT has an elegant algebraic interpretation: when `gcd(m, n) = 1`:
```
ℤ/(mn) ≅ ℤ/m × ℤ/n
```
as rings. The CRT bijection maps `x mod mn` to the pair `(x mod m, x mod n)`. This ring isomorphism is fundamental to algebraic number theory and coding theory.

## Summary

| Aspect | Statement |
|--------|-----------|
| Condition | m₁, m₂, …, mₖ pairwise coprime |
| Existence | Always exists under pairwise coprimality |
| Uniqueness | Unique mod M = m₁⋯mₖ |
| Algorithm | Construct using Mᵢ = M/mᵢ and their inverses mod mᵢ |
| Applications | RSA speedup, secret sharing, big integer arithmetic |

The Chinese Remainder Theorem elegantly connects divisibility, modular inverses, and ring theory — showing how number theory problems can be decomposed into independent sub-problems on prime-power moduli, then recombined.
