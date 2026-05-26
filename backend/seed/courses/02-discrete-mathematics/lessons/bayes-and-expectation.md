# Bayes' Theorem and Expected Value

## Bayes' Theorem

Bayes' theorem is the mathematical engine behind **updating beliefs based on evidence**. It inverts conditional probability: given that we observe B, what is the probability that A was the underlying cause?

### Derivation

From the multiplication rule:
```
P(A ∩ B) = P(B | A) · P(A) = P(A | B) · P(B)
```

Solving for `P(A | B)`:
```
P(A | B) = P(B | A) · P(A) / P(B)
```

Using the **Law of Total Probability** to expand `P(B)` (assuming `A` and `Aᶜ` partition the sample space):
```
P(B) = P(B | A) · P(A)  +  P(B | Aᶜ) · P(Aᶜ)
```

So the full Bayes formula is:
```
P(A | B) = P(B | A) · P(A) / [P(B|A)·P(A) + P(B|Aᶜ)·P(Aᶜ)]
```

### Terminology

| Term | Symbol | Meaning |
|------|--------|---------|
| **Prior** | `P(A)` | Probability of A before observing B |
| **Likelihood** | `P(B\|A)` | Probability of evidence B, given A is true |
| **Posterior** | `P(A\|B)` | Updated probability of A after observing B |
| **Marginal** | `P(B)` | Total probability of observing B |

The Bayesian update rule: `Posterior ∝ Likelihood × Prior`.

### Worked Example 1 — Medical Test

A disease affects 1% of the population. A test has:
- 95% **sensitivity** (true positive rate): P(positive | has disease) = 0.95
- 90% **specificity** (true negative rate): P(negative | no disease) = 0.90, so P(positive | no disease) = 0.10 (10% false positive rate)

You test positive. What is the probability you actually have the disease?

Let A = "has disease", B = "tests positive."
- P(A) = 0.01, P(Aᶜ) = 0.99
- P(B | A) = 0.95, P(B | Aᶜ) = 0.10

```
P(B) = 0.95 × 0.01 + 0.10 × 0.99 = 0.0095 + 0.099 = 0.1085

P(A | B) = (0.95 × 0.01) / 0.1085 ≈ 0.0876  ≈ 8.76%
```

Despite the high sensitivity, you have less than a **9% chance** of having the disease after testing positive — because the disease is rare. The false positive rate (10% of 99% of people) swamps the true positives. This counter-intuitive result explains why population-wide screening for rare diseases generates many false alarms.

### Worked Example 2 — Spam Filtering

Prior P(spam) = 0.30 (30% of emails are spam). The word "free" appears in:
- 80% of spam emails: P("free" | spam) = 0.80
- 10% of legitimate emails: P("free" | not spam) = 0.10

Given an email contains "free," what is P(spam | "free")?

```
P("free") = 0.80 × 0.30 + 0.10 × 0.70 = 0.24 + 0.07 = 0.31

P(spam | "free") = (0.80 × 0.30) / 0.31 = 0.24 / 0.31 ≈ 0.774  ≈ 77.4%
```

A Bayesian spam filter does this for every word in the email, updating the probability iteratively (under a Naïve Bayes independence assumption).

## Random Variables and Expected Value

A **random variable** X is a function from the sample space S to the real numbers. It assigns a numerical value to each outcome.

- X = value shown on a die roll: X(1)=1, X(2)=2, …, X(6)=6.
- X = number of heads in 3 coin flips: X(HHH)=3, X(HHT)=2, etc.

The **probability distribution** of X is the function `P(X = x)` for each possible value x.

### Expected Value (Mean)

The **expected value** `E[X]` is the probability-weighted average of all possible outcomes:
```
E[X] = Σₓ x · P(X = x)
```

**Example — Die Roll:**
```
E[X] = 1·(1/6) + 2·(1/6) + 3·(1/6) + 4·(1/6) + 5·(1/6) + 6·(1/6)
     = (1+2+3+4+5+6)/6 = 21/6 = 3.5
```

The expected value need not be a possible outcome — you can't roll 3.5, but 3.5 is the long-run average.

**Example — Biased Coin:**
Flip a coin that shows heads with probability p. Let X = 1 for heads, 0 for tails.
```
E[X] = 1·p + 0·(1−p) = p
```

### Properties of Expectation

**Linearity (always true, even for dependent variables):**
```
E[aX + bY] = a·E[X] + b·E[Y]
```

**Constant:** `E[c] = c`

**Non-negativity:** If `X ≥ 0` always, then `E[X] ≥ 0`.

**Warning:** In general, `E[g(X)] ≠ g(E[X])` unless g is linear (Jensen's inequality).

### Indicator Random Variables

For an event A, define the **indicator**:
```
I_A = 1  if A occurs
I_A = 0  otherwise
```

Then `E[I_A] = P(A)`. This simple trick is extremely powerful.

**Example — Expected heads in 10 flips:**
Let `Xᵢ = 1` if flip i is heads. Total heads: `X = X₁ + X₂ + ⋯ + X₁₀`. By linearity:
```
E[X] = E[X₁] + ⋯ + E[X₁₀] = 10 × (1/2) = 5
```

**Example — Expected inversions in a random permutation:**
For a random permutation of `{1,…,n}`, let `Iᵢⱼ = 1` if element at position i is greater than element at position j (i < j). The number of inversions is `X = Σᵢ<ⱼ Iᵢⱼ`. By symmetry, `P(Iᵢⱼ = 1) = 1/2` for each pair. So:
```
E[X] = C(n,2) × (1/2) = n(n−1)/4
```

This tells us the average number of swaps needed by insertion sort on a random array is `Θ(n²)`.

### Variance

The **variance** `Var(X)` measures the spread of X around its mean:
```
Var(X) = E[(X − E[X])²] = E[X²] − (E[X])²
```

The **standard deviation** is `σ(X) = √Var(X)`.

**Example (die roll):**
```
E[X²] = (1²+2²+3²+4²+5²+6²)/6 = (1+4+9+16+25+36)/6 = 91/6

Var(X) = 91/6 − (3.5)² = 91/6 − 12.25 = 91/6 − 73.5/6 = 17.5/6 ≈ 2.917
```

**Independence and variance:**
If X and Y are **independent**, `Var(X + Y) = Var(X) + Var(Y)`.
If dependent, there is a covariance term: `Var(X + Y) = Var(X) + Var(Y) + 2·Cov(X,Y)`.

## Markov's and Chebyshev's Inequalities

These give bounds on probabilities without knowing the full distribution — invaluable in algorithm analysis.

**Markov's Inequality:** For non-negative X and any `t > 0`:
```
P(X ≥ t) ≤ E[X] / t
```

**Example:** If a website serves an average of 100 requests/minute, P(≥ 500 requests in a minute) ≤ 100/500 = 0.20.

**Chebyshev's Inequality:** For any `k > 0`:
```
P(|X − E[X]| ≥ k·σ) ≤ 1/k²
```

The probability of being more than k standard deviations from the mean is at most `1/k²`. This applies to **any** distribution — it is distribution-free.

**CS application — Hashing:** If a hash table has n buckets and m keys are inserted (m = n), Chebyshev's Inequality bounds the probability of heavy collisions, justifying the O(1) expected lookup claim.

## Summary

- Bayes' theorem updates prior beliefs with new evidence: `Posterior ∝ Likelihood × Prior`.
- The base rate (prior) often dominates — rare events remain unlikely even after a positive test.
- Expected value is the probability-weighted average; linearity makes it tractable for complex random variables.
- Indicator random variables and linearity of expectation are the main tools for computing expectations of sums.
- Markov's and Chebyshev's inequalities provide distribution-free probability bounds.
