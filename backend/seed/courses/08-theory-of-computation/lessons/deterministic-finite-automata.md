# Deterministic Finite Automata

A **deterministic finite automaton (DFA)** is the simplest model of computation: it reads input left-to-right, maintains a finite amount of state, and at the end either accepts or rejects. Despite its simplicity, the DFA characterizes exactly the class of regular languages — the same class captured by regular expressions and NFAs.

## Formal Definition

A DFA is a 5-tuple M = (Q, Σ, δ, q₀, F) where:

| Component | Type | Meaning |
|-----------|------|---------|
| Q | finite set | Set of **states** |
| Σ | finite set | Input **alphabet** |
| δ | Q × Σ → Q | **Transition function** (total, deterministic) |
| q₀ | element of Q | **Start state** |
| F | subset of Q | Set of **accept (final) states** |

The machine processes string w = w₁w₂…wₙ by:
1. Starting in state q₀.
2. For each symbol wᵢ (in order), moving from current state q to δ(q, wᵢ).
3. After all n symbols, **accepting** iff the current state ∈ F; otherwise **rejecting**.

The machine *always* halts (there is no looping) and gives a definitive answer. This is what "decidable" looks like for finite-memory computation.

## Extended Transition Function δ̂

The **extended transition function** δ̂ : Q × Σ\* → Q applies δ repeatedly over a string:

- δ̂(q, ε) = q  (reading nothing keeps the state)
- δ̂(q, wa) = δ(δ̂(q, w), a)  (read all of w, then read a)

The language of M is L(M) = {w ∈ Σ\* \| δ̂(q₀, w) ∈ F}.

## Worked Example 1: Binary Strings Ending in 1

Σ = {0, 1}. Construct a DFA for L = {w \| w ends in 1}.

**States:** q₀ (last symbol was 0, or no input yet), q₁ (last symbol was 1).

**Transition table:**

| State | 0 | 1 |
|-------|---|---|
| q₀ | q₀ | q₁ |
| q₁ | q₀ | q₁ |

**Start:** q₀. **Accept:** {q₁}.

Trace on w = "101":
- δ̂(q₀, 1) = δ(q₀, 1) = q₁
- δ̂(q₁, 0) = δ(q₁, 0) = q₀
- δ̂(q₀, 1) = δ(q₀, 1) = q₁ ∈ F → **accept** ✓

Trace on w = "10":
- q₀ →¹ q₁ →⁰ q₀ ∉ F → **reject** ✓

## Worked Example 2: Binary Numbers Divisible by 3

Σ = {0, 1}, encoding n in binary (most-significant bit first). Construct a DFA for L = {w \| w encodes a non-negative integer divisible by 3}.

**Key insight:** Reading bit b in state r (meaning current value mod 3 = r) moves to state (2r + b) mod 3, since appending bit b multiplies the current value by 2 and adds b.

**States:** {r₀, r₁, r₂} where rᵢ represents "current prefix value ≡ i (mod 3)".

| State | 0 | 1 |
|-------|---|---|
| r₀ (rem 0) | r₀ | r₁ |
| r₁ (rem 1) | r₂ | r₀ |
| r₂ (rem 2) | r₁ | r₂ |

**Start:** r₀ (ε encodes 0, and 0 mod 3 = 0). **Accept:** {r₀}.

Verification:
- "110" = 6. Trace: r₀ →¹ r₁ →¹ r₀ →⁰ r₀ ∈ F. **accept** ✓ (6 mod 3 = 0)
- "111" = 7. Trace: r₀ →¹ r₁ →¹ r₀ →¹ r₁ ∉ F. **reject** ✓ (7 mod 3 = 1)
- "100" = 4. Trace: r₀ →¹ r₁ →⁰ r₂ →⁰ r₁ ∉ F. **reject** ✓ (4 mod 3 = 1)

This DFA is minimal (3 states is the minimum, since 0, 1, 2 are mutually distinguishable by the string "0": appending "0" doubles the value, which moves r₀→r₀, r₁→r₂, r₂→r₁ — all different).

## Worked Example 3: Language with a More Complex Structure

Σ = {a, b}. Construct a DFA for L = {w \| w contains neither "aa" nor "bb" as a substring} — i.e., no two consecutive identical symbols.

**States:**
- q₀: start / last symbol was b (or start)
- q₁: last symbol was a
- q₂: dead state (already saw aa or bb)

| State | a | b |
|-------|---|---|
| q₀ | q₁ | q₀ |
| q₁ | q₂ | q₀ |
| q₂ | q₂ | q₂ |

**Start:** q₀. **Accept:** {q₀, q₁}.

This DFA accepts strings like ε, a, b, ab, ba, aba, bab, abab, … and rejects aa, bb, aab, bba, …

## Regular Languages: Definition via DFAs

**Definition.** A language L is **regular** if and only if some DFA decides it.

This is the definition of regular languages from the automata perspective. Three equivalent characterizations will emerge:
1. Recognized by a DFA.
2. Recognized by an NFA (Module 2).
3. Described by a regular expression (Module 3).

The equivalence of all three is a deep and useful result (Kleene's theorem).

## Minimization: The Myhill-Nerode Theorem

Two strings x, y ∈ Σ\* are **indistinguishable** with respect to L (written x ≡_L y) if for every string z: xz ∈ L ⟺ yz ∈ L. This is the Myhill-Nerode equivalence relation.

**Theorem (Myhill-Nerode, 1958).** A language L is regular iff ≡_L has finitely many equivalence classes. Moreover, the number of equivalence classes equals the number of states in the **minimal DFA** for L.

This gives both a test for regularity (stronger than the pumping lemma — it is if and only if) and a canonical smallest DFA. For the divisibility-by-3 example, the three classes are: {w \| w encodes n ≡ 0 mod 3}, {w \| w encodes n ≡ 1 mod 3}, {w \| w encodes n ≡ 2 mod 3}. Three classes → three states → the DFA above is minimal.

## What DFAs Cannot Do

DFAs have a fixed finite number of states and cannot count unboundedly. The language {0ⁿ1ⁿ \| n ≥ 0} requires knowing n, which grows arbitrarily. The Myhill-Nerode theorem formalizes why: the strings 0^i and 0^j (i ≠ j) are distinguishable (using suffix 1^i, we get 0^i 1^i ∈ L but 0^j 1^i ∉ L when i ≠ j). So ≡_L has infinitely many classes → L is not regular.
