# Nondeterministic Finite Automata

A **nondeterministic finite automaton (NFA)** extends the DFA by allowing multiple transitions on the same symbol and spontaneous (ε) transitions. Nondeterminism is a theoretical tool — think of it as the machine exploring all possible execution paths simultaneously. The NFA **accepts** if *any* path ends in an accept state.

NFAs do not add computational power over DFAs, but they often offer exponentially more concise descriptions and make closure proofs elegant.

## Formal Definition

An NFA is a 5-tuple N = (Q, Σ, δ, q₀, F) where:

| Component | Type | Meaning |
|-----------|------|---------|
| Q | finite set | States |
| Σ | finite set | Input alphabet |
| δ | Q × (Σ ∪ {ε}) → 𝒫(Q) | Transition function (returns a *set* of states) |
| q₀ | element of Q | Start state |
| F | subset of Q | Accept states |

Three key differences from a DFA:
1. δ returns a **set** (possibly empty, possibly with multiple elements).
2. The domain includes **ε** — free transitions not consuming input.
3. δ(q, a) = ∅ means the computation on this path **dies** (equivalent to moving to an implicit dead state).

## ε-Closure

The **ε-closure** of state q, written E(q), is the set of all states reachable from q by zero or more ε-transitions alone:

E(q) = {q} ∪ {r \| q →ε* r}

Extend to sets of states: E(R) = ∪_{q∈R} E(q).

**Example:** If δ(q₀, ε) = {q₁} and δ(q₁, ε) = {q₂}, then E({q₀}) = {q₀, q₁, q₂}.

## NFA Computation via Subset Tracking

The NFA processes string w = a₁a₂…aₙ by tracking the *set* of currently active states:

1. S₀ = E({q₀}) (ε-close the start)
2. For each input symbol aᵢ: Sᵢ = E(∪_{q∈S_{i-1}} δ(q, aᵢ))
3. **Accept** iff Sₙ ∩ F ≠ ∅

## Worked Example: Strings Containing "ab"

Σ = {a, b}. NFA for L = {w \| w contains "ab" as a substring}:

```
States: {q₀, q₁, q₂}
Start: q₀, Accept: {q₂}

δ(q₀, a) = {q₀, q₁}   -- stay at q₀ looping, or guess: this 'a' starts "ab"
δ(q₀, b) = {q₀}
δ(q₁, b) = {q₂}        -- the 'b' completing "ab"
δ(q₁, a) = ∅           -- dead (bad guess)
δ(q₂, a) = {q₂}        -- absorb rest of string
δ(q₂, b) = {q₂}
```

**Transition table** (δ, sets shown):

| State | a | b | ε |
|-------|---|---|---|
| q₀ | {q₀,q₁} | {q₀} | ∅ |
| q₁ | ∅ | {q₂} | ∅ |
| q₂ | {q₂} | {q₂} | ∅ |

**Trace on "bab":**
- S₀ = E({q₀}) = {q₀}
- Read b: ∪_{q∈{q₀}} δ(q,b) = {q₀}; E({q₀}) = {q₀} → S₁ = {q₀}
- Read a: δ(q₀,a) = {q₀,q₁}; E({q₀,q₁}) = {q₀,q₁} → S₂ = {q₀,q₁}
- Read b: δ(q₀,b)∪δ(q₁,b) = {q₀}∪{q₂} = {q₀,q₂}; E({q₀,q₂}) = {q₀,q₂} → S₃ = {q₀,q₂}
- S₃ ∩ {q₂} = {q₂} ≠ ∅ → **accept** ✓

**Trace on "ba":**
- S₀ = {q₀}
- Read b: S₁ = {q₀}
- Read a: S₂ = {q₀,q₁}
- S₂ ∩ {q₂} = ∅ → **reject** ✓

## The Subset Construction (NFA → DFA)

**Theorem (Rabin and Scott, 1959).** For every NFA N there exists an equivalent DFA M with L(M) = L(N).

**Construction.** Given N = (Q, Σ, δ, q₀, F), build DFA M = (Q', Σ, Δ, q₀', F') where:

- Q' = 𝒫(Q) (DFA states are subsets of NFA states; up to 2^|Q| states)
- q₀' = E({q₀}) (ε-close the NFA start state)
- Δ(S, a) = E(∪_{q∈S} δ(q, a)) for each S ⊆ Q, a ∈ Σ
- F' = {S ∈ Q' \| S ∩ F ≠ ∅}

In practice, only the **reachable** subsets need to be built — often far fewer than 2^|Q|.

### Worked Subset Construction Example

Apply the construction to the "ab" substring NFA above. Reachable subsets from q₀' = {q₀}:

| Subset | On a | On b |
|--------|------|------|
| {q₀} | E({q₀,q₁}) = {q₀,q₁} | E({q₀}) = {q₀} |
| {q₀,q₁} | E({q₀,q₁}) = {q₀,q₁} | E({q₀,q₂}) = {q₀,q₂} |
| {q₀,q₂} | E({q₀,q₁,q₂}) = {q₀,q₁,q₂} | E({q₀,q₂}) = {q₀,q₂} |
| {q₀,q₁,q₂} | E({q₀,q₁,q₂}) = {q₀,q₁,q₂} | E({q₀,q₂}) = {q₀,q₂} |

DFA states (reachable): {q₀}, {q₀,q₁}, {q₀,q₂}, {q₀,q₁,q₂} — 4 states (vs. 2³=8 possible subsets).

Accept states: those containing q₂: {q₀,q₂}, {q₀,q₁,q₂}.

The NFA had 3 states; the DFA needs 4. In the worst case the DFA can require 2^n states for an n-state NFA — and there exist families of languages where this blowup is unavoidable.

## Closure Properties via NFA

NFAs make closure proofs for regular languages elegant and mechanical:

**Union:** Given NFAs N₁, N₂, add a new start state q₀ with ε-transitions to the starts of N₁ and N₂. Accept states unchanged. The resulting NFA accepts L(N₁) ∪ L(N₂).

**Concatenation:** Connect every accept state of N₁ to the start of N₂ via ε-transitions; make only N₂'s accept states the final accept states.

**Kleene star:** Add a new start/accept state q₀; add ε-transitions from q₀ to N's original start, and from every accept state of N back to q₀.

**Complement:** For DFAs (not NFAs directly): first convert to a DFA via subset construction, then swap accept and non-accept states.

Each NFA construction is small and straightforward. Converting to DFAs afterward yields formal proofs that all these operations preserve regularity.

## Why Nondeterminism Matters Conceptually

While NFAs and DFAs recognize the same languages, nondeterminism:
- Provides exponentially more succinct descriptions (sometimes).
- Generalizes naturally to PDAs (where determinism and nondeterminism give different power) and TMs (where nondeterminism gives a model capturing NP).
- Captures the idea of "guessing and verifying" — the heart of the NP definition.

The NFA is thus the conceptual bridge from simple finite automata all the way to the P vs NP question.
