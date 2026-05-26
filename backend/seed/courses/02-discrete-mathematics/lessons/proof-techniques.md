# Proof Techniques

A **proof** is a sequence of logically justified steps that establishes a mathematical statement beyond all doubt. Unlike experimental evidence, a proof is universal — once proven, the theorem holds in every conceivable case. This lesson surveys the most widely used techniques you will encounter in discrete mathematics and algorithm analysis.

## Why Proofs Matter in CS

- **Correctness:** Proving an algorithm correct means it works for all valid inputs, not just the tested ones.
- **Complexity:** Asymptotic bounds like `O(n log n)` are proven, not just measured.
- **Cryptography:** Security guarantees are mathematical reductions, not empirical observations.
- **Compilers:** Transformation correctness (e.g., loop unrolling, inlining) relies on logical equivalences.

## Direct Proof

**Idea:** Assume the hypothesis is true and derive the conclusion step by step using definitions, axioms, and previously proven lemmas.

**Template:** To prove `p → q`, assume `p` and show `q` must follow.

**Example 1:** Prove that if `n` is even, then `n²` is even.

*Proof:* Assume `n` is even. By definition, `n = 2k` for some integer `k`. Therefore:
```
n² = (2k)² = 4k² = 2(2k²)
```
Since `2k²` is an integer, `n²` is divisible by 2, so `n²` is even. QED.

**Example 2:** Prove that if a | b and b | c, then a | c.

*Proof:* Assume `a | b` and `b | c`. Then `b = ak` and `c = bm` for some integers k, m. Substituting:
```
c = bm = (ak)m = a(km)
```
Since `km` is an integer, `a | c`. QED.

This technique is called **transitivity of divisibility** and is used constantly in number theory.

## Proof by Contrapositive

**Idea:** Instead of proving `p → q` directly, prove the logically equivalent contrapositive `¬q → ¬p`. Choose whichever direction is algebraically easier.

**When to use:** When the hypothesis `p` is easy to state but hard to connect forward to `q`, whereas the negation of the conclusion `¬q` gives you something concrete to work with.

**Example:** Prove that if `n²` is odd, then `n` is odd.

*Direct proof is hard:* We would need to extract properties of `n` from `n²`, which is awkward.

*Proof by contrapositive:* Assume `n` is **even** (i.e., ¬q). Then `n = 2k`, so `n² = 4k² = 2(2k²)`, which is even (¬p). Therefore, the contrapositive holds, and the original statement is proved. QED.

**Comparison table:**

| Approach | Assumes | Derives |
|----------|---------|---------|
| Direct | p (n² is odd) | q (n is odd) |
| Contrapositive | ¬q (n is even) | ¬p (n² is even) |

Both are logically equivalent, but the contrapositive is often cleaner.

## Proof by Contradiction

**Idea:** Assume the **negation** of the entire statement, then derive a logical contradiction (a statement of the form `P ∧ ¬P`). Since a contradiction is impossible, the negation must be false, so the original statement is true.

**When to use:** When the statement involves "no X exists" or "X is irrational/transcendental," i.e., when direct construction fails.

**Example: `√2` is irrational.**

*Proof:* Suppose for contradiction that `√2` is rational. Then `√2 = p/q` where `p, q` are integers with `gcd(p, q) = 1` (the fraction is in lowest terms).

Squaring: `2 = p²/q²`, so `p² = 2q²`. This means `p²` is even, which implies `p` is even (by the previous theorem). Write `p = 2m`.

```
(2m)² = 2q²  ⟹  4m² = 2q²  ⟹  q² = 2m²
```

So `q²` is even, which implies `q` is even. But then both `p` and `q` are even, contradicting `gcd(p, q) = 1`. Contradiction. Therefore, `√2` is irrational. QED.

**Example: There are infinitely many primes.**

*Proof:* Suppose there are finitely many primes: `p₁, p₂, …, pₖ`. Form the number `N = p₁p₂⋯pₖ + 1`. N is not divisible by any `pᵢ` (the remainder is always 1). Since `N ≥ 2`, it must have a prime divisor. That divisor is not on our list — contradiction. Hence there are infinitely many primes. QED.

## Proof by Cases

**Idea:** Partition the domain into finitely many exhaustive, non-overlapping cases and prove the claim independently in each case.

**When to use:** When the property behaves differently for different types of inputs (e.g., even vs. odd, positive vs. zero vs. negative).

**Example:** Prove that `n² + n` is even for all integers `n`.

*Proof:*
- **Case 1 (n even):** `n = 2k`, so `n² + n = 4k² + 2k = 2(2k² + k)` — even.
- **Case 2 (n odd):** `n = 2k+1`, so `n² + n = (4k²+4k+1) + (2k+1) = 4k²+6k+2 = 2(2k²+3k+1)` — even.

Both cases give an even result. QED.

**Note:** The two cases (even, odd) are exhaustive (every integer falls in exactly one) and non-overlapping.

**Example: |xy| = |x|·|y| for real numbers x, y.**

Cases: both positive; x positive, y negative; x negative, y positive; both negative. Four sub-cases, each a short algebraic check.

## Mathematical Induction

Induction proves statements of the form "`P(n)` is true for all `n ≥ n₀`."

**Structure:**
1. **Base case:** Verify `P(n₀)` is true.
2. **Inductive step:** Assume `P(k)` (the **inductive hypothesis**), then prove `P(k+1)`.

**Example:** Prove `1 + 2 + ⋯ + n = n(n+1)/2`.

*Base case (n=1):* LHS = 1, RHS = `1·2/2 = 1`. ✓

*Inductive step:* Assume the formula holds for `n = k`:
```
1 + 2 + ⋯ + k = k(k+1)/2
```
Add `k+1` to both sides:
```
1 + 2 + ⋯ + k + (k+1)
= k(k+1)/2 + (k+1)
= (k+1)[k/2 + 1]
= (k+1)(k+2)/2
```
This is exactly the formula with `n = k+1`. QED.

**Common induction pitfalls:**

| Pitfall | Why it breaks the proof |
|---------|------------------------|
| Forgetting the base case | The chain has no anchor |
| Circular reasoning: using P(k+1) in proving P(k+1) | Logical fallacy |
| Inductive step valid only for k > 1 but base case is k=1 | Check ranges carefully |
| Assuming one example proves the general case | That is testing, not proof |

## Strong Induction

In **strong (complete) induction**, the inductive hypothesis is: "Assume `P(j)` holds for all `n₀ ≤ j ≤ k`." This is strictly more powerful when proving `P(k+1)` requires results from further back than just `P(k)`.

**Example:** Every integer `n ≥ 2` has a prime factorization.

*Base case (n=2):* 2 is prime — its factorization is just {2}. ✓

*Strong inductive step:* Assume every integer from 2 to k has a prime factorization. Consider `k+1`:
- If `k+1` is prime: done.
- If `k+1 = a·b` with `2 ≤ a, b ≤ k`: by hypothesis, both `a` and `b` have prime factorizations, so `k+1` does too. ✓

Notice we needed the hypothesis for values less than k, not just k — that's why strong induction is required.

## Choosing a Technique

| Situation | Preferred technique |
|-----------|-------------------|
| Direct path from hypothesis to conclusion | Direct proof |
| Negation of conclusion is easier to use | Contrapositive |
| Negation leads to an obvious impossibility | Contradiction |
| Domain splits into a few distinct types | Cases |
| Statement involves all natural numbers | Induction |
| P(k+1) depends on earlier values, not just P(k) | Strong induction |

## Worked Example Combining Techniques

**Theorem:** For all integers `n ≥ 0`, the expression `6^n - 1` is divisible by 5.

**Proof by induction:**

*Base case (n=0):* `6⁰ - 1 = 0 = 5·0`. ✓

*Inductive step:* Assume `5 | (6^k - 1)`, i.e., `6^k = 5m + 1` for some integer m. Then:
```
6^(k+1) - 1 = 6 · 6^k - 1
             = 6(5m + 1) - 1      [substituting inductive hypothesis]
             = 30m + 6 - 1
             = 30m + 5
             = 5(6m + 1)
```
So `5 | (6^(k+1) - 1)`. QED.

This combines the **substitution** trick with a **direct** algebraic manipulation inside the inductive step — a common pattern.

## Key Takeaway

Good proofs are clear, complete, and justified at every step. Mastering these techniques gives you the tools to tackle virtually any elementary mathematical claim, and more importantly, to reason rigorously about algorithms, data structures, and protocols in computer science.
