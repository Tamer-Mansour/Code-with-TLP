# NFA to DFA Conversion: The Subset Construction in Full Detail

The subset construction (also called the powerset construction) is the algorithm that converts any NFA into an equivalent DFA. It is one of the most important algorithms in automata theory, both theoretically (it proves NFA = DFA in expressive power) and practically (it is how regex engines build fast matchers).

## Motivation and Overview

An NFA may be in multiple states simultaneously. The key insight is: we can track the **set** of all states the NFA could currently be in as a single DFA state. This set-of-states becomes one DFA state. The DFA's transition function computes the next set of states from the current set.

**Input:** NFA N = (Q, Σ, δ_N, q₀, F_N)  
**Output:** DFA M = (Q_M, Σ, δ_M, q₀_M, F_M) with L(M) = L(N)

**Construction:**
- Q_M = 𝒫(Q) (subsets of Q; at most 2^|Q| states)
- q₀_M = E({q₀}) (ε-closure of the NFA start state)
- δ_M(S, a) = E(∪_{q ∈ S} δ_N(q, a)) for each S ⊆ Q, a ∈ Σ
- F_M = {S ⊆ Q \| S ∩ F_N ≠ ∅}

In practice, only the **reachable** subsets are constructed (starting from q₀_M and following transitions). This lazy construction often produces far fewer than 2^|Q| states.

## Worked Example: NFA for Strings Ending in "01"

**NFA N:** Σ = {0, 1}, accept strings ending in "01".

```
States: {q₀, q₁, q₂}
Start: q₀, Accept: {q₂}

δ_N transitions:
  State  | 0        | 1       | ε
  q₀     | {q₀,q₁} | {q₀}   | ∅
  q₁     | ∅        | {q₂}   | ∅
  q₂     | ∅        | ∅      | ∅
```

**q₀** is the "reset" state — it can always restart a new potential "01" match.  
**q₁** means "just saw a 0 that might be the start of 01".  
**q₂** means "just completed 01" (accept).

### Step 1: Compute Start State

q₀_M = E({q₀}) = {q₀} (no ε-transitions from q₀).

### Step 2: Build Reachable DFA States

Begin with worklist = [{q₀}].

**Process {q₀}:**
- On 0: ∪_{q∈{q₀}} δ_N(q,0) = {q₀,q₁}; ε-close: E({q₀,q₁}) = {q₀,q₁}
- On 1: ∪_{q∈{q₀}} δ_N(q,1) = {q₀}; ε-close: E({q₀}) = {q₀}

Add {q₀,q₁} to worklist.

**Process {q₀,q₁}:**
- On 0: δ_N(q₀,0)∪δ_N(q₁,0) = {q₀,q₁}∪∅ = {q₀,q₁}; ε-close: {q₀,q₁}
- On 1: δ_N(q₀,1)∪δ_N(q₁,1) = {q₀}∪{q₂} = {q₀,q₂}; ε-close: {q₀,q₂}

Add {q₀,q₂} to worklist.

**Process {q₀,q₂}:**
- On 0: δ_N(q₀,0)∪δ_N(q₂,0) = {q₀,q₁}∪∅ = {q₀,q₁}; ε-close: {q₀,q₁}  (already seen)
- On 1: δ_N(q₀,1)∪δ_N(q₂,1) = {q₀}∪∅ = {q₀}; ε-close: {q₀}  (already seen)

**No new states.** Worklist empty.

### Step 3: Build the DFA Transition Table

| DFA State | On 0 | On 1 | Accept? |
|-----------|------|------|---------|
| A = {q₀} | B = {q₀,q₁} | A = {q₀} | No (q₂ ∉ A) |
| B = {q₀,q₁} | B = {q₀,q₁} | C = {q₀,q₂} | No |
| C = {q₀,q₂} | B = {q₀,q₁} | A = {q₀} | **Yes** (q₂ ∈ C) |

**DFA start:** A. **DFA accept:** {C}.

### Verification

Does the DFA accept "001"?
- A →⁰ B →⁰ B →¹ C ✓ **accept** ("001" ends in "01")

Does the DFA accept "010"?
- A →⁰ B →¹ C →⁰ B ✗ **reject** ("010" does not end in "01")

Does the DFA accept "01"?
- A →⁰ B →¹ C ✓ **accept** ✓

## The Exponential Blowup: When Is It Real?

For the "ending in 01" example, 3 NFA states → 3 DFA states (only 3 of 2³=8 subsets are reachable). In general, many NFA states go to few reachable DFA states — the practical blowup is often small.

**Worst case:** There exist NFAs for which the subset construction is unavoidable. The classic example: the language of all strings over {0,1} whose n-th-from-last symbol is 1. A minimal NFA for this language has n+1 states, but any DFA needs 2ⁿ states. For n=4, that is 16 DFA states. For n=20, that is over 1 million.

| NFA states | Min DFA states (worst case family) |
|-----------|-----------------------------------|
| 3 | 8 |
| 10 | 1,024 |
| 20 | 1,048,576 |
| 30 | ~10⁹ |

This exponential blowup is unavoidable for some languages, but for most practical regexes (like email patterns or URL matchers), the DFA has few states.

## ε-Transitions: Computing ε-Closure

The ε-closure computation is a graph reachability problem. For each state q, E(q) is the set of states reachable via zero or more ε-transitions. This is computed by BFS or DFS from q along ε-labeled edges.

**Example:** NFA with ε-transitions:
```
δ(q₀, ε) = {q₁, q₂}
δ(q₁, ε) = {q₃}
δ(q₂, ε) = {}
δ(q₃, ε) = {}
```

E({q₀}) = {q₀} ∪ {q₁,q₂} ∪ E({q₁}) ∪ E({q₂}) = {q₀,q₁,q₂,q₃}.

ε-closure is computed once as preprocessing, then used in every δ_M computation.

## Summary

The subset construction is:
1. **Correct:** L(DFA) = L(NFA) by induction on |w|.
2. **Complete:** Every reachable DFA state is constructed.
3. **Worst-case exponential:** But usually manageable in practice.
4. **Foundation:** Underlies all DFA-based regex matching engines (e.g., lex, re2).
