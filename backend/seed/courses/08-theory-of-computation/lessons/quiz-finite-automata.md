# Quiz: Finite Automata

**Q1. A DFA's transition function has which signature?**
- [ ] δ : Q × Σ → 𝒫(Q)
- [x] δ : Q × Σ → Q
- [ ] δ : Σ* → Q
- [ ] δ : Q → 𝒫(Q)

**Q2. An NFA differs from a DFA in that an NFA:**
- [ ] Can have more than one start state
- [ ] Always accepts a strictly larger class of languages than a DFA
- [x] May have multiple transitions on the same symbol and ε-transitions, with δ returning a set of states
- [ ] Cannot have any accept states

**Q3. The subset construction converts an NFA with n states to a DFA with at most how many states?**
- [ ] n
- [ ] n²
- [ ] n!
- [x] 2ⁿ (one state per subset of the NFA's state set)

**Q4. In the subset construction, the DFA's start state corresponds to:**
- [ ] The NFA's start state alone, without ε-closure
- [x] The ε-closure of the NFA's start state
- [ ] The set of all NFA states
- [ ] Any arbitrarily chosen subset

**Q5. The Myhill-Nerode theorem states that a language L is regular if and only if:**
- [ ] L satisfies the pumping lemma
- [ ] L has at most 2^|Q| equivalence classes for some DFA Q
- [x] The Myhill-Nerode equivalence relation ≡_L has finitely many equivalence classes
- [ ] L is closed under all Boolean operations

**Q6. For the DFA recognizing binary numbers divisible by 3, the minimal DFA has how many states?**
- [ ] 2 (one accepting, one rejecting)
- [x] 3 (one per remainder class 0, 1, 2 mod 3)
- [ ] 4
- [ ] 6

**Q7. The language {w ∈ {a,b}* | w contains the substring "ab"} can be recognized by an NFA with how many states?**
- [ ] 2
- [x] 3 (start, seen-a, seen-ab-absorb)
- [ ] 4
- [ ] It requires a DFA; no NFA of fewer than 8 states works
