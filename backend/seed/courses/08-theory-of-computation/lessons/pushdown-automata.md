# Pushdown Automata

A **pushdown automaton (PDA)** is an NFA augmented with an infinite stack. The stack provides unbounded memory — but only in a last-in-first-out (LIFO) discipline — and this is exactly what is needed to match nested structures like {aⁿbⁿ} or balanced parentheses. The class of languages recognized by PDAs is exactly the class of context-free languages.

## Formal Definition

A PDA is a 6-tuple P = (Q, Σ, Γ, δ, q₀, F) where:

| Component | Type | Meaning |
|-----------|------|---------|
| Q | finite set | States |
| Σ | finite set | Input alphabet |
| Γ | finite set | **Stack alphabet** (may differ from Σ) |
| δ | Q × (Σ ∪ {ε}) × (Γ ∪ {ε}) → 𝒫(Q × (Γ ∪ {ε})) | Transition function |
| q₀ | element of Q | Start state |
| F | subset of Q | Accept states |

A transition (q', γ) ∈ δ(q, a, s) means:
- In state q,
- reading input symbol a (or ε for a free move — no input consumed),
- if the top of the stack is s (or ε to match without popping),
- move to state q' and push γ onto the stack (or ε to not push).

The **stack** is initially empty (or contains a designated bottom marker $). The PDA accepts w if some sequence of transitions on w ends in an accept state with any stack content (acceptance by final state).

## Configuration and Computation

A **configuration** of a PDA is a triple (q, w, γ) where q is the current state, w is the remaining input, and γ is the current stack contents (top at left).

A configuration (q, aw, sγ) **yields** (q', w, γ'γ) in one step if (q', γ') ∈ δ(q, a, s) (reading a and popping s, pushing γ').

A string w is **accepted** if there is a computation sequence from (q₀, w, ε) to (q_f, ε, γ) for some q_f ∈ F and any γ (accept by final state), OR from (q₀, w, ε) to (q, ε, ε) for any state q (accept by empty stack — equivalent model).

## Worked Example 1: {aⁿbⁿ | n ≥ 0}

**Intuition:** Push one stack symbol for each 'a' read; pop one for each 'b'. Accept if stack is empty and all input consumed.

```
States: {q₀, q₁, q₂}
Σ = {a, b}, Γ = {A, $}
Start: q₀, Accept: {q₂}

Transitions:
  δ(q₀, ε, ε)  = {(q₁, $)}       -- push bottom marker $
  δ(q₁, a, ε)  = {(q₁, A)}       -- reading 'a': push A
  δ(q₁, b, A)  = {(q₂, ε)}       -- first 'b': pop A (transition to q₂)
  δ(q₂, b, A)  = {(q₂, ε)}       -- subsequent 'b's: pop A
  δ(q₂, ε, $)  = {(q₂, ε)}       -- reached bottom marker: accept
```

Wait — state q₂ should be an accept state reached when the bottom marker $ is on top. Let me refine:

```
States: {q₀, q₁, q₂, q₃}
Start: q₀, Accept: {q₃}

δ(q₀, ε, ε)  = {(q₁, $)}        -- push $
δ(q₁, a, ε)  = {(q₁, A)}        -- push A for each 'a'
δ(q₁, b, A)  = {(q₂, ε)}        -- first 'b' pops A
δ(q₂, b, A)  = {(q₂, ε)}        -- more 'b's
δ(q₂, ε, $)  = {(q₃, ε)}        -- stack empty (only $ was there): accept
```

**Trace on "aabb":**

| Step | State | Remaining input | Stack (top→bottom) |
|------|-------|----------------|-------------------|
| 0 | q₀ | aabb | (empty) |
| 1 | q₁ | aabb | $ |
| 2 | q₁ | abb | A$ |
| 3 | q₁ | bb | AA$ |
| 4 | q₂ | b | A$ |
| 5 | q₂ | (empty) | $ |
| 6 | q₃ | (empty) | (empty) → **accept** ✓ |

**Trace on "ab":**
- q₀ →ε q₁($) → read a → q₁(A$) → read b → q₂($) →ε q₃ → **accept** ✓

**Trace on "aab" (should reject):**
- q₀ →ε q₁($) → read a → q₁(A$) → read a → q₁(AA$) → read b → q₂(A$) → no transition on ε reading $ with A still on top... stuck → **reject** ✓

## Worked Example 2: Even-Length Palindromes {wwᴿ | w ∈ {a,b}*}

```
States: {q₀, q₁, q₂}
Σ = {a, b}, Γ = {a, b, $}
Start: q₀, Accept: {q₂}

Phase 1 (push half):
  δ(q₀, a, ε) = {(q₀, a)}      -- push input symbols
  δ(q₀, b, ε) = {(q₀, b)}
  δ(q₀, ε, ε) = {(q₁, ε)}      -- nondeterministically guess midpoint

Phase 2 (match second half):
  δ(q₁, a, a) = {(q₁, ε)}      -- pop if input matches stack top
  δ(q₁, b, b) = {(q₁, ε)}
  δ(q₁, ε, ε) = {(q₂, ε)}      -- stack empty: accept
```

Acceptance is nondeterministic: the PDA "guesses" the midpoint. The DFA for this language does not exist (the language is not regular), but the NPDA accepts it.

## Deterministic PDAs

A **DPDA** has at most one applicable transition for each (state, input symbol or ε, stack top) combination. But unlike DFA vs NFA, **deterministic and nondeterministic PDAs are NOT equivalent**.

**Deterministic CFLs (DCFLs)**: recognized by DPDAs. Examples: {aⁿbⁿ}, arithmetic expressions with the standard grammar. All practical programming language grammars are DCFLs.

**Proper CFL \ DCFL**: {wwᴿ \| w ∈ {a,b}\*} (even palindromes). Requires nondeterminism to find the midpoint. No DPDA can recognize it.

**Why?** A DPDA processing aⁿbⁿ uses the stack deterministically (push on a, pop on b). But for wwᴿ, the machine must decide when to switch from pushing to matching — this requires a nondeterministic guess about the midpoint. This separation mirrors the separation between deterministic and nondeterministic computation in complexity theory.

## Acceptance by Empty Stack

An alternative acceptance criterion: the PDA accepts w if it reaches the end of input with an **empty stack** (regardless of current state).

**Theorem.** Acceptance by empty stack and acceptance by final state are equivalent: for every PDA M_f using final states, there is a PDA M_e using empty stack with L(M_e) = L(M_f), and vice versa.

The conversions add a few extra states and transitions to drain the stack (for the F→E direction) or to transfer to a new accept state when the stack empties (for E→F direction). This equivalence is technically important for the PDA → CFG direction of the equivalence theorem (covered in the next lesson).

## Why One Stack is the Right Amount

| Memory resource | Model | Language class |
|----------------|-------|---------------|
| None (finite states only) | DFA/NFA | Regular |
| One stack | PDA | Context-free |
| Two stacks (or one tape) | TM | Recursively enumerable (all decidable + undecidable) |
| Bounded stack or queue | Various | Intermediate classes |

One stack is exactly the right amount of memory to capture "one level of nesting" — matching the opening of a structure to its closing. Two stacks (simulated by a TM tape) provide unrestricted computation power.
