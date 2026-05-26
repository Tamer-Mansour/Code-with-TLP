# Complexity Classes: P and NP

Computability theory asks *what* can be computed. Complexity theory asks *how efficiently*. The most important open question in computer science is whether every efficiently verifiable problem is also efficiently solvable — the **P vs NP question**.

## Time Complexity

For a TM M that always halts, define its **time complexity** as the function t : ℕ → ℕ where t(n) is the maximum number of steps M takes on any input of length n (worst-case):

> t(n) = max{steps(M, w) \| |w| = n}

**Time complexity class:**
> **TIME(f(n))** = {L \| some single-tape TM decides L in O(f(n)) steps}

## The Class P

> **P** = ∪_{k≥1} TIME(nᵏ) — languages decidable in **polynomial time**.

**P is robust:** Switching between single-tape TM, multi-tape TM, RAM model, or any other "reasonable" deterministic model changes the running time by at most a polynomial factor. This robustness makes P a meaningful definition of "feasibly solvable," independent of implementation details.

### Problems in P

| Problem | Algorithm | Time |
|---------|-----------|------|
| Sorting n numbers | Merge sort | O(n log n) |
| Shortest path (SSSP) | Dijkstra | O(E + V log V) |
| Primality testing | AKS (Agrawal-Kayal-Saxena, 2002) | O((log n)^6) |
| Linear programming | Ellipsoid method (Khachian, 1979) | Polynomial in input size |
| 2-SAT | Implication graph + SCC | O(n + m) |
| Bipartite matching | Hopcroft-Karp | O(E√V) |
| Graph connectivity | BFS/DFS | O(V + E) |
| Context-free membership (CYK) | Dynamic programming | O(n³·\|G\|) |

## The Class NP

A language L is in **NP** if there is a **polynomial-time verifier**: a deterministic TM V and a polynomial p(n) such that:

> w ∈ L ⟺ ∃ certificate c with |c| ≤ p(|w|) and V accepts ⟨w, c⟩ in polynomial time.

The certificate c is a "short proof" that w ∈ L. The verifier checks c efficiently.

**Equivalent definition via NTMs:** L ∈ NP iff a nondeterministic TM decides L in polynomial time (the nondeterminism "guesses" the certificate).

### Problems in NP

| Problem | Certificate | Verifier |
|---------|------------|---------|
| SAT (Boolean satisfiability) | Truth assignment | Evaluate formula under assignment |
| 3-SAT | Truth assignment | Check all 3-literal clauses |
| CLIQUE | The k vertices | Check all pairs are edges, k vertices |
| VERTEX-COVER | The k vertices | Check every edge has an endpoint in the set |
| HAMILTONIAN-PATH | The path (vertex order) | Check each vertex appears once, adjacent pairs are edges |
| SUBSET-SUM | The subset | Check sum equals target |
| GRAPH-COLORING (k colors) | Color assignment | Check no two adjacent vertices share a color |
| FACTORING (composite?) | A non-trivial factor | Multiply and verify |

Clearly P ⊆ NP: a polynomial-time decider is a verifier with the empty certificate.

## NP-Completeness

**Definition.** A language B is **NP-hard** if every A ∈ NP satisfies A ≤_p B (polynomial-time many-one reduction).

**Definition.** B is **NP-complete** if B ∈ NP and B is NP-hard.

**Cook-Levin Theorem (1971/1972).** SAT is NP-complete.

The original proof (Cook, 1971; Levin independently, 1973) encodes an arbitrary polynomial-time NTM computation as a Boolean formula. Each step of the NTM is encoded as clauses ensuring the transition rules are respected. The formula is satisfiable iff the NTM accepts — and the formula has polynomial size in the NTM's running time.

### Consequences of Cook-Levin

Once SAT is known NP-complete, we can prove other problems NP-complete by:
1. Show the problem is in NP (give a polynomial verifier).
2. Reduce SAT (or another known NP-complete problem) to it in polynomial time.

## The P vs NP Question

**If P = NP:** Every problem whose solutions can be *quickly verified* can also be *quickly found*. This would imply:
- Cryptographic schemes based on hardness (RSA, discrete log, AES secrecy) would need re-evaluation.
- Protein folding could be solved efficiently.
- Mathematical proofs could be found automatically.

**If P ≠ NP:** There exist problems (like SAT) that are fundamentally harder to solve than to verify. This is the widely held belief, supported by decades of failed attempts to find polynomial-time algorithms for NP-complete problems.

The P vs NP problem is listed as one of the **Clay Millennium Prize Problems** (prize: $1,000,000). Despite enormous effort, no resolution is known.

## co-NP

**co-NP** = {L \| L̄ ∈ NP} = languages whose complements are in NP.

Equivalently: L ∈ co-NP iff there is a polynomial-time **refuter**: when w ∉ L, there is a short certificate proving w ∉ L.

| Problem | co-NP version |
|---------|--------------|
| TAUTOLOGY (every assignment satisfies?) | The complement of SAT — no short refutation of a formula that is always true |
| NON-HAMILTONIAN | No short proof a graph lacks a Ham. path |

Clearly co-P = P (P is closed under complement). So P ⊆ NP ∩ co-NP.

Whether NP = co-NP is open (most believe NP ≠ co-NP). If NP ≠ co-NP, then P ≠ NP (since P ⊆ NP ∩ co-NP).

## The Complexity Hierarchy

```
L ⊆ NL ⊆ P ⊆ NP ⊆ PSPACE ⊆ EXPTIME ⊆ NEXPTIME ⊆ …
```

Known strict separations:
- **P ≠ EXPTIME** (by the time hierarchy theorem — a language in TIME(2^n) cannot be in TIME(n^k) for any k).
- **NL ≠ PSPACE** (known, though the intermediate separations P vs NP remain open).

The time and space hierarchy theorems guarantee that giving more resources strictly expands the set of solvable problems, but pinpointing exactly where common classes like P and NP fall relative to each other remains one of the deepest open problems in mathematics.
