# Probability Basics: Sample Spaces and Events

Probability theory gives us a rigorous way to reason about uncertainty. In computer science, probability underpins randomized algorithms, hashing analysis, machine learning, cryptographic security arguments, and systems reliability. We focus here on **discrete probability** — settings where outcomes can be enumerated.

## Sample Space and Events

The **sample space** `S` (or `Ω`) is the set of all possible outcomes of a random experiment.

- Roll a single die: `S = {1, 2, 3, 4, 5, 6}`
- Flip two coins: `S = {HH, HT, TH, TT}`
- Draw a card from a 52-card deck: `S` has 52 elements

An **event** is any subset `E ⊆ S`. Events can be:
- **Elementary:** a single outcome, e.g., `{4}` (rolled a 4).
- **Compound:** multiple outcomes, e.g., `{2, 4, 6}` (rolled an even number).
- **Impossible event:** `∅` (probability 0).
- **Certain event:** `S` itself (probability 1).

## Probability of an Event (Uniform Distribution)

When all outcomes are equally likely (the **uniform** or **equiprobable** distribution):
```
P(E) = |E| / |S|
```

**Example:** P(rolling a 4) = 1/6.  
**Example:** P(rolling even) = |{2,4,6}| / 6 = 3/6 = 1/2.  
**Example:** P(drawing an ace) = 4/52 = 1/13.

## Kolmogorov's Probability Axioms

A **probability function** P must satisfy:

1. `P(E) ≥ 0` for every event E.
2. `P(S) = 1` (the sample space has probability 1).
3. **Countable additivity:** For mutually exclusive events A₁, A₂, …:
   ```
   P(A₁ ∪ A₂ ∪ …) = P(A₁) + P(A₂) + …
   ```

From these three axioms we derive everything else:

| Derived rule | Formula |
|-------------|---------|
| Impossible event | `P(∅) = 0` |
| Complement | `P(Eᶜ) = 1 − P(E)` |
| Inclusion-exclusion | `P(A ∪ B) = P(A) + P(B) − P(A ∩ B)` |
| Monotonicity | If `A ⊆ B`, then `P(A) ≤ P(B)` |
| Bound | `0 ≤ P(E) ≤ 1` |

## Worked Examples

**Example 1:** Draw one card from a standard 52-card deck. P(heart OR face card)?

- P(heart) = 13/52
- P(face card) = 12/52  (J, Q, K in each of 4 suits)
- P(heart AND face card) = 3/52  (J♥, Q♥, K♥)
- P(heart OR face card) = 13/52 + 12/52 − 3/52 = 22/52 = **11/26**

**Example 2:** Flip 3 fair coins. P(at least two heads)?

Sample space: `{HHH, HHT, HTH, THH, HTT, THT, TTH, TTT}`, all equally likely, so `|S| = 8`.

Favorable outcomes (≥ 2 heads): HHH, HHT, HTH, THH → 4 outcomes.

P(at least two heads) = 4/8 = **1/2**.

**Complement shortcut:** P(at least two heads) = 1 − P(0 or 1 head).
P(0 heads) = 1/8, P(exactly 1 head) = 3/8. So P(≥ 2 heads) = 1 − 1/8 − 3/8 = 4/8 = 1/2. ✓

## Conditional Probability

The **conditional probability** of A given B is:
```
P(A | B) = P(A ∩ B) / P(B)      (assuming P(B) > 0)
```

Intuitively: restrict the sample space to B, and ask what fraction of B also satisfies A.

**Example:** Roll a fair die. P(result > 4 | result is even)?
- `B = {2, 4, 6}`, `P(B) = 3/6 = 1/2`
- `A ∩ B = {6}`, `P(A ∩ B) = 1/6`
- `P(A | B) = (1/6) / (1/2) = 1/3`

**CS application:** Bayesian spam filtering computes P(spam | the word "free" appears), updating the prior probability of spam with evidence from the email's content.

## Independence

Events A and B are **independent** if:
```
P(A ∩ B) = P(A) · P(B)
```

Equivalently, `P(A | B) = P(A)` (knowing B occurred gives no information about A).

**Example:** Roll two dice. The result of the first die is independent of the second.

**Example:** Drawing two cards **with** replacement are independent; **without** replacement are not.

**Mutual independence (multiple events):** Events A₁, A₂, …, Aₙ are mutually independent if every subset's intersection probability equals the product of individual probabilities.

**Pairwise independence is NOT sufficient for mutual independence** — a subtle point often missed. There exist sets of events that are pairwise independent but not mutually independent.

## The Multiplication Rule

From the definition of conditional probability:
```
P(A ∩ B) = P(A) · P(B | A) = P(B) · P(A | B)
```

For independent events: `P(A ∩ B) = P(A) · P(B)`.

**Example:** Draw two cards without replacement from a 52-card deck.
P(both aces) = P(first is ace) × P(second is ace | first was ace) = (4/52) × (3/51) = 12/2652 = **1/221**.

## Law of Total Probability

If `{B₁, B₂, …, Bₖ}` is a **partition** of S (mutually exclusive and exhaustive):
```
P(A) = Σᵢ P(A | Bᵢ) · P(Bᵢ)
```

**Example:** A factory has two machines. Machine 1 produces 60% of items and has a 2% defect rate; Machine 2 produces 40% and has a 5% defect rate.

P(defective item) = P(def | M1) · P(M1) + P(def | M2) · P(M2)
= 0.02 × 0.60 + 0.05 × 0.40
= 0.012 + 0.020
= **0.032** (3.2% overall defect rate)

## Union Bound (Boole's Inequality)

For any events A₁, A₂, …, Aₙ (not necessarily disjoint):
```
P(A₁ ∪ A₂ ∪ … ∪ Aₙ) ≤ P(A₁) + P(A₂) + … + P(Aₙ)
```

**CS application:** In algorithm analysis, we often want to show that a "bad event" is unlikely. If each bad sub-event has probability at most `ε`, and there are `n` such sub-events, the Union Bound guarantees the overall bad probability is at most `nε`. This is standard in probabilistic algorithm analysis.

## Counting Meets Probability

Many probability problems reduce to counting:

**Problem:** 5 cards are drawn from a 52-card deck. What is P(exactly one pair)?

- Total 5-card hands: `C(52,5) = 2,598,960`
- "Exactly one pair" hands:
  - Choose the pair's rank: `C(13,1) = 13`
  - Choose 2 of 4 suits for the pair: `C(4,2) = 6`
  - Choose 3 other ranks (different from the pair): `C(12,3) = 220`
  - For each of the 3 other ranks, choose a suit: `4^3 = 64`
  - Favorable hands: `13 × 6 × 220 × 64 = 1,098,240`
- P(exactly one pair) = 1,098,240 / 2,598,960 ≈ **0.4226** (42.26%)

## Summary

| Concept | Formula |
|---------|---------|
| Uniform probability | `P(E) = |E| / |S|` |
| Complement | `P(Eᶜ) = 1 − P(E)` |
| Inclusion-exclusion | `P(A∪B) = P(A)+P(B)−P(A∩B)` |
| Conditional | `P(A\|B) = P(A∩B)/P(B)` |
| Independence | `P(A∩B) = P(A)·P(B)` |
| Multiplication rule | `P(A∩B) = P(A)·P(B\|A)` |
| Total probability | `P(A) = Σ P(A\|Bᵢ)·P(Bᵢ)` |
| Union bound | `P(∪Aᵢ) ≤ Σ P(Aᵢ)` |

These fundamentals prepare us for Bayes' theorem and expected value in the next lesson.
