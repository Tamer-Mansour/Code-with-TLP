# TM Variants and the Church-Turing Thesis

Understanding why all "reasonable" models of computation are equivalent is the heart of the Church-Turing thesis. This lesson proves two key equivalences in detail and discusses the broader implications of the thesis.

## Multi-Tape TMs Are Equivalent to Single-Tape TMs

**Theorem.** Every k-tape TM has an equivalent single-tape TM. Specifically, if the k-tape TM M runs in time t(n), the single-tape TM S runs in time O(t(n)²).

### Proof of Equivalence

**Construction.** Given k-tape TM M, construct single-tape TM S that encodes all k tapes on one tape separated by delimiter symbols #.

**Tape layout:** S's single tape contains:
```
#  [tape 1 contents with head marker]  #  [tape 2 contents with head marker]  # … #
```

Each cell of each virtual tape gets a "dotted" variant (e.g., ȧ = "head is here reading a") to mark the virtual head position.

**Simulating one step of M:**

1. **Phase 1 — Read:** S scans its entire tape, locating all k virtual heads and recording their symbols in S's finite state.

2. **Phase 2 — Compute:** S applies M's transition function to determine the new state, the k new symbols to write, and the k head movement directions.

3. **Phase 3 — Write and move:** S scans again, updating each virtual tape cell. When a virtual head moves right, S shifts all content rightward by one cell (inserting a blank) if the head would fall off the allocated region. This takes O(tape length) = O(n + t(n)) time.

**Time analysis:** Each step of M costs O(total tape length) steps for S. After t(n) steps of M, the tape length is at most O(n + t(n)) ≤ O(t(n)) (since t(n) ≥ n for any useful TM). So S uses O(t(n)) steps per M-step, for a total of O(t(n)²). ∎

**Corollary:** Any language decidable by a multi-tape TM in polynomial time is also decidable by a single-tape TM in polynomial time (since (poly)² = poly). This makes the class P robust to the tape model.

## Nondeterministic TMs Are Equivalent to DTMs

**Theorem.** Every nondeterministic TM (NTM) N has an equivalent deterministic TM D. Specifically, if N accepts, D accepts; if N rejects, D rejects; if N loops on some branch, D still correctly decides if N also has accepting or rejecting branches.

### Proof: BFS Simulation

**Construction.** D simulates N by exploring all nondeterministic branches in **breadth-first order** (to ensure no infinite branch prevents D from finding accepting branches).

D uses three tapes:
1. **Input tape:** A read-only copy of the original input w.
2. **Simulation tape:** Used to simulate one branch of N.
3. **Address tape:** Encodes the current "address" — a sequence of integers representing which nondeterministic choice to take at each step.

**Algorithm of D:**

```
for length = 1, 2, 3, …:
    for each address a of length `length` (in lexicographic order):
        copy input w to simulation tape
        simulate N on w, following choices encoded in a
        if N reaches q_accept: D accepts (and halts)
        if N reaches q_reject or runs out of choices: continue to next address
```

**Correctness:** If N accepts w via some accepting branch of length t, D will eventually enumerate the address of that branch (in time O(t)). D never falsely accepts because each simulation follows a valid branch of N.

**Remark:** D may run for exponential time in t, but it always *halts* (it never loops), making it a correct decider if N is a decider.

## Enumerators

An **enumerator** is a TM with a special "print" action: it starts with a blank tape and at any point can print a string to an output tape. The language **enumerated** by E is the set of all strings E ever prints.

**Theorem.** A language L is Turing-recognizable if and only if some enumerator enumerates L.

### Turing-recognizable → Enumerator

Let M recognize L. Build enumerator E:

```
for s = 1, 2, 3, …  (step limit)
    for w = w₁, w₂, …, w_s  (first s strings in shortlex order)
        simulate M on w for s steps
        if M accepts in ≤ s steps: print w
```

Every string w ∈ L is accepted by M in some finite number of steps t. For s ≥ max(t, position of w in shortlex order), E will print w. So every string in L is eventually printed. ✓

E may print duplicates (the same w printed at multiple values of s), but this is allowed.

### Enumerator → Turing-recognizable

Given E, build recognizer M:

```
Run E in parallel; at each print event, compare the printed string to the input w.
If they match, accept.
```

If w ∈ L(E), E eventually prints w, so M accepts w. If w ∉ L(E), M never accepts. ✓

## The Church-Turing Thesis in Practice

When designing a TM algorithm, we invoke the thesis to skip low-level details:

**Example.** Prove that the language CONNECTED = {⟨G⟩ \| G is a connected undirected graph} is decidable.

*High-level description:* On input ⟨G⟩:
1. Parse ⟨G⟩ to extract the adjacency list (computable).
2. Run BFS or DFS from any vertex.
3. If all vertices are visited, accept; otherwise reject.

By Church-Turing, this high-level description corresponds to a valid TM. We trust the standard model of computation can implement BFS on a tape — the details are tedious but mechanical.

**What the thesis does NOT say:**
- It says nothing about time or space. The BFS TM above runs in polynomial time; that's a separate claim to prove.
- It does not say quantum computers are equivalent in speed — only in what they can decide.
- It does not guarantee that "natural" descriptions of algorithms always yield efficient TMs.

## Lambda Calculus Equivalence

Church's **lambda calculus** defines computable functions via anonymous function definitions and β-reduction. A function is lambda-computable iff it is Turing-computable. The proof (Church, Turing, 1936) was one of the first confirmations that two entirely different formalisms agreed on the boundary of computability.

This equivalence has a practical legacy: functional programming languages (Haskell, ML, Lisp) are based on lambda calculus and are computationally equivalent to imperative programs — they can compute the same set of functions, just expressed differently.

## Limits of the Church-Turing Thesis

The thesis is **empirical**, not proven. However, all known evidence supports it:

- Lambda calculus, general recursive functions, register machines, TAG systems, cellular automata (Rule 110), and many other models are all equivalent to TMs.
- No physical system has been shown to compute a function that TMs cannot.
- Quantum computers (BQP) are believed to be strictly faster than classical TMs for some problems (e.g., factoring via Shor's algorithm), but they are not known to decide any language outside the decidable languages.

The strongest current version: the **physical Church-Turing thesis** claims every physically realizable computation can be simulated by a probabilistic TM with polynomial overhead. This remains unproven and is an active area of theoretical physics and computer science research.
