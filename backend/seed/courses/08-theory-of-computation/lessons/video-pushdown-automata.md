# Video: Pushdown Automata and Their Equivalence to Context-Free Grammars

This video introduces pushdown automata (PDAs) — finite automata augmented with a stack — and proves they accept exactly the context-free languages.

**Key takeaways:**
- PDA formal definition: states, input alphabet, stack alphabet, transition relation (nondeterministic), and acceptance by empty stack vs. accepting state.
- Tracing PDA computation on {0ⁿ1ⁿ} and {ww^R}: how the stack provides the counting and matching power that DFAs lack.
- The two-direction equivalence proof sketch: given a CFG, construct a PDA that simulates leftmost derivations (top-down); given a PDA, construct a CFG (the construction producing one variable per pair of states).
- Why PDAs cannot handle {www}: a single stack is not enough for center-symmetric languages of this form.

**Approximate timestamps:**
- 0:00 – PDA motivation and definition
- 15:00 – Stack traces for {0ⁿ1ⁿ} and {ww^R}
- 30:00 – CFG to PDA construction
- 48:00 – PDA to CFG construction
- 1:05:00 – Non-context-free languages and the CFL pumping lemma
