# Turing Machine Simulation and the Halting Problem

The Halting Problem asks: given a Turing machine M and an input w, does M halt on w? Turing proved in 1936 that no algorithm can decide this in general. But for a **bounded** simulation — where we limit the number of steps — we can always answer by running the machine for at most K steps and reporting whether it halted.

This exercise bridges theory and practice: implement a bounded TM simulator that decides "does this TM halt (and accept or reject) within K steps on the empty string?" For any fixed K, this is trivially decidable. The undecidability arises because we cannot choose K universally to work for all TMs.

## The Turing Machine Model

A Turing machine has:
- A finite set of **states** (including the special states `qaccept` and `qreject`)
- An infinite **tape** initialized to all blanks (`B`)
- A **read/write head** starting at position 0
- A **transition function** δ: (state, symbol) → (new_state, new_symbol, direction)

Each step:
1. Read the symbol under the head (blank `B` if unwritten).
2. Look up δ(current_state, symbol).
3. Write `new_symbol`, move to `new_state`, move head Left or Right.

If the TM enters `qaccept` or `qreject`, it halts immediately. If no transition is defined for the current (state, symbol) pair, the TM halts and rejects by convention.

## Connection to Undecidability

This simulation is decidable **only because** we fix a step bound K. In the general halting problem, K is unbounded: if the TM hasn't halted after any finite number of steps, you cannot tell whether it will ever halt or loop forever. This is why no algorithm can solve HALT_TM in general — there is no computable function that gives a sufficient step bound for an arbitrary TM.

When you run this simulator, you are building an approximation to a solution to the halting problem: it gives definitive answers for TMs that halt within K steps, and says "DID_NOT_HALT" for those that don't. But a TM that "DID_NOT_HALT" in K steps might halt at step K+1.

## Reductions and Rice's Theorem

The halting problem HALT_TM is undecidable, and many other questions about TMs are undecidable by reduction from HALT_TM (or from A_TM):

- **E_TM** = {M | L(M) = ∅}: undecidable.
- **EQ_TM** = {(M1, M2) | L(M1) = L(M2)}: undecidable.
- **REGULAR_TM** = {M | L(M) is regular}: undecidable.

**Rice's Theorem** subsumes all of these: every non-trivial semantic property of TM languages is undecidable. "Does M halt on ε?" is a semantic property (it depends on M's behavior, not its description), and it is non-trivial, so it is undecidable — unless bounded by K.

## Practical Relevance

This bounded simulation is essentially what model checkers do for finite-state systems: verify up to a bounded number of steps. It is also the basis of "bounded model checking" and "bounded program analysis" in software verification. The theoretical impossibility of unbounded checking is why formal verification remains hard.

## Further Reading

- Sipser §3.1–3.2, §4.1–4.2 — MIT OCW: https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/
- Maheshwari & Smid, Chapters 5–6 (TM model, decidability, reductions) — https://cglab.ca/~michiel/TheoryOfComputation/TheoryOfComputation.pdf
