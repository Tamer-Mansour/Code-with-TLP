# Functions and Cardinality

## Functions

A **function** `f: A → B` assigns to every element `a ∈ A` (the **domain**) exactly one element `f(a) ∈ B` (the **codomain**). The set of all output values actually produced is the **range** (or image): `range(f) = { f(a) | a ∈ A }`.

The range need not equal the codomain. For instance, `f: ℝ → ℝ` defined by `f(x) = x²` has codomain ℝ but range `[0, ∞)` — negative outputs are never produced.

### Injective (One-to-One)

No two distinct inputs share the same output:
```
f(a₁) = f(a₂)  ⟹  a₁ = a₂
```
Equivalently, distinct inputs produce distinct outputs. An injective function "spreads" the domain into the codomain without collisions.

**Example:** `f: ℤ → ℤ, f(n) = 2n` is injective (every even integer is hit at most once).

**Example:** `f: ℝ → ℝ, f(x) = x²` is NOT injective: `f(2) = f(-2) = 4`.

**CS application:** A perfect hash function is injective — no two distinct keys produce the same hash, eliminating collisions.

### Surjective (Onto)

Every element of the codomain is the image of at least one domain element:
```
∀b ∈ B, ∃a ∈ A: f(a) = b
```
The range equals the codomain.

**Example:** `f: ℤ → ℤ, f(n) = n - 5` is surjective (every integer is hit: `f(b+5) = b`).

**Example:** `f: ℝ → ℝ, f(x) = x²` is NOT surjective onto ℝ (no real squares to -1).

**CS application:** A hash function from keys to `{0, …, m-1}` should ideally be surjective so no bucket is wasted.

### Bijective (One-to-One Correspondence)

Both injective and surjective. A bijection is a perfect pairing — every element of A maps to a unique element of B, and every element of B is mapped to.

| Domain A | Codomain B | Bijective? | Reason |
|----------|------------|-----------|--------|
| {1,2,3} | {a,b,c} | Yes (with right mapping) | Same size |
| {1,2,3} | {a,b} | No | Can't be injective (3 inputs, 2 outputs) |
| {1,2} | {a,b,c} | No | Can't be surjective (2 inputs, 3 outputs) |

**Key fact:** For finite sets, a bijection `f: A → B` exists iff `|A| = |B|`. For infinite sets, bijections define equal cardinality.

### Inverse Functions

If `f: A → B` is bijective, its **inverse** `f⁻¹: B → A` satisfies:
```
f⁻¹(f(a)) = a  for all a ∈ A
f(f⁻¹(b)) = b  for all b ∈ B
```

Only bijections have inverses that are also functions. A non-injective function has no left inverse (two inputs share an output — which one does the inverse pick?). A non-surjective function has no right inverse (some outputs are never produced — the inverse has no input for them).

### Composition

`(g ∘ f)(x) = g(f(x))`. Read right-to-left: apply f first, then g.

If `f: A → B` and `g: B → C`, then `g ∘ f: A → C`.

**Preservation of injectivity/surjectivity:**
- If `g ∘ f` is injective, then f must be injective.
- If `g ∘ f` is surjective, then g must be surjective.
- If f and g are both injective (or both surjective, or both bijective), so is `g ∘ f`.

**Example:** Composing two bijections always gives a bijection — crucial for cryptographic key composition.

## Counting Functions

Given finite sets A and B with `|A| = m` and `|B| = n`:

| Type | Count | Formula |
|------|-------|---------|
| All functions A → B | Each of m inputs independently picks 1 of n outputs | `n^m` |
| Injections (one-to-one) | First input picks any of n; second picks n-1; etc. | `n · (n-1) · … · (n-m+1) = P(n,m)` — requires `n ≥ m` |
| Surjections (onto) | Inclusion-exclusion | Complex; at least `n! · S(m,n)` where S is a Stirling number |
| Bijections | Only when `m = n` | `n!` |

**Example:** How many functions from {0,1}³ (3 bits) to {0,1} exist? `2^3 = 8` possible inputs, each independently maps to 0 or 1 → `2^8 = 256` Boolean functions of 3 variables. This is why the truth table of a 3-variable Boolean formula has 8 rows.

## Cardinality

Two sets have the same **cardinality** (size) if there exists a bijection between them. For finite sets this coincides with the element count. For infinite sets it requires careful construction of bijections.

### Finite Cardinality Rules

For finite sets A and B:
- `|A ∪ B| = |A| + |B| - |A ∩ B|` (inclusion-exclusion)
- `|A × B| = |A| · |B|`
- `|P(A)| = 2^|A|` (power set)
- Number of functions A → B: `|B|^|A|`

### Countably Infinite Sets

A set S is **countably infinite** if there is a bijection between S and ℕ. Such sets can be listed: `s₀, s₁, s₂, …` where every element eventually appears.

**ℤ is countable:** Define `f: ℕ → ℤ` by `f(2k) = k` and `f(2k+1) = -(k+1)`. Listing: `0, 1, -1, 2, -2, 3, -3, …`

**ℚ is countable:** Arrange fractions in a grid and enumerate by diagonals, skipping duplicates. This is Cantor's enumeration. Any finite union or Cartesian product of countable sets is countable.

**Important:** A subset of a countable set is countable. The set of all programs in any language is countable (programs are finite strings over a finite alphabet).

### Uncountable Sets

**ℝ is uncountably infinite** — no bijection with ℕ exists.

**Cantor's diagonal argument (full proof):**

Suppose for contradiction that all real numbers in `(0, 1)` can be listed: `x₁, x₂, x₃, …`. Write each in decimal:
```
x₁ = 0.d₁₁ d₁₂ d₁₃ d₁₄ …
x₂ = 0.d₂₁ d₂₂ d₂₃ d₂₄ …
x₃ = 0.d₃₁ d₃₂ d₃₃ d₃₄ …
…
```
Construct `y = 0.e₁ e₂ e₃ …` where `eₙ = 5` if `dₙₙ ≠ 5`, else `eₙ = 6`. Then y differs from every listed xₙ in the nth decimal place, so y is not on the list. But `y ∈ (0,1)` — contradiction. QED.

**Consequence for CS:** The set of all computable functions is countable (one per program), but the set of all functions `ℕ → ℕ` is uncountable. Therefore, most mathematical functions are **not computable** by any program. This is the theoretical foundation of the Halting Problem and undecidability.

### Comparing Infinite Cardinalities

| Set | Cardinality | Symbol |
|-----|-------------|--------|
| ℕ, ℤ, ℚ, all finite-length strings | Countably infinite | ℵ₀ |
| ℝ, ℂ, P(ℕ), all functions ℕ→{0,1} | Uncountably infinite | 𝔠 = 2^ℵ₀ |

**Cantor's theorem:** For any set A, `|P(A)| > |A|`. There is no largest cardinality — the power set always jumps to a strictly larger infinity. This implies an infinite hierarchy: `ℵ₀ < 2^ℵ₀ < 2^{2^ℵ₀} < …`

### Schröder-Bernstein Theorem (statement)

If there exist injections `f: A → B` and `g: B → A`, then there exists a bijection `h: A → B`. In other words, `|A| ≤ |B|` and `|B| ≤ |A|` together imply `|A| = |B|`. This is the tool for proving two infinite sets have the same cardinality without constructing an explicit bijection.

## Worked Example: Pigeonhole Principle

If `f: A → B` is a function with `|A| > |B|`, then f cannot be injective — at least two elements of A map to the same element of B.

**Example:** Among 13 people, at least 2 share a birth month (|people| = 13 > 12 = |months|).

**Generalized pigeonhole:** Among n people placed into k months, at least `⌈n/k⌉` share a month.

**Birthday paradox:** With 23 people in a room, the probability two share a birthday exceeds 50%. The pigeonhole principle guarantees a collision once you have 366+ people, but probability makes it likely much sooner.

## Summary

- A function assigns each input exactly one output; its injectivity, surjectivity, and bijectivity determine how "spread out" the mapping is.
- Bijections are the key tool for comparing sizes of sets, finite or infinite.
- Infinite sets come in multiple "sizes" — countable (ℕ, ℤ, ℚ) and uncountable (ℝ) — with far-reaching implications for computability.
- Cantor's diagonal argument is a model proof technique used in many undecidability results in theoretical computer science.
