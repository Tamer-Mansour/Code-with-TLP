# PDA–CFG Equivalence in Detail

The equivalence between pushdown automata and context-free grammars is one of the central results of the field. It shows that two very different formalisms — one operational (PDA) and one generative (CFG) — capture exactly the same set of languages. This lesson works through both directions carefully, with examples.

## Theorem Statement

**Theorem.** A language L is context-free if and only if some PDA recognizes L.

**Proof overview:**
- (CFG → PDA): Given a CFG G, build a PDA P that simulates leftmost derivations of G nondeterministically.
- (PDA → CFG): Given a PDA P, build a CFG G whose variables encode the stack behaviour of P.

## Direction 1: CFG → PDA (Simulating Leftmost Derivations)

Given CFG G = (V, Σ, R, S), construct PDA P with three states: q_start, q_loop, q_accept.

### Construction

**Transition 1** (initialize): δ(q_start, ε, ε) = {(q_loop, S)} — push start symbol S.

**Transition 2** (expand): For each rule A → w = X₁X₂…Xₖ ∈ R:
δ(q_loop, ε, A) = {(q_loop, XₖXₖ₋₁…X₁)} — pop A, push w reversed (so X₁ is on top).

**Transition 3** (match): For each terminal a ∈ Σ:
δ(q_loop, a, a) = {(q_loop, ε)} — read a from input, pop a from stack.

**Transition 4** (accept): δ(q_loop, ε, ε) = {(q_accept, ε)} — when stack is empty, accept.

### Correctness Intuition

The stack at any point holds the remaining sentential form of the current leftmost derivation. When a variable A is on top, the PDA nondeterministically picks a rule A → w and replaces A with w (reversed on stack so the leftmost symbol is accessible). When a terminal a is on top and the input also has a, they are matched and both consumed. The PDA accepts iff it produces a complete leftmost derivation of the input.

### Example: S → aSb | ε

PDA transitions:
- δ(q_start, ε, ε) = {(q_loop, S)}
- δ(q_loop, ε, S) = {(q_loop, bSa), (q_loop, ε)} — rules S → aSb (push b,S,a reversed = a,S,b) and S → ε
- δ(q_loop, a, a) = {(q_loop, ε)}
- δ(q_loop, b, b) = {(q_loop, ε)}
- δ(q_loop, ε, ε) = {(q_accept, ε)}

**Trace on "aabb":**
1. Push S: stack = [S]
2. Expand S → aSb: pop S, push b,S,a → stack = [a,S,b] (a on top)
3. Match a: pop a, advance input → stack = [S,b], input = "abb"
4. Expand S → aSb: pop S, push b,S,a → stack = [a,S,b,b]
5. Match a: pop a, advance → stack = [S,b,b], input = "bb"
6. Expand S → ε: pop S, push nothing → stack = [b,b]
7. Match b: pop b → stack = [b], input = "b"
8. Match b: pop b → stack = [], input = ""
9. Accept ✓

## Direction 2: PDA → CFG (The [p A q] Construction)

Given PDA P = (Q, Σ, Γ, δ, q₀, F) (using acceptance by **empty stack** — convert to this mode first), construct CFG G.

### Variable Scheme

Introduce a variable **[p A q]** for each triple (p, A, q) ∈ Q × Γ × Q.

**Intuition:** [p A q] generates all strings that can take the PDA from state p with symbol A on top to state q with A removed from the stack. That is, [p A q] derives all strings that cause P to go from configuration (p, w, Aγ) to (q, ε, γ) for some w.

### Rules

**Start rule:** S → [q₀ $ q_f] for each q_f ∈ Q.
($ is the initial stack symbol; the PDA starts with q₀ and $ on the stack.)

**For each PDA transition** (r, B₁B₂…Bₘ) ∈ δ(p, a, A):

For every sequence of intermediate states r₀ = r, r₁, r₂, …, r_{m-1}, rₘ = q ∈ Q:

```
[p A q] → a [r₀ B₁ r₁] [r₁ B₂ r₂] … [r_{m-1} Bₘ rₘ]
```

(Here a ∈ Σ ∪ {ε}.)

**Special case** m = 0 (pop A without pushing anything): [p A r] → a for the state r that the PDA moves to.

### Concrete Example

PDA for {aⁿbⁿ}: states {q₀, q₁}, Γ = {A, $}, transitions:
- δ(q₀, a, ε) = {(q₀, A)} — push A
- δ(q₀, b, A) = {(q₁, ε)} — pop A on b
- δ(q₁, b, A) = {(q₁, ε)} — continue popping
- δ(q₁, ε, $) = {(q₁, ε)} — pop $ to empty stack

Variable [q₀ $ q₁] generates strings that take the PDA from q₀ with $ on top to q₁ with stack empty — which are exactly the strings aⁿbⁿ.

### Correctness (Claim)

[p A q] derives w iff starting in state p with A on top of the stack, reading w takes the PDA to state q with A removed.

The proof is by induction on the number of steps in the PDA computation, mirroring the recursive structure of the grammar.

## Simplified PDA: Acceptance by Empty Stack

For the PDA → CFG construction, it is cleaner to use **acceptance by empty stack** (the PDA accepts when the stack is empty, regardless of state). Every accept-by-final-state PDA has an equivalent accept-by-empty-stack PDA:

**Conversion:** Add a new start state q_s that pushes a bottom marker $, then ε-transitions to the original start. Add a new state q_e. From every accept state q_f, add ε-transitions that pop the entire stack and ε-transition to q_e (which empties the stack). Then q_e accepts by empty stack.

## Summary of the Equivalence

The CFG ↔ PDA equivalence establishes:

1. **CFGs** (generative/algebraic model) and **PDAs** (automaton/computational model) describe exactly the same languages: the context-free languages.

2. Programming language parsers (recursive descent, LR parsers) are deterministic PDAs running in linear or near-linear time.

3. The stack is the key computational resource: automata with finite memory → regular; automata with one stack → context-free; automata with two stacks (or a tape) → Turing-complete.

4. This equivalence has practical impact: the derivation sequence in a CFG corresponds directly to the trace of a parser, which is why CFGs are the universal notation for language grammars in compiler textbooks.
