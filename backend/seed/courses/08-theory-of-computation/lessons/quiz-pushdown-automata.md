# Quiz: Pushdown Automata

**Q1. A pushdown automaton extends a finite automaton by adding:**
- [ ] Multiple input tapes
- [x] An infinite stack (LIFO memory)
- [ ] Two-way input head movement
- [ ] Multiple start states

**Q2. The transition function of a PDA has signature:**
- [ ] δ : Q × Σ → Q
- [ ] δ : Q × Σ → 𝒫(Q)
- [x] δ : Q × (Σ ∪ {ε}) × (Γ ∪ {ε}) → 𝒫(Q × (Γ ∪ {ε}))
- [ ] δ : Q × Σ × Γ → Q × Γ (deterministic, no ε)

**Q3. The language {aⁿbⁿ | n ≥ 0} is recognized by a PDA because:**
- [ ] It is regular and all regular languages are recognized by PDAs
- [x] The stack tracks the count of a's by pushing a symbol per 'a', then pops one per 'b'
- [ ] It has a finite number of strings
- [ ] It can be recognized by a DFA with enough states

**Q4. Deterministic and nondeterministic PDAs differ in that:**
- [ ] They recognize exactly the same class of languages, just like DFA vs NFA
- [x] Deterministic PDAs (DPDAs) recognize a proper subclass of the context-free languages
- [ ] Nondeterministic PDAs are strictly weaker than deterministic PDAs
- [ ] They differ only in speed, not in languages recognized

**Q5. The language {wwᴿ | w ∈ {a,b}*} (even-length palindromes) is:**
- [ ] Regular
- [x] Context-free but not deterministic context-free (requires nondeterminism to guess the midpoint)
- [ ] Not context-free
- [ ] Decidable but not context-free

**Q6. In the CFG-to-PDA construction, the PDA's stack at any point holds:**
- [ ] The input string processed so far
- [x] The remaining sentential form of the current leftmost derivation (the "frontier" yet to be matched)
- [ ] The complete parse tree
- [ ] The set of all reachable states

**Q7. Acceptance by empty stack and acceptance by final state for PDAs are:**
- [ ] Inequivalent — one accepts a strictly larger class
- [ ] Equivalent only for deterministic PDAs
- [ ] Not comparable — they accept incomparable classes of languages
- [x] Equivalent — every PDA using one mode has a PDA using the other mode that accepts the same language
