# CFL Closure Properties and the Pumping Lemma

Context-free languages (CFLs) enjoy several closure properties, but — unlike regular languages — are **not** closed under intersection or complement. Understanding exactly where closure breaks down is as important as knowing where it holds.

## Closure Properties of CFLs

| Operation | CFL closed? | Proof method |
|-----------|------------|-------------|
| Union L₁ ∪ L₂ | **Yes** | Grammar merge |
| Concatenation L₁·L₂ | **Yes** | Grammar merge |
| Kleene star L\* | **Yes** | Grammar extension |
| Reversal Lᴿ | **Yes** | Reverse all rule RHS |
| Intersection with a regular language | **Yes** | PDA × DFA product |
| Intersection of two CFLs | **No** | Counterexample |
| Complement of a CFL | **No** | Follows from intersection |
| Homomorphism | **Yes** | Replace terminals in rules |

### Union (Grammar Merge)

Given G₁ = (V₁, Σ, R₁, S₁) and G₂ = (V₂, Σ, R₂, S₂) with disjoint variable sets, build G = (V₁ ∪ V₂ ∪ {S}, Σ, R₁ ∪ R₂ ∪ {S → S₁ \| S₂}, S).

L(G) = L(G₁) ∪ L(G₂). The new start variable S nondeterministically chooses which grammar to use.

### Concatenation

Add rules S → S₁S₂. Then L(G) = L(G₁)·L(G₂).

### Kleene Star

Add rules S → SS₁ \| ε. (Or equivalently S → S₁S \| ε.) Then L(G) = L(G₁)\*.

### Intersection with a Regular Language (PDA × DFA Product)

**Theorem.** If L is a CFL and R is regular, then L ∩ R is context-free.

**Proof.** Let P = (Q_P, Σ, Γ, δ_P, q_P, F_P) be a PDA for L and D = (Q_D, Σ, δ_D, q_D, F_D) be a DFA for R. Construct PDA P' with:
- States: Q_P × Q_D (track both automata simultaneously)
- Start: (q_P, q_D)
- Transitions: if (q', γ) ∈ δ_P(q, a, s) and r' = δ_D(r, a), then (q', γ) ∈ δ_{P'}((q,r), a, s)
- Accept: F_P × F_D

P' accepts w iff P accepts w and D accepts w, i.e., w ∈ L ∩ R. ∎

This construction is extremely useful in practice: it lets us intersect a context-free language with a regular constraint (e.g., "strings in L that also match some pattern") and keep the result context-free.

### Non-Closure Under Intersection

**Example:** Let
- L₁ = {aⁿbⁿcᵐ \| n, m ≥ 0}: context-free (equal a's and b's; c's are unconstrained).
- L₂ = {aᵐbⁿcⁿ \| n, m ≥ 0}: context-free (a's unconstrained; equal b's and c's).

Both are CFLs. Their intersection: L₁ ∩ L₂ = {aⁿbⁿcⁿ \| n ≥ 0}.

We will prove {aⁿbⁿcⁿ} is NOT a CFL using the CFL pumping lemma, so CFLs are not closed under intersection. ∎

### Non-Closure Under Complement

If CFLs were closed under complement, they would be closed under intersection (via De Morgan: L₁ ∩ L₂ = complement of (complement(L₁) ∪ complement(L₂))). Since they're not closed under intersection, they're not closed under complement. ∎

## Pumping Lemma for Context-Free Languages

**Theorem (Bar-Hillel, Perles, Shamir, 1961).** If L is a CFL, there exists a pumping length p ≥ 1 such that every string s ∈ L with |s| ≥ p can be written s = uvxyz where:

1. |vy| ≥ 1 (at least one of v, y is non-empty)
2. |vxy| ≤ p (the "middle" portion is bounded)
3. For all i ≥ 0, uvⁱxyⁱz ∈ L (v and y are pumped *together*)

### Proof Sketch

Convert G to CNF. Let |V| = k (number of variables). Set p = 2^k. If s ∈ L with |s| ≥ p = 2^k, then any parse tree for s has height ≥ k+1 (since a CNF tree of height h has at most 2^h leaves). By the Pigeonhole Principle, some variable A appears at least twice on the path from root to the deepest leaf.

Let R be the deepest repeated variable. The two occurrences of R define:
- **x**: the yield of the deeper R subtree
- **vxy**: the yield of the shallower R subtree (so v is to the left of x, y to the right)
- **u** and **z**: the remaining prefix and suffix of s

Since R can be expanded to itself any number of times (using the shallower subtree's path), uvⁱxyⁱz is derived for all i ≥ 0. Setting i=0 gives uxz ∈ L (the deeper R used directly by the shallower rule's context). ∎

## Example 1: {aⁿbⁿcⁿ | n ≥ 0} is Not Context-Free

**Proof.** Assume L is a CFL with pumping length p. Choose s = aᵖbᵖcᵖ ∈ L (|s| = 3p ≥ p).

Consider any split s = uvxyz with |vy| ≥ 1 and |vxy| ≤ p. Since |vxy| ≤ p and the string has three blocks each of length p, the substring vxy spans **at most two** of the three blocks (it cannot reach from the a-block through the b-block to the c-block in p characters).

**Case 1**: vxy ⊆ aᵖbᵖ (lies entirely in the a's and b's). Then v and y together contain only a's and b's. Pumping with i=2 increases the count of a's, b's, or both, but NOT c's. So uv²xy²z has more a's or b's than c's → ∉ L.

**Case 2**: vxy ⊆ bᵖcᵖ (lies entirely in the b's and c's). Similarly, pumping increases b's or c's but not a's → ∉ L.

**Case 3**: vxy ⊆ aᵖ only. Pumping increases only a's → ∉ L.

(And symmetric cases for only b's or only c's.) All cases lead to contradiction. ∎

## Example 2: {ww | w ∈ {a,b}*} is Not Context-Free

**Proof.** Let p be the pumping length. Choose s = aᵖbᵖaᵖbᵖ (so w = aᵖbᵖ).

|s| = 4p ≥ p. Consider any split s = uvxyz with |vy| ≥ 1, |vxy| ≤ p.

Since |vxy| ≤ p, the substring vxy cannot straddle the exact midpoint of s (position 2p). The midpoint separates the two copies of w = aᵖbᵖ. So vxy lies entirely in the first half (positions 1..2p) or entirely in the second half (positions 2p+1..4p), or it straddles the midpoint but cannot reach both copies' matching structure.

Pump with i=2: the first half grows (or the second half grows) while the other stays the same → the two halves are no longer equal → uv²xy²z ∉ {ww}. Contradiction. ∎

## CFL Hierarchy Summary

> Regular ⊊ Context-Free ⊊ Deterministic Context-Free ⊊ ... wait, actually:

The correct picture:

```
Regular ⊊ Deterministic CFL ⊊ CFL ⊊ Decidable ⊊ Turing-recognizable ⊊ All languages
```

Each inclusion is proper:
- {aⁿbⁿ} ∈ CFL \ Regular
- {wwᴿ} ∈ CFL but not deterministic CFL (requires nondeterminism to guess the midpoint)
- {aⁿbⁿcⁿ} ∈ Decidable \ CFL (a TM can count all three groups)
- A_TM ∈ Turing-recognizable \ Decidable
- The diagonal language D ∈ All \ Turing-recognizable

Closure properties reveal and confirm these distinctions: CFLs are not closed under intersection (so {aⁿbⁿcⁿ} ∉ CFL is consistent), but regular languages are.
