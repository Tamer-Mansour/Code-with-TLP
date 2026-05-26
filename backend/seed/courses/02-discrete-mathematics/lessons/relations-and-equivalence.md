# Relations and Equivalence

A **binary relation** R from set A to set B is a subset of the Cartesian product `A × B`. We write `a R b` (equivalently, `(a, b) ∈ R`) to mean "a is related to b." Relations generalize the notion of a function — they describe connections between elements without requiring the input-output structure.

## Properties of Relations on a Set

When the relation is from A to itself (`R ⊆ A × A`), we examine its structural properties:

| Property | Formal definition | Informal meaning | Example |
|----------|------------------|------------------|---------|
| **Reflexive** | `∀a ∈ A: a R a` | Every element relates to itself | `=` on ℤ; `≤` on ℤ |
| **Irreflexive** | `∀a ∈ A: ¬(a R a)` | No element relates to itself | `<` on ℤ; "is a proper subset of" |
| **Symmetric** | `∀a,b: a R b → b R a` | Relating goes both ways | "is a sibling of" |
| **Antisymmetric** | `∀a,b: a R b ∧ b R a → a = b` | Both directions only if equal | `≤` on ℤ; `⊆` on sets |
| **Transitive** | `∀a,b,c: a R b ∧ b R c → a R c` | The chain carries forward | "ancestor of"; `<` |

A relation can satisfy multiple properties simultaneously — or none at all. For instance, `=` is reflexive, symmetric, and transitive; `<` is irreflexive, antisymmetric, and transitive; and the "is acquainted with" relation among strangers could be symmetric but neither reflexive nor transitive.

### Quick Checks via Matrices

Represent R on a finite set `{1,…,n}` as an n×n matrix M where `M[i][j] = 1` iff `i R j`.

- **Reflexive:** All diagonal entries are 1.
- **Symmetric:** The matrix equals its own transpose: `M = Mᵀ`.
- **Antisymmetric:** For `i ≠ j`, M[i][j] and M[j][i] cannot both be 1.
- **Transitive:** M² (Boolean matrix multiply) has no 1 that M lacks.

## Equivalence Relations

A relation is an **equivalence relation** if it is reflexive, symmetric, **and** transitive. Equivalence relations formalize the notion of "being the same in some respect."

**Examples:**
- Equality (`=`): the finest equivalence — only equal elements are related.
- Congruence modulo n: `a ≡ b (mod n)` iff `n | (a - b)`.
- "Has the same parity": even numbers are equivalent to each other, odd to each other.
- Graph isomorphism: two graphs are equivalent if one can be relabeled to match the other.

### Equivalence Classes

For an equivalence relation R on set A, the **equivalence class** of element a is:
```
[a] = { x ∈ A | x R a }
```

**Fundamental theorem of equivalence classes:** The equivalence classes of R form a **partition** of A — they are pairwise disjoint and their union is all of A. Conversely, every partition of A defines an equivalence relation.

**Proof sketch:** 
- Each a belongs to [a] (reflexivity), so every element is in some class.
- If `[a] ∩ [b] ≠ ∅`, pick `c ∈ [a] ∩ [b]`. Then `c R a` and `c R b`. By symmetry and transitivity, `a R b`, so `[a] = [b]`.
Hence classes are either identical or disjoint.

**Example: Congruence mod 3 on ℤ.** The three classes are:
```
[0] = {…, -6, -3, 0, 3, 6, …}  (multiples of 3)
[1] = {…, -5, -2, 1, 4, 7, …}  (≡ 1 mod 3)
[2] = {…, -4, -1, 2, 5, 8, …}  (≡ 2 mod 3)
```
Every integer belongs to exactly one class. The **quotient set** `ℤ / 3ℤ = {[0], [1], [2]}` — this is the foundation of modular arithmetic (working with these classes as objects).

**CS application:** Hash tables partition keys by their hash value — a form of equivalence class. Two keys in the same "bucket" are not truly equivalent, but they are assigned to the same slot, which defines a practical partition.

## Partial and Total Orders

A relation that is reflexive, antisymmetric, and transitive is a **partial order**, written `(A, ≤)` or `poset` (partially ordered set).

- **Partial order:** `⊆` on the power set of a set — not every two subsets are comparable (e.g., `{1,2}` and `{2,3}` are incomparable under `⊆`).
- **Total order (linear order):** Every two elements are comparable. `≤` on ℤ is a total order.

A **strict partial order** uses `<` (irreflexive, antisymmetric, transitive).

### Hasse Diagrams

A **Hasse diagram** represents a partial order visually:
- Vertices are elements.
- An edge goes up from x to y if y **covers** x (i.e., `x < y` and no z with `x < z < y` exists).
- Transitivity is implicit — you don't draw edges that can be inferred by chains.

**Example:** The divisibility relation on `{1, 2, 3, 4, 6, 12}`:
```
        12
       /  \
      4    6
      |   / \
      2  3   (implied by transitivity)
       \ |
        ...
```

## Functions as Relations

A **function** `f: A → B` is a relation where every element of A relates to **exactly one** element of B. All functions are relations, but not all relations are functions.

| Property | Definition |
|----------|-----------|
| **Injective** (one-to-one) | `f(a₁) = f(a₂) → a₁ = a₂` |
| **Surjective** (onto) | `∀b ∈ B, ∃a ∈ A: f(a) = b` |
| **Bijective** | Both injective and surjective |

A bijection between finite sets implies they have the same size. This is the formal definition of "same cardinality."

## Composition of Relations

For relations R ⊆ A × B and S ⊆ B × C, their **composition** is:
```
S ∘ R = { (a,c) | ∃b ∈ B: (a,b) ∈ R and (b,c) ∈ S }
```

Note: the notation `S ∘ R` means "apply R first, then S" — right-to-left, matching function composition.

**Matrix representation:** If M_R and M_S are the Boolean matrices of R and S, then `M_{S∘R} = M_R ⊗ M_S` (Boolean matrix product).

**Transitive closure:** `R⁺ = R ∪ R² ∪ R³ ∪ …` — the smallest transitive relation containing R. This is computed by Floyd-Warshall or repeated matrix multiplication in `O(n³)`.

## Worked Example: Modular Congruence

Is `≡ (mod 4)` an equivalence relation on ℤ?

- **Reflexive:** `a - a = 0 = 4·0`, so `4 | (a - a)`, hence `a ≡ a`. ✓
- **Symmetric:** If `4 | (a - b)`, then `4 | (-(a-b)) = (b - a)`, so `b ≡ a`. ✓
- **Transitive:** If `4 | (a - b)` and `4 | (b - c)`, then `4 | ((a-b) + (b-c)) = (a-c)`. ✓

Yes, it is an equivalence relation. The four equivalence classes are `[0], [1], [2], [3]` — the integers modulo 4. These are the elements of the algebraic structure `ℤ/4ℤ`, which underpins modular arithmetic in computing (e.g., how a 4-bit unsigned integer wraps around).

## Cardinality and Cantor's Theorem

For **finite** sets, `|A|` is simply the count. Two sets have the **same cardinality** if there is a bijection between them — this definition extends to infinite sets.

| Set | Cardinality label | Symbol |
|-----|------------------|--------|
| Any finite set of size n | Finite | n |
| ℕ, ℤ, ℚ | Countably infinite | ℵ₀ (aleph-null) |
| ℝ, P(ℕ) | Uncountably infinite | 𝔠 (the cardinality of the continuum) |

**ℤ is countably infinite:** List as `0, 1, -1, 2, -2, 3, -3, …` — a bijection with ℕ exists.

**ℚ is countably infinite:** Cantor's diagonal enumeration: arrange fractions in a grid (row = numerator, column = denominator) and snake through diagonals.

**ℝ is uncountably infinite:** Cantor's diagonal argument shows no list can enumerate all reals in `[0,1]`.

**Cantor's theorem:** `|P(A)| > |A|` for every set A. There is no largest infinity — the power set always produces a strictly larger cardinality. This has profound implications: the set of all programs is countable (programs are finite strings over a finite alphabet), but the set of all functions `ℕ → ℕ` is uncountable — proving that most mathematical functions cannot be computed by any program.

## Summary

Relations formalize connections between elements. Equivalence relations create natural partitions, partial orders capture hierarchies, and functions (as special relations) are the workhorse of all mathematics. The concepts here underlie type inference, database indexing, topological sorting, and the theory of computability.
