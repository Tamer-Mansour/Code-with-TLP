# Mathematical Induction

Mathematical induction is one of the most powerful — and most frequently used — proof techniques in discrete mathematics. It allows us to prove statements that hold for infinitely many cases without checking each individually. Understanding induction deeply is essential not just for proofs, but for reasoning about loops, recursion, and algorithm correctness.

## The Principle

Think of induction like an infinite row of dominoes:
1. The **first** domino falls (base case).
2. Whenever **any** domino falls, the **next** one also falls (inductive step).

Conclusion: every domino falls.

Formally, to prove `∀n ≥ n₀: P(n)`:
1. **Base case:** Prove `P(n₀)`.
2. **Inductive step:** For arbitrary `k ≥ n₀`, assume `P(k)` (the **inductive hypothesis**), then prove `P(k+1)`.

The key skill is algebraically connecting the `P(k+1)` expression back to the `P(k)` hypothesis — usually by isolating the "new" term added at step k+1 and applying the inductive hypothesis to the rest.

## Worked Example 1 — Sum of Consecutive Integers

**Claim:** `1 + 2 + 3 + ⋯ + n = n(n+1)/2` for all `n ≥ 1`.

**Base case (n=1):** LHS = 1, RHS = `1·2/2 = 1`. ✓

**Inductive step:** Assume `1 + 2 + ⋯ + k = k(k+1)/2`. We want to show the formula holds for `k+1`:
```
LHS(k+1) = (1 + 2 + ⋯ + k) + (k+1)
          = k(k+1)/2  +  (k+1)            [inductive hypothesis]
          = (k+1)[k/2 + 1]
          = (k+1)(k+2)/2
          = RHS(k+1)  ✓
```

This formula is crucial in algorithm analysis: the total work done by a triangular nested loop `for i in range(n): for j in range(i)` is exactly `n(n-1)/2 = Θ(n²)`.

## Worked Example 2 — Sum of First n Odd Numbers

**Claim:** `1 + 3 + 5 + ⋯ + (2n-1) = n²` for all `n ≥ 1`.

**Base case (n=1):** LHS = 1, RHS = 1². ✓

**Inductive step:** Assume `1 + 3 + ⋯ + (2k-1) = k²`. The next odd number is `2k+1 = 2(k+1)-1`. Adding it:
```
1 + 3 + ⋯ + (2k-1) + (2k+1)
= k²  +  (2k+1)               [by inductive hypothesis]
= k² + 2k + 1
= (k+1)²  ✓
```

**Visual insight:** This has a beautiful geometric interpretation. An `n×n` square can be built from nested L-shaped "gnomons," each contributing the next odd number. The n-th gnomon adds `2n-1` unit squares.

## Worked Example 3 — Geometric Sum

**Claim:** For `r ≠ 1`, `1 + r + r² + ⋯ + rⁿ = (r^(n+1) - 1) / (r - 1)` for all `n ≥ 0`.

**Base case (n=0):** LHS = 1, RHS = `(r¹ - 1)/(r - 1) = 1`. ✓

**Inductive step:** Assume the formula holds for n = k. Then for n = k+1:
```
(1 + r + ⋯ + r^k) + r^(k+1)
= (r^(k+1) - 1)/(r-1)  +  r^(k+1)             [by inductive hypothesis]
= [r^(k+1) - 1 + r^(k+1)(r-1)] / (r-1)
= [r^(k+1) - 1 + r^(k+2) - r^(k+1)] / (r-1)
= [r^(k+2) - 1] / (r-1)  ✓
```

**Application:** This formula gives the exact total cost of a complete binary tree traversal, and it explains why `O(2^n)` algorithms are infeasible for large n: the total work doubles each step, and the geometric sum is dominated by the last term.

## Worked Example 4 — Powers of 2 and Sets

**Claim:** A set with `n` elements has exactly `2^n` subsets, for all `n ≥ 0`.

**Base case (n=0):** The empty set has exactly 1 = `2^0` subset (itself). ✓

**Inductive step:** Assume a set with k elements has `2^k` subsets. Let `S = {a₁, a₂, …, aₖ, aₖ₊₁}`. Each subset of S either:
- does **not** contain `aₖ₊₁`: there are `2^k` such subsets (subsets of `{a₁,…,aₖ}`).
- **does** contain `aₖ₊₁`: there are also `2^k` such subsets (take each of the above and add `aₖ₊₁`).

Total: `2^k + 2^k = 2^(k+1)`. ✓

This proves why a hash set with n bits has `2^n` possible states — an insight central to space complexity analysis and the subset-sum problem.

## Strong Induction

In **strong (complete) induction**, the inductive hypothesis is:
> Assume `P(n₀), P(n₀+1), …, P(k)` all hold (not just `P(k)`).

This is necessary when the proof of `P(k+1)` requires some `P(j)` for `j < k`, not just the immediately preceding step.

**Example: Every integer ≥ 2 is a product of primes (Fundamental Theorem, existence).**

*Base case (n=2):* 2 is prime. ✓

*Strong inductive step:* Assume every integer from 2 to k has a prime factorization. Consider `k+1`:
- If `k+1` is prime: done.
- If `k+1 = a × b` with `2 ≤ a, b < k+1`: by the strong hypothesis, both `a` and `b` have prime factorizations, so `k+1` is the product of those factorizations. ✓

Since a and b might be as small as 2 (nowhere near k), the standard induction hypothesis `P(k)` alone is insufficient.

**Another use — Fibonacci:** To show `F(n) ≤ 2^n` you only need `P(n-1)`, but to derive an exact formula for `F(n)` you need both `F(n-1)` and `F(n-2)`, which requires strong induction.

## The Well-Ordering Principle

The **well-ordering principle** states: every non-empty subset of non-negative integers has a **least element**.

Induction, strong induction, and the well-ordering principle are all logically equivalent over the natural numbers. Many elegant number-theory proofs proceed by contradiction using the well-ordering principle:

1. Assume the set of counterexamples is non-empty.
2. Pick its least element n.
3. Show n cannot actually be a counterexample, or that a smaller counterexample exists — contradiction.

**Example:** Prove every positive integer can be written as a sum of distinct powers of 2 (i.e., in binary). Assume the set of integers that **cannot** be so written is non-empty. Let n be the smallest such integer. If n is even, `n/2` is smaller, so it has a binary representation; multiplying each power by 2 gives one for n — contradiction. If n is odd, `n-1` is even and smaller, so it has a binary representation; adding `2⁰ = 1` (which is not already present since n-1 is even) gives one for n — contradiction.

## Induction Compared to Recursion

The analogy between induction and recursion is precise:

| Induction | Recursion |
|-----------|-----------|
| Base case | Base case |
| Inductive step | Recursive case |
| Inductive hypothesis | Recursive call result |
| Proved once, valid for all n | Computed once per call |

When you prove that a recursive algorithm is correct, you are almost always doing induction on the input size.

## Common Mistakes

| Mistake | Why it breaks the proof |
|---------|------------------------|
| Forgetting the base case | The chain has no starting point |
| Using P(k+1) to prove P(k+1) | Circular reasoning |
| Inductive step valid only for k ≥ 2 but base case is k=1 | Gap in the chain |
| Claiming "it works for small values, so it's general" | That is empirical testing, not proof |
| Confusing the inductive hypothesis with the conclusion | You assume P(k); you prove P(k+1) |

## Summary

- Induction = base case + inductive step.
- Strong induction allows using all prior cases; use it when `P(k+1)` depends on earlier values beyond `P(k)`.
- The well-ordering principle is an equivalent formulation of induction, often used in number-theory contradiction arguments.
- Induction directly corresponds to recursive algorithm correctness proofs.
- The key algebraic move in the inductive step is to isolate the "extra" term, apply the hypothesis to the remaining sum/product, and simplify.
