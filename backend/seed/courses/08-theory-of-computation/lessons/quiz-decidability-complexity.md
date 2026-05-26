# Quiz: Decidability & Complexity

**Q1. The language HALT_TM = {⟨M, w⟩ | M halts on w} is:**
- [ ] Decidable
- [x] Undecidable but Turing-recognizable
- [ ] Not Turing-recognizable
- [ ] In the class P

**Q2. A language L is decidable if and only if:**
- [ ] L is Turing-recognizable
- [ ] L has a finite number of strings
- [x] L is both Turing-recognizable and co-Turing-recognizable (its complement is also Turing-recognizable)
- [ ] L can be described by a context-free grammar

**Q3. Rice's Theorem implies that:**
- [ ] All properties of DFAs are decidable
- [x] Every non-trivial semantic property of a Turing machine's language is undecidable
- [ ] The halting problem is decidable for finite automata inputs
- [ ] P ≠ NP

**Q4. A problem is in NP if:**
- [ ] It can be solved in nondeterministic polynomial time, but provably NOT in deterministic polynomial time
- [x] A proposed solution (certificate) can be verified in deterministic polynomial time
- [ ] It requires exponential time to solve on all known algorithms
- [ ] It has a polynomial-time reduction to every other NP problem

**Q5. If A ≤_p B (polynomial-time reduction from A to B) and B ∈ P, then:**
- [x] A ∈ P (we can decide A by reducing to B, then applying B's polynomial algorithm)
- [ ] A is NP-complete
- [ ] B is NP-hard
- [ ] A and B have identical time complexity

**Q6. The Cook-Levin theorem states that:**
- [ ] P = NP
- [ ] P ≠ NP
- [x] SAT is NP-complete: every language in NP has a polynomial-time reduction to SAT
- [ ] Every NP problem reduces to HALT_TM

**Q7. The language E_TM = {⟨M⟩ | L(M) = ∅} is undecidable. The proof reduces which known language to E_TM?**
- [ ] HALT_TM directly
- [ ] The complement of A_TM
- [x] A_TM (by constructing M' that accepts everything iff M accepts w, then noting ⟨M,w⟩ ∈ A_TM ⟺ ⟨M'⟩ ∉ E_TM)
- [ ] The diagonal language D
