# Quiz: Turing Machines

**Q1. A Turing machine's transition function has signature:**
- [ ] δ : Q × Σ → Q
- [x] δ : Q' × Γ → Q × Γ × {L, R} (where Q' = Q minus halt states)
- [ ] δ : Q × Γ → 𝒫(Q × Γ)
- [ ] δ : Q × Σ × Γ → Q × Γ × {L, R}

**Q2. A Turing machine "decides" a language L if:**
- [ ] It accepts all strings in L but may loop on strings not in L
- [ ] It never loops on any input in L
- [x] It accepts all strings in L and rejects all strings not in L, halting on every input
- [ ] It runs in polynomial time on all inputs

**Q3. The Church-Turing thesis states:**
- [ ] Every function computable by a TM can be computed in polynomial time
- [ ] Quantum computers can decide languages that TMs cannot
- [x] Every effectively computable function (any function computable by a definite step-by-step procedure) can be computed by a Turing machine
- [ ] All TM variants run at the same speed

**Q4. Simulating a k-tape TM with a single-tape TM incurs how much time overhead?**
- [ ] O(log n) per step
- [ ] O(n) total overhead regardless of computation length
- [x] O(t(n)) per step, making the total time O(t(n)²) for a t(n)-step k-tape TM
- [ ] No overhead — they run at the same speed

**Q5. A nondeterministic TM N is simulated by a deterministic TM D via:**
- [ ] Depth-first search over N's nondeterministic branches (may miss accepting branches on infinite paths)
- [x] Breadth-first search over N's nondeterministic branches (ensures all branches of any fixed length are explored)
- [ ] Running only one branch chosen at random
- [ ] Converting N directly to a deterministic TM by the subset construction

**Q6. An enumerator for language L is most closely related to:**
- [ ] A DFA that decides L
- [ ] A PDA that accepts L
- [x] A Turing machine that recognizes L (both enumerate the same class: Turing-recognizable)
- [ ] A context-free grammar for L

**Q7. Which variant is strictly WEAKER than a standard Turing machine (i.e., recognizes a proper subclass)?**
- [ ] Multi-tape TM
- [ ] Nondeterministic TM
- [ ] 2-stack PDA
- [x] A single-stack pushdown automaton (PDA), which recognizes only context-free languages
