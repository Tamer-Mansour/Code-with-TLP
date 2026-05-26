# Closure Properties of Regular Languages

A key way to prove a language is regular is to decompose it as a combination of simpler regular languages using **closure properties**. If the components are regular and the operations preserve regularity, the result is regular. Closure properties are also used in the other direction: if an operation on a regular language is known to yield a non-regular result, the original assumption (that some ingredient is regular) must be false.

## The Regular Language Closure Properties

**Theorem.** If A and B are regular languages over Σ, then the following languages are also regular:

1. **A ∪ B** (union)
2. **A ∩ B** (intersection)
3. **Ā = Σ\* \ A** (complement)
4. **A ∘ B = AB** (concatenation)
5. **A\*** (Kleene star)
6. **A \ B = A ∩ B̄** (set difference — follows from 2 and 3)
7. **Aᴿ** (reversal: reverse all strings in A)
8. **h(A)** for any homomorphism h (replace each symbol a by a fixed string h(a))
9. **h⁻¹(A)** (inverse homomorphism)

Regular languages are thus closed under all operations of the Boolean algebra (∪, ∩, complement) plus concatenation, Kleene star, reversal, and homomorphisms. This is a much richer closure structure than context-free languages enjoy.

## Proof Sketches

### Complement (DFA state swap)

Given DFA M = (Q, Σ, δ, q₀, F) that decides A, swap accept and non-accept states: M' = (Q, Σ, δ, q₀, Q \ F). M' accepts w iff M rejects w, so L(M') = Ā. This works because a DFA **always halts** and never is in an ambiguous state — exactly one state is reached after each input, so swapping is sound. This proof does NOT work directly for NFAs: if an NFA rejects, it means no path accepts, but "no path accepts" is not the same as "there is a path to a non-accept state."

### Intersection (Product Construction)

Given DFAs M₁ = (Q₁, Σ, δ₁, s₁, F₁) and M₂ = (Q₂, Σ, δ₂, s₂, F₂), construct M₁ × M₂:

- **States:** Q₁ × Q₂ (all pairs)
- **Start:** (s₁, s₂)
- **Transitions:** δ((p, q), a) = (δ₁(p, a), δ₂(q, a)) for all p ∈ Q₁, q ∈ Q₂, a ∈ Σ
- **Accept (intersection):** F₁ × F₂ = {(p, q) \| p ∈ F₁ and q ∈ F₂}
- **Accept (union):** F₁ × Q₂ ∪ Q₁ × F₂ = {(p,q) \| p ∈ F₁ or q ∈ F₂}

The product construction elegantly handles both intersection and union. It has |Q₁| × |Q₂| states — potentially large but always finite.

### Union (NFA Construction)

Given NFAs N₁ and N₂, add a new start state q₀ with ε-transitions to the starts of N₁ and N₂. Accept states are the same as before. The resulting NFA accepts w iff N₁ or N₂ accepts w. This is much simpler than the product construction, with only |Q₁| + |Q₂| + 1 states.

### Concatenation (NFA ε-link)

Given NFAs N₁ and N₂, add ε-transitions from every accept state of N₁ to the start of N₂. The accept states are only those of N₂. The NFA accepts w iff w can be split as xy where N₁ accepts x and N₂ accepts y.

### Kleene Star (NFA loop)

Given NFA N₁, add a new start/accept state q₀ with ε-transition to N₁'s start, and ε-transitions from every accept state of N₁ back to q₀. This allows zero repetitions (ε, accepted at q₀) or any number of repetitions.

### Reversal (Reversed NFA)

Given DFA M for A, construct NFA for Aᴿ:
- Reverse all transition arrows: if δ(p, a) = q in M, add a transition q →^a p in the NFA.
- The new start state is a fresh state with ε-transitions to all original accept states.
- The accept state is the original start state.

Then the NFA accepts w iff M would accept wᴿ, i.e., wᴿ ∈ A, i.e., w ∈ Aᴿ.

## Worked Application 1: Showing a Language is Regular

**Example.** Show L = {w ∈ {a,b}\* \| w contains "ab" but does not start with "b"} is regular.

- L₁ = {w \| w contains "ab"}: regular (regex: (a∪b)\*ab(a∪b)\*, or a 3-state NFA).
- L₂ = {w \| w starts with "b"} = b(a∪b)\*: regular.
- L = L₁ ∩ L̄₂: intersection of two regular languages → regular. ✓

The product DFA construction gives an explicit DFA for L.

**Example.** Show L = {w ∈ {0,1}\* \| |w| is even} is regular.

- The language {0,1}^(2k) for k ≥ 0 is described by the regex ((0∪1)(0∪1))\*.
- DFA: 2 states (even length, odd length). Accept only the even-length state. ✓

**Example.** Show L = {w ∈ {0,1}\* \| w contains "11" and does not contain "000"} is regular.

- A = {w \| w contains "11"}: regular (NFA for "11" substring).
- B = {w \| w contains "000"}: regular.
- L = A ∩ B̄ = A ∩ complement(B): regular. ✓

## Worked Application 2: Using Closure to Prove Non-Regularity

Closure properties can also show non-regularity:

**Example.** Show {0^n 1^n \| n ≥ 0} ∩ {0\*1\*} = {0^n 1^n \| n ≥ 0} is not regular.

If {0^n 1^n} were regular, and since {0\*1\*} is regular, then their intersection would be regular by closure. But {0^n 1^n} itself is the intersection of {0^n 1^n} with the universal language (which is trivially regular), so this argument circles back. The pumping lemma is needed here.

**Example.** Show that if L is regular and we remove all strings of even length, we do not necessarily get a regular language... wait, actually we do: {w ∈ L \| |w| even} = L ∩ {w \| |w| even}, and both parts are regular, so the intersection is regular. Closure strikes again.

## Myhill-Nerode and Closure

The Myhill-Nerode theorem provides a deeper perspective on closure. For the product construction, the equivalence classes of ≡_{A∩B} are finer than the product of classes of ≡_A and ≡_B: two strings in the same class for both A and B are in the same class for A ∩ B. Since both have finitely many classes (by regularity), the product also has finitely many → A ∩ B is regular.

## Summary Table

| Operation | Regular? | Simplest proof |
|-----------|----------|---------------|
| Union | Yes | NFA (new start with ε-transitions) or product DFA |
| Intersection | Yes | Product DFA (both components accept) |
| Complement | Yes | DFA state swap (only works for DFAs) |
| Concatenation | Yes | NFA ε-link between components |
| Kleene star | Yes | NFA with ε-loop |
| Reversal | Yes | Reversed NFA |
| Homomorphism h | Yes | Replace each terminal a in each rule by h(a) |
| Inverse homomorphism h⁻¹ | Yes | Modified DFA tracking pre-image |
| Set difference A\B | Yes | A ∩ B̄ (intersection + complement) |
