# Video: Decidability, Undecidability, and P vs NP

This video covers the two crowning results of theory of computation: the undecidability of the halting problem and the P vs NP question, including polynomial-time reductions and NP-completeness.

**Key takeaways:**
- Proving A_TM (does TM M accept input w?) is undecidable via diagonalization: the classical self-referential argument that rules out any decider.
- Reductions as the main proof tool: if A reduces to B and A is undecidable, then B is undecidable; mapping reductions vs. Turing reductions.
- The classes P and NP: what makes a verifier polynomial-time, and why NP ⊆ EXPTIME but we do not know if P = NP.
- Cook-Levin theorem: SAT is NP-complete; how to reduce SAT to other problems (3-SAT, Clique, Vertex Cover, Subset Sum) to establish NP-completeness.

**Approximate timestamps:**
- 0:00 – Decidable vs. recognizable languages
- 15:00 – Halting problem proof (diagonalization)
- 30:00 – Reductions and more undecidable problems
- 50:00 – P and NP definitions
- 1:05:00 – Cook-Levin and NP-completeness reductions
