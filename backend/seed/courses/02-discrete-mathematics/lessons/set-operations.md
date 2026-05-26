# Set Operations

A **set** is an unordered collection of distinct objects called **elements** (or members). Sets are the building blocks of virtually all of mathematics and the formal foundation of data structures, databases, and type theory.

## Notation

- `A = {1, 2, 3}` — listing elements explicitly (roster/extensional notation).
- `B = {x ∈ ℤ | x is even and 0 < x < 10}` — set-builder (intensional) notation; reads "the set of integers x such that…"
- `x ∈ A` means x is an element of A; `x ∉ A` means it is not.
- `|A|` — the **cardinality** of A, i.e., the number of elements (for finite sets).

## Special Sets

| Symbol | Name | Contents |
|--------|------|----------|
| `∅` or `{}` | Empty set | No elements; `|∅| = 0` |
| `ℕ` | Natural numbers | {0, 1, 2, 3, …} (sometimes starting at 1) |
| `ℤ` | Integers | {…, -2, -1, 0, 1, 2, …} |
| `ℚ` | Rationals | Fractions p/q with p, q ∈ ℤ, q ≠ 0 |
| `ℝ` | Reals | All points on the number line |
| `ℂ` | Complex numbers | a + bi |

## Subset and Equality

- `A ⊆ B` (A is a **subset** of B): every element of A is also in B. Formally: `∀x (x ∈ A → x ∈ B)`.
- `A = B` iff `A ⊆ B` and `B ⊆ A` (double containment). This is the standard technique to prove two sets are equal.
- `A ⊂ B` (proper subset): `A ⊆ B` and `A ≠ B`.

Two important facts:
- `∅ ⊆ A` for every set A (vacuously true: there is no element in ∅ that violates the condition).
- `A ⊆ A` always (every set is a subset of itself).

## Core Operations

### Union
`A ∪ B = {x | x ∈ A  or  x ∈ B}`

Everything in either set. Analogous to logical disjunction `∨`. In SQL this corresponds to `UNION`.

### Intersection
`A ∩ B = {x | x ∈ A  and  x ∈ B}`

Only what both sets share. Analogous to conjunction `∧`. SQL: `INTERSECT` or `JOIN`.

### Difference (Relative Complement)
`A \ B = {x | x ∈ A  and  x ∉ B}`

Elements in A but not in B. Also written `A − B`. SQL: `EXCEPT`.

### Complement
`Aᶜ = U \ A`

Everything in the **universal set** U that is not in A. The universal set must be declared explicitly.

### Symmetric Difference
`A △ B = (A \ B) ∪ (B \ A) = (A ∪ B) \ (A ∩ B)`

Elements in exactly one of the two sets — those in A or B but not both. Corresponds to XOR (`⊕`).

### Cartesian Product
`A × B = {(a, b) | a ∈ A and b ∈ B}`

The set of all ordered pairs. If `|A| = m` and `|B| = n`, then `|A × B| = mn`.

**Example:** `{1,2} × {a,b} = {(1,a), (1,b), (2,a), (2,b)}`

Cartesian products generalize: `A × B × C` contains ordered triples, and `Aⁿ` (A to the n-th power) is the set of all n-tuples. This is exactly the set of all strings of length n over alphabet A.

## Worked Example

Let `U = {1,2,3,4,5,6}`, `A = {1,2,3,4}`, `B = {3,4,5,6}`.

| Operation | Result | Size |
|-----------|--------|------|
| `A ∪ B` | `{1,2,3,4,5,6}` | 6 |
| `A ∩ B` | `{3,4}` | 2 |
| `A \ B` | `{1,2}` | 2 |
| `B \ A` | `{5,6}` | 2 |
| `A △ B` | `{1,2,5,6}` | 4 |
| `Aᶜ` | `{5,6}` | 2 |
| `Bᶜ` | `{1,2}` | 2 |

Notice: `|A ∪ B| = |A| + |B| - |A ∩ B| = 4 + 4 - 2 = 6` ✓ (inclusion-exclusion).

## Venn Diagrams

Venn diagrams visualize set relationships using overlapping circles inside a rectangle (the universal set). Each region corresponds to a logical combination:

```
  U = [  A only  |  A ∩ B  |  B only  |  neither  ]
```

Venn diagrams are excellent for sanity-checking set identities with small examples, but they are **not** formal proofs. A proof requires the double-containment technique or algebraic manipulation.

## Important Set Identities

| Identity | Name |
|----------|------|
| `A ∪ ∅ = A`, `A ∩ U = A` | Identity laws |
| `A ∪ U = U`, `A ∩ ∅ = ∅` | Domination laws |
| `A ∪ A = A`, `A ∩ A = A` | Idempotent laws |
| `(Aᶜ)ᶜ = A` | Double complement |
| `A ∪ B = B ∪ A`, `A ∩ B = B ∩ A` | Commutativity |
| `(A ∪ B) ∪ C = A ∪ (B ∪ C)` | Associativity |
| `A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)` | Distributive |
| `(A ∪ B)ᶜ = Aᶜ ∩ Bᶜ` | De Morgan (set form) |
| `(A ∩ B)ᶜ = Aᶜ ∪ Bᶜ` | De Morgan (set form) |

These mirror the Boolean algebra laws for propositions exactly — union ↔ ∨, intersection ↔ ∧, complement ↔ ¬.

## Proving a Set Identity

**Claim:** `A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C)` (distributivity of ∩ over ∪).

**Proof (element-based):** Let x be arbitrary.

Forward direction (⊆): Assume `x ∈ A ∩ (B ∪ C)`. Then `x ∈ A` and `x ∈ B ∪ C`.
- Case 1: `x ∈ B`. Then `x ∈ A` and `x ∈ B`, so `x ∈ A ∩ B ⊆ (A ∩ B) ∪ (A ∩ C)`.
- Case 2: `x ∈ C`. Then `x ∈ A ∩ C ⊆ (A ∩ B) ∪ (A ∩ C)`.

Backward direction (⊇): Assume `x ∈ (A ∩ B) ∪ (A ∩ C)`.
- Case 1: `x ∈ A ∩ B`. Then `x ∈ A` and `x ∈ B ⊆ B ∪ C`, so `x ∈ A ∩ (B ∪ C)`.
- Case 2: `x ∈ A ∩ C`. Then `x ∈ A` and `x ∈ C ⊆ B ∪ C`, so `x ∈ A ∩ (B ∪ C)`.

Both inclusions hold, so the sets are equal. QED.

## Power Set

The **power set** of A, written `P(A)` or `2^A`, is the set of all subsets of A.

If `|A| = n`, then `|P(A)| = 2^n`.

**Example:** `A = {1, 2, 3}`.
```
P(A) = { ∅, {1}, {2}, {3}, {1,2}, {1,3}, {2,3}, {1,2,3} }
```
That is `2^3 = 8` subsets.

**Why 2^n?** For each of the n elements, you independently choose to include it or not — 2 choices, n times.

**CS application:** The power set models the state space of a Boolean vector of length n (e.g., a bitmask). Iterating over all subsets is `Θ(2^n)` — intractable for large n, which is why subset-sum and other subset problems are NP-complete.

## Inclusion-Exclusion Principle (General)

For three sets:
```
|A ∪ B ∪ C| = |A| + |B| + |C|
             − |A∩B| − |A∩C| − |B∩C|
             + |A∩B∩C|
```

For n sets, the pattern alternates between adding and subtracting cardinalities of overlapping groups:
```
|A₁ ∪ A₂ ∪ … ∪ Aₙ| = Σ|Aᵢ| − Σ|Aᵢ∩Aⱼ| + Σ|Aᵢ∩Aⱼ∩Aₖ| − …
```

**Application:** How many integers from 1 to 100 are divisible by 2, 3, or 5?

- `|A₂| = 50`, `|A₃| = 33`, `|A₅| = 20`
- `|A₆| = 16` (divisible by 6), `|A₁₀| = 10`, `|A₁₅| = 6`
- `|A₃₀| = 3`
- Total = `50 + 33 + 20 − 16 − 10 − 6 + 3 = 74`

## Summary

Set operations are the Boolean algebra of collections. They underlie:
- **Database query logic** (JOIN ≈ intersection, UNION, EXCEPT ≈ difference).
- **Type theory** (union types, intersection types, complement types for negation).
- **Formal language theory** (regular languages are closed under union, intersection, complement).
- **Counting and probability** (inclusion-exclusion is the core tool for counting overlapping cases).
