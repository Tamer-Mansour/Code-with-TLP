# Set Operations and Proof Techniques

Formal proofs are the currency of theory of computation. Every claim — from "this language is regular" to "the halting problem is undecidable" — must be established rigorously. This lesson reviews the principal proof techniques and illustrates each with a concrete example from the theory.

## Proof by Construction

To show a language has some property (e.g., is regular, is context-free), you *construct* an automaton or grammar that witnesses the property. This is the most common technique in the first half of the course.

**Example.** Prove that L = {w ∈ {0,1}\* \| w contains the substring 01} is regular.

*Proof.* Construct the DFA M = ({q₀, q₁, q₂}, {0,1}, δ, q₀, {q₂}):

| State | 0 | 1 |
|-------|---|---|
| q₀ (initial: no progress) | q₁ | q₀ |
| q₁ (seen a 0) | q₁ | q₂ |
| q₂ (seen 01, absorb remaining) | q₂ | q₂ |

This DFA accepts iff the input contains "01" as a substring. Since we constructed an explicit DFA, L is regular by definition. ∎

The power of construction proofs is that they are *checkable* — anyone can verify the automaton works correctly by tracing all cases.

## Proof by Mathematical Induction

Mathematical induction proves "P(n) for all n ≥ n₀."

**Structure:**
1. **Base case**: verify P(n₀).
2. **Inductive hypothesis**: assume P(k) holds for some k ≥ n₀.
3. **Inductive step**: using the hypothesis, prove P(k+1).

**Strong induction** assumes P(j) for *all* j with n₀ ≤ j ≤ k, which is useful when the step uses any earlier case, not just the immediate predecessor.

**Example.** Prove that every string w over {0,1} with |w| = n satisfies: the number of substrings of w (including duplicates, including ε and w itself) is at most n(n+1)/2 + 1.

*Base case* (n=0): w = ε. The only substring is ε, so count = 1 ≤ 0(1)/2 + 1 = 1. ✓

*Inductive step*: Assume the bound holds for all strings of length k. Let w have length k+1. Removing the last character gives a string of length k, which by hypothesis has at most k(k+1)/2 + 1 substrings. Appending a new character adds at most k+1 new substrings (all suffixes ending at the new position, of lengths 1 through k+1). So the total is at most k(k+1)/2 + 1 + (k+1) = (k+1)(k+2)/2 + 1. ✓

## Proof by Contradiction

Assume the claim is false; derive a logical contradiction; conclude the claim must be true. This is the workhorse of undecidability and non-regularity proofs.

**Template:**
1. "Assume for contradiction that [claim is false]."
2. [Derive something impossible, like a TM that decides an undecidable language.]
3. "This is a contradiction; therefore [claim is true]."

**Example.** Prove there are infinitely many prime numbers.

*Assume* only finitely many primes p₁, p₂, …, pₙ exist. Let N = p₁·p₂·…·pₙ + 1. N is not divisible by any pᵢ (remainder 1 each time). So N is either prime itself or has a prime factor not in our list. Either way, contradicting the assumption that we listed all primes. ∎

## Proof by Diagonalization

Cantor's diagonalization shows |ℝ| > |ℕ|: suppose for contradiction we list all real numbers in [0,1] as r₁, r₂, r₃, … Construct a new number d where the i-th decimal digit of d differs from the i-th decimal digit of rᵢ. Then d differs from every rᵢ in at least one position, so d is not on the list — contradiction.

In computability, the same idea proves the existence of languages that are not Turing-recognizable:

**Example.** Prove D = {⟨M⟩ \| M does not accept ⟨M⟩} is not Turing-recognizable.

*Proof.* Suppose TM R recognizes D. Ask: does R accept ⟨R⟩?
- If R accepts ⟨R⟩: then ⟨R⟩ ∈ D, meaning R does not accept ⟨R⟩ — contradiction.
- If R does not accept ⟨R⟩: then ⟨R⟩ ∉ D by definition of D… wait — ⟨R⟩ ∈ D requires R does NOT accept ⟨R⟩, so ⟨R⟩ ∈ D but R doesn't accept it — meaning R doesn't recognize D — contradiction.

Either case is impossible, so no such R exists. ∎

This argument is the direct analogue of Cantor's diagonal: we are constructing a language that disagrees with every TM's behaviour on its own encoding.

## Proof by Contradiction via Reduction

To prove language A is undecidable, reduce a known undecidable problem B to A:

1. Assume A is decidable by machine M_A.
2. Construct a machine M_B that uses M_A as a subroutine to decide B.
3. Since B is known undecidable, M_B cannot exist; therefore M_A cannot exist.

This template appears repeatedly in Module 7. The key creative step is designing the "reduction gadget" — the transformation from B instances to A instances.

## Closure Properties

A **class** of languages C is **closed** under operation op if: whenever L ∈ C, op(L) ∈ C; and whenever L₁, L₂ ∈ C, op(L₁, L₂) ∈ C (for binary ops).

| Class | Closed under | Not closed under |
|-------|-------------|-----------------|
| Regular | ∪, ∩, complement, concatenation, Kleene star, reversal, homomorphism | (all ops closed) |
| Context-free | ∪, concatenation, Kleene star, intersection with regular | ∩ of two CFLs, complement |
| Decidable | ∪, ∩, complement, concatenation, Kleene star | (all closed) |
| Turing-recognizable | ∪, concatenation, Kleene star | complement, ∩ with co-recognizable |

Closure proofs typically proceed by constructing a new machine from existing ones. For example, to prove regular languages are closed under intersection: given DFA M₁ and M₂, build the **product DFA** M₁ × M₂ whose states are pairs (q₁, q₂) ∈ Q₁ × Q₂, transitions are δ((q₁,q₂), a) = (δ₁(q₁,a), δ₂(q₂,a)), start is (q₁₀, q₂₀), and accept states are pairs where both components are accepting. This DFA accepts w iff both M₁ and M₂ accept w.

## Element-Chasing Proofs for Language Equalities

The standard technique for proving L₁ = L₂ is to show L₁ ⊆ L₂ and L₂ ⊆ L₁. For each direction, fix an arbitrary w ∈ L₁ and show w ∈ L₂.

**Example.** Prove Ā ∩ B̄ = (A ∪ B)`.

**Forward (⊆):** Let w ∈ Ā ∩ B̄. Then w ∉ A and w ∉ B (definitions of Ā, B̄, and ∩). So it is not the case that (w ∈ A or w ∈ B), i.e., w ∉ A ∪ B, i.e., w ∈ (A ∪ B)`. ✓

**Backward (⊇):** Let w ∈ (A ∪ B)`. Then w ∉ A ∪ B, so w ∉ A and w ∉ B, so w ∈ Ā and w ∈ B̄, so w ∈ Ā ∩ B̄. ✓

This is De Morgan's law for languages, and the proof is completely parallel to its propositional logic counterpart. This parallelism is not a coincidence: the boolean algebra of propositions and the boolean algebra of languages over a fixed Σ have the same structure.

## Pigeonhole Principle

If n items are placed into fewer than n bins, some bin contains at least two items.

In automata theory, the Pigeonhole Principle is the key to the pumping lemmas: if a DFA with p states processes a string of length ≥ p, it must visit some state twice (since there are p+1 or more configurations and only p states). The states are the bins; the time steps are the items. The repeated state is the loop that gets pumped.

## Summary of Proof Techniques

| Technique | Typical use in theory of computation |
|-----------|--------------------------------------|
| Construction | Proving a language IS in some class (build the machine) |
| Induction | Counting, properties of derivations and computations |
| Contradiction | Non-membership proofs, undecidability |
| Diagonalization | Self-reference arguments, undecidability of A_TM |
| Reduction | Propagating undecidability or hardness to new problems |
| Element-chasing | Proving language equalities, closure properties |
| Pigeonhole | Pumping lemmas |
