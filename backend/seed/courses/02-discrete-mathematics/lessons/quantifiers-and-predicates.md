# Quantifiers and Predicates

Propositional logic cannot express statements like "Every even number is divisible by 2" or "There exists a prime greater than 100." For these we need **predicate logic** (also called first-order logic), which adds variables, predicates, and quantifiers to propositional logic.

Predicate logic is the language of mathematics and formal specification. Almost every theorem you will encounter in a discrete mathematics or algorithms course is written in predicate logic, whether or not the symbols appear explicitly.

## Predicates

A **predicate** is a statement with one or more free variables — it becomes a proposition once the variables are bound to specific values. We write `P(x)` to mean "predicate P applied to x."

- `P(x)` : "`x` is a prime number" — `P(7)` is **true**; `P(6)` is **false**.
- `Q(x, y)` : "`x` divides `y`" — `Q(3, 9)` is **true**; `Q(3, 10)` is **false**.
- `R(n)` : "`n` is a valid array index (0 ≤ n < len)" — depends on the runtime context.

A predicate with k variables is called a **k-ary** predicate. Binary predicates express relations between two objects.

## The Universal Quantifier — ∀

`∀x P(x)` reads "**for all** x, P(x) is true." It asserts P holds for every element of the **domain of discourse** (the set of values x ranges over). The domain must always be specified or clear from context.

**Example** (domain = positive integers):
`∀x (x + 1 > x)` — True, since adding 1 always increases a positive integer.

**Example** (domain = real numbers):
`∀x (x² ≥ 0)` — True for all reals.

**Disproving a universal statement:** A single **counterexample** suffices.
- To disprove `∀x (x² > x)` over the reals, note `x = 0.5` gives `0.25 < 0.5`. Done.

## The Existential Quantifier — ∃

`∃x P(x)` reads "**there exists** an x such that P(x) is true." It asserts at least one domain element satisfies P.

**Example** (domain = integers):
`∃x (x² = 4)` — True, because `x = 2` (and `x = -2`) work.

**Proving an existential statement:** Find at least one concrete witness.
**Disproving an existential statement:** Show P(x) fails for every element — which often requires a general argument.

## Negating Quantifiers (Quantifier Duality)

The negation of a quantified statement swaps the quantifier and negates the body:

| Statement | Negation |
|-----------|----------|
| `∀x P(x)` | `∃x ¬P(x)` |
| `∃x P(x)` | `∀x ¬P(x)` |

These are the quantifier analogues of De Morgan's Laws.

**Example:** The negation of `∀x (x ≥ 0)` is `∃x (x < 0)`.

**Common pitfall:** The negation of "Every student passed" is NOT "No student passed" — it is "There exists at least one student who did not pass."

**Nested negation example:**
```
¬(∀x ∃y (y > x))
= ∃x ¬(∃y (y > x))
= ∃x ∀y ¬(y > x)
= ∃x ∀y (y ≤ x)
```
This says "there is an x that is an upper bound for the entire domain" — false over the integers, since no integer is ≥ all integers.

## Nested Quantifiers

When two quantifiers appear, their **order** matters significantly.

| Formula | Meaning | Truth over ℤ |
|---------|---------|-------------|
| `∀x ∃y (y > x)` | For every x, there is some larger y | **True** (y = x+1 always works) |
| `∃y ∀x (y > x)` | There is a single y larger than all x | **False** (no largest integer) |
| `∀x ∀y (x + y = y + x)` | Addition is commutative | **True** |
| `∃x ∃y (x + y = 5)` | Some two integers sum to 5 | **True** |

Swapping `∀` and `∃` can entirely reverse the truth value. This is one of the most important insights in predicate logic.

### Reading Strategy for Nested Quantifiers

Read left to right. Each `∀` introduces an "adversary" that picks the worst value; each `∃` introduces an "ally" that picks the best value.

- `∀x ∃y (y > x)` — adversary picks any x; ally responds with y = x+1. True.
- `∃y ∀x (y > x)` — ally must commit to one y first; adversary then picks y+1 as x. False.

## Worked Example: Translating English to Logic

**Sentence:** "Every prime greater than 2 is odd."

Let the domain be all integers. Let `P(n)` = "n is prime", `G(n)` = "n > 2", `O(n)` = "n is odd."

**Translation:** `∀n (P(n) ∧ G(n) → O(n))`

**Sentence:** "There is no largest real number."

**Translation:** `∀x ∃y (y > x)` — for every real x, there is a larger real y.

**Sentence:** "Some courses are hard but not all courses are boring."

Let `H(x)` = "course x is hard", `B(x)` = "course x is boring."

**Translation:** `(∃x H(x)) ∧ (∃x ¬B(x))`

(Equivalently, using negation of universal: `(∃x H(x)) ∧ ¬(∀x B(x))`)

## The Uniqueness Quantifier — ∃!

`∃!x P(x)` means "**there exists exactly one** x such that P(x)." Formally:
```
∃!x P(x)  ≡  ∃x (P(x) ∧ ∀y (P(y) → y = x))
```

**Example:** `∃!x (x² = 0)` over the integers — True; only x = 0 satisfies it.
**Example:** `∃!x (x² = 4)` over the integers — False; both x = 2 and x = -2 work.

## Predicate Logic and Computer Science

Predicate logic is foundational to several CS areas:

- **Databases:** SQL `WHERE` clauses are quantified predicates over table rows. `SELECT * FROM Students WHERE grade > 90` is `∃row (grade(row) > 90)`.
- **Loop invariants:** An invariant `P(i)` is true `∀i` in range — the assertion is universally quantified over loop iterations.
- **Type systems:** A type system asserts `∀e (well-typed(e) → ¬crashes(e))`.
- **Contracts / Hoare logic:** Preconditions and postconditions are predicates; the statement `{P} C {Q}` says "if P holds before C executes, then Q holds after."
- **SAT / SMT solvers:** Tools like Z3 reason about satisfiability of first-order formulas automatically, powering program verification.

## Worked Proof Using Quantifiers

**Theorem:** For all integers n, if n² is even then n is even.

**Formal statement:** `∀n (Even(n²) → Even(n))`

**Proof by contrapositive:** We prove `¬Even(n) → ¬Even(n²)`, i.e., "if n is odd then n² is odd."

Assume n is odd: `∃k (n = 2k + 1)`. Then:
```
n² = (2k+1)² = 4k² + 4k + 1 = 2(2k² + 2k) + 1
```
This has the form `2m + 1`, so n² is odd, i.e., `¬Even(n²)`. QED.

## Common Mistakes

| Mistake | Correct approach |
|---------|-----------------|
| Ignoring the domain of discourse | Always state or infer what x ranges over |
| Confusing ∀x ∃y and ∃y ∀x | These have completely different meanings |
| Negating ∀x P(x) as ∀x ¬P(x) | Correct negation is ∃x ¬P(x) |
| Confusing "there exists a unique" with "there exists" | ∃! is strictly stronger than ∃ |

## Summary

| Quantifier | Symbol | True when |
|------------|--------|-----------|
| Universal | `∀x P(x)` | P holds for every element |
| Existential | `∃x P(x)` | P holds for at least one element |
| Uniqueness | `∃!x P(x)` | P holds for exactly one element |

Mastery of predicates and quantifiers is essential for reading proofs, writing formal specifications, and understanding the semantics of programming languages throughout computer science.
