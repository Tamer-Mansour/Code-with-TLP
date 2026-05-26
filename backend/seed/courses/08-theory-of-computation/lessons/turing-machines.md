# Turing Machines

A **Turing machine (TM)** is the canonical model of universal computation. Unlike finite automata and PDAs, a TM has an infinite tape (read/write memory) and a head that can move in both directions. This gives it the full power needed to simulate any algorithm — and makes precise what we mean by "computable."

## Formal Definition

A TM is a 7-tuple M = (Q, Σ, Γ, δ, q₀, q_accept, q_reject) where:

| Component | Type | Meaning |
|-----------|------|---------|
| Q | finite set | States |
| Σ | finite set | Input alphabet (blank ␣ ∉ Σ) |
| Γ | finite set | Tape alphabet: Σ ⊆ Γ, ␣ ∈ Γ |
| δ | Q' × Γ → Q × Γ × {L, R} | Transition function (Q' = Q \ {q_accept, q_reject}) |
| q₀ | element of Q | Start state |
| q_accept | element of Q | Accept state (halts immediately on entry) |
| q_reject | element of Q | Reject state (halts immediately on entry; q_reject ≠ q_accept) |

The **tape** is infinite in both directions (or semi-infinite — either model is equivalent). Initially, the tape contains w (the input) followed by infinitely many blanks ␣. The head starts at the leftmost cell.

## Configurations and Computation

A **configuration** is a triple (q, tape, head-position). Conventionally written as the string to the left of the head, then the current state, then the symbol under the head and everything to the right. Example: "01q₃10␣" means: tape "0110", head on the third cell (reading '1'), state q₃.

**One computation step** from configuration with state q and head reading symbol a:
- δ(q, a) = (q', b, D): write b at the current cell, move head direction D ∈ {L, R}, enter state q'.
- If D=L and head is at position 0, the head stays at position 0 (left end of tape).
- The computation **halts** immediately upon entering q_accept or q_reject.

## Languages and Turing Machines

- M **accepts** w: starting in q₀ with w on tape, M eventually enters q_accept.
- M **rejects** w: M eventually enters q_reject.
- M **loops** on w: M runs forever without halting.

- M **recognizes** (or accepts) L if L = {w \| M accepts w}. M may loop on w ∉ L.
- M **decides** L if M recognizes L and M halts on all inputs (no loops). A decider never loops — it always accepts or rejects.

## Worked Example 1: Deciding {0ⁿ1ⁿ | n ≥ 1}

**High-level algorithm:** Alternately mark one 0 and one 1 until none remain. Accept if they run out together; reject if one type runs out before the other.

**Tape symbols:** Γ = {0, 1, X, Y, ␣} where X marks a used 0 and Y marks a used 1.

**States and transitions:**

| State | Purpose |
|-------|---------|
| q₀ | Find leftmost unmarked 0 |
| q₁ | Scan right to find the leftmost unmarked 1 |
| q₂ | Scan left back to beginning |
| q₃ | Verify no unmarked 0s or 1s remain |

Key transitions:
- δ(q₀, 0) = (q₁, X, R): mark 0 as X, go right to find 1
- δ(q₁, 0) = (q₁, 0, R): skip over 0s
- δ(q₁, Y) = (q₁, Y, R): skip over already-marked 1s
- δ(q₁, 1) = (q₂, Y, L): mark 1 as Y, go left to restart
- δ(q₂, 0) = (q₂, 0, L): scan left over 0s
- δ(q₂, Y) = (q₂, Y, L): scan left over Y's
- δ(q₂, X) = (q₀, X, R): reached leftmost X, start next round
- δ(q₀, Y) = (q₃, Y, R): no more 0s; check for remaining 1s
- δ(q₃, Y) = (q₃, Y, R): skip Y's
- δ(q₃, ␣) = (q_accept, ␣, R): only blanks → accept
- δ(q₀, ␣) = (q_reject, ␣, R): started with no 0s → reject
- δ(q₁, ␣) = (q_reject, ␣, R): ran out of 1s before 0s → reject

**Trace on "0011":**

| Config | Action |
|--------|--------|
| q₀: 0011 | Read 0 → mark X, move R |
| q₁: X011 (head on 0) | Read 0 → skip, move R |
| q₁: X011 (head on 1) | Read 1 → mark Y, move L |
| q₂: X0Y1 (head on 0) | Read 0 → skip left |
| q₂: X0Y1 (head on X) | Read X → move R, go to q₀ |
| q₀: X0Y1 (head on 0) | Read 0 → mark X, move R |
| q₁: XX Y1 (head on Y) | Read Y → skip, move R |
| q₁: XXY1 (head on 1) | Read 1 → mark Y, move L |
| q₂ → q₀: XXYY (head at second X) | Read X → move R, go to q₀ |
| q₀: XXYY (head on Y) | Read Y → go to q₃ |
| q₃: XXYY (head on Y) | Read Y → skip |
| q₃: XXYY (head on ␣) | → **accept** ✓ |

**Time complexity:** O(n²) — n iterations, each scanning up to O(n) cells.

## Worked Example 2: TM for Doubling

Recognize {0^(2n) \| n ≥ 0} (binary strings of 0s whose length is a power of 2... actually let's do a simpler one).

**Recognize {0^n \| n is a power of 2}**: Repeatedly halve the count of 0s. If you reach a single 0, accept. If you reach an odd count > 1, reject.

This TM repeatedly crosses out every other 0. It runs in O(n log n) time.

## Variants and Robustness

| Variant | Description | Overhead vs. standard |
|---------|-------------|----------------------|
| Multi-tape TM | k separate tapes with k heads | O(t(n)²) slowdown |
| Bidirectional tape | Tape extends both ways | Equivalent (fold one way) |
| Nondeterministic TM (NTM) | Multiple transitions; accepts if any branch accepts | Exponential time overhead (BFS simulation) |
| Enumerator | Prints strings; equivalent to recognizer | — |
| RAM model | O(1) memory access | Polynomial overhead |
| 2-PDA (two stacks) | Simulate a tape: left stack + right stack | Equivalent to TM |

All of these recognize exactly the same class of languages (Turing-recognizable). The time and space overheads matter for complexity theory but not for computability.

## The Church-Turing Thesis

The **Church-Turing thesis** is not a formal theorem — it is a widely accepted empirical claim:

> Every effectively computable function (any function a human can compute by following a definite procedure) can be computed by a Turing machine.

**Support for the thesis:**
- Lambda calculus (Church, 1936) and general recursive functions (Gödel, Herbrand, Kleene) were shown to be equivalent to TMs despite being invented independently.
- Every physically realizable model of computation proposed so far (cellular automata, quantum computers for decision problems, DNA computing, analog circuits under appropriate assumptions) computes the same set of decision problems as TMs.
- No counterexample has ever been found.

**What the thesis does NOT say:** It makes no claim about time or space efficiency — only about what is *computable at all*. A quantum computer may solve certain problems exponentially faster than any classical TM, but it cannot decide any language that a TM cannot decide (for decision problems).

The thesis allows us to describe TM algorithms at a high level: "the TM simulates a Python program doing X" — without specifying every tape transition — because we trust that any effective procedure can be so simulated.
