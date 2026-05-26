# The Pumping Lemma for Regular Languages

The pumping lemma is the standard tool for proving that a language is **not** regular. It provides a necessary condition: every regular language satisfies the pumping property. If a language fails the property, it cannot be regular. The proof exploits the pigeonhole principle applied to a DFA's finite state set.

## The Theorem

**Pumping Lemma (Bar-Hillel, Perles, Shamir, 1961).** If L is a regular language, then there exists a **pumping length** p ≥ 1 (depending on L) such that every string s ∈ L with |s| ≥ p can be written s = xyz satisfying all three conditions simultaneously:

1. |y| ≥ 1 (the pumped portion y is non-empty)
2. |xy| ≤ p (the pump occurs within the first p symbols)
3. For all i ≥ 0, xyⁱz ∈ L (pumping y zero, one, or more times keeps the string in L)

Here y⁰ = ε, y¹ = y, y² = yy, and so on.

## Proof of the Lemma

Let M be a DFA with p states that decides L. Let s ∈ L with |s| = n ≥ p. Consider the sequence of states visited while processing s:

q₀, q₁, q₂, …, qₙ

where q₀ is the start state and qᵢ = δ̂(q₀, s[1..i]).

This sequence has n+1 ≥ p+1 states, but there are only p distinct states. By the **Pigeonhole Principle**, some state is visited at least twice. Let qⱼ = qₖ for some 0 ≤ j < k ≤ p (we can always find such j, k with k ≤ p since the first p+1 elements of the sequence have length p).

Set:
- x = s[1..j] (the prefix before the first visit to the repeated state)
- y = s[j+1..k] (the substring between the two visits, the "loop")
- z = s[k+1..n] (the suffix)

Then:
- |y| = k - j ≥ 1 since j < k. ✓ (condition 1)
- |xy| = k ≤ p since k ≤ p by choice. ✓ (condition 2)
- Reading x from q₀ ends in qⱼ. Reading y from qⱼ loops back to qⱼ = qₖ. So reading y any number of times still ends at qⱼ. Then reading z ends in qₙ ∈ F. So xyⁱz is accepted for all i ≥ 0. ✓ (condition 3) ∎

## Proof Template for Non-Regularity

To prove L is not regular:

1. **Assume** for contradiction that L is regular with pumping length p.
2. **Choose** a specific string s ∈ L with |s| ≥ p. (Your choice — make it clever.)
3. **Analyze all valid splits** s = xyz with |y| ≥ 1 and |xy| ≤ p. Use these constraints to determine what y can look like.
4. **Find** an i ≥ 0 such that xyⁱz ∉ L. This must work for **every** valid split.
5. **Conclude** contradiction — the pumping lemma is violated, so L is not regular.

## Example 1: {0ⁿ1ⁿ | n ≥ 0} is Not Regular

**Proof.** Assume L = {0ⁿ1ⁿ \| n ≥ 0} is regular with pumping length p. Choose s = 0ᵖ1ᵖ ∈ L (|s| = 2p ≥ p). 

Consider any split s = xyz with |y| ≥ 1 and |xy| ≤ p. Since |xy| ≤ p, both x and y lie entirely within the first p symbols of s, which are all 0s. So y = 0ᵏ for some k ≥ 1.

Pump with i = 2: xy²z = 0ᵖ⁺ᵏ1ᵖ. Since k ≥ 1, we have p+k > p zeros but only p ones. So xy²z ∉ L. Contradiction. ∎

Alternatively, pump with i = 0: xy⁰z = xz = 0ᵖ⁻ᵏ1ᵖ. This has fewer zeros than ones, also ∉ L.

## Example 2: {0^(n²) | n ≥ 0} is Not Regular

**Proof.** Let p be the pumping length. Choose s = 0^(p²) ∈ L. Any valid split gives y = 0ᵏ with 1 ≤ k ≤ p. Consider pumping with i = 2: xy²z = 0^(p²+k). Is p² + k a perfect square?

The next perfect square after p² is (p+1)² = p² + 2p + 1. We have p² < p² + k ≤ p² + p < p² + 2p + 1. So p² + k is strictly between two consecutive perfect squares, hence not a perfect square. Therefore xy²z ∉ L. Contradiction. ∎

## Example 3: {ww | w ∈ {0,1}\*} is Not Regular

**Proof.** Let p be the pumping length. Choose s = 0ᵖ10ᵖ1 ∈ L (with w = 0ᵖ1, so s = ww has length 2p+2 ≥ p). Any split with |xy| ≤ p gives y = 0ᵏ (1 ≤ k ≤ p) lying in the first block of zeros.

Pump with i = 2: s' = 0^(p+k)10ᵖ1. For s' to equal ww for some w, both halves must be identical. The first half would be 0^((p+k+1)/1)... more carefully: s' has length 2p+2+k. The first half has length p+1+k/2 (only integer if k is even), but the symmetry needed for ww means the exact midpoint must split cleanly. The first half starts with more 0s than the second half (p+k vs p), so they cannot be equal. Therefore s' ∉ L. Contradiction. ∎

## Common Pitfalls

1. **Wrong quantifier direction.** The pumping lemma says: ∃p ∀s ∈ L with |s| ≥ p, ∃ split xyz, ∀i ≥ 0, xyⁱz ∈ L. The negation (for contradiction) is: ∀p ∃s ∈ L with |s| ≥ p, ∀ splits xyz, ∃i such that xyⁱz ∉ L. You **choose** s after seeing p; you **analyze all** splits; you **find one** i per split.

2. **Forgetting condition 2.** You must respect |xy| ≤ p — it constrains where y can appear. Missing this gives an invalid proof.

3. **Only considering one split.** You must show that *every* valid split leads to a contradiction, not just one convenient split.

4. **Misapplying in the other direction.** The pumping lemma does NOT certify regularity. A language that satisfies the pumping property might still be non-regular. (Example: there exist non-regular languages that satisfy the pumping lemma.) The Myhill-Nerode theorem gives the if-and-only-if characterization.

## The Myhill-Nerode Theorem (Stronger Alternative)

For a more powerful tool, use the Myhill-Nerode theorem:

**Define** x ≡_L y iff for all z: xz ∈ L ⟺ yz ∈ L.

**Theorem.** L is regular iff ≡_L has finitely many equivalence classes.

To prove non-regularity: exhibit an infinite set of strings that are pairwise L-distinguishable (each pair (x, y) has a distinguishing extension z with xz ∈ L but yz ∉ L, or vice versa). If you can find infinitely many pairwise distinguishable strings, then ≡_L has infinitely many classes → L is not regular.

For {0ⁿ1ⁿ}: the strings 0, 00, 000, … are pairwise distinguishable: 0ⁱ and 0ʲ (i≠j) are distinguished by z = 1ⁱ (gives 0ⁱ1ⁱ ∈ L but 0ʲ1ⁱ ∉ L when i≠j). So ≡_L has infinitely many classes, and {0ⁿ1ⁿ} is not regular — with no case analysis required.
