# Reductions and NP-Completeness Proofs

Polynomial-time reductions are the primary tool for proving NP-hardness. A reduction shows that solving problem B is "at least as hard" as solving problem A: any efficient algorithm for B would give an efficient algorithm for A. This lesson works through three classic reductions in detail.

## Polynomial-Time Reductions

**Definition.** A **polynomial-time many-one reduction** (Cook reduction or Karp reduction) from A to B, written A ≤_p B, is a polynomial-time computable function f : Σ\* → Σ\* such that:

> w ∈ A ⟺ f(w) ∈ B for all w ∈ Σ\*.

**Key theorems:**
- If A ≤_p B and B ∈ P, then A ∈ P.
- If A ≤_p B and A is NP-hard, then B is NP-hard.
- If A ≤_p B and A ≤_p C, then A ≤_p C (transitivity — ≤_p is transitive).

Reductions are one-way: A ≤_p B means B is *at least as hard* as A. To show NP-hardness, reduce from a known NP-complete problem.

## Proving NP-Completeness: The Template

1. **Show B ∈ NP:** Describe a polynomial-time verifier — a program that takes (w, c) and checks in poly time that c is a valid certificate for w ∈ B.

2. **Choose** a known NP-complete problem A (usually SAT, 3-SAT, CLIQUE, or another from Karp's 21).

3. **Reduce A ≤_p B:** Construct a polynomial-time function f such that w ∈ A ⟺ f(w) ∈ B. Prove correctness in both directions.

## Classic Reduction 1: 3-SAT ≤_p CLIQUE

**3-SAT:** Given a CNF formula φ = C₁ ∧ C₂ ∧ … ∧ Cₖ where each clause Cᵢ = (lᵢ₁ ∨ lᵢ₂ ∨ lᵢ₃) has exactly 3 literals, is φ satisfiable?

**CLIQUE:** Given undirected graph G and integer k, does G contain a k-clique (k mutually adjacent vertices)?

**The Reduction.** Given 3-SAT instance φ with k clauses, construct graph G:

- **Nodes:** 3k nodes, grouped into k triples {lᵢ₁, lᵢ₂, lᵢ₃} (one triple per clause).
- **Edges:** Connect node u in clause i to node v in clause j (i ≠ j) if their literals are **not contradictory** (i.e., u ≠ ¬v). No edges within the same clause.
- **Target:** k-clique.

**Correctness.**

(⟹) Suppose φ has a satisfying assignment. In each clause Cᵢ, pick one true literal lᵢ. These k literals form a set S of k nodes, one per clause. Since they're from different clauses (condition for edges) and no two are contradictory (they're all true under the same assignment), all pairs are connected → S is a k-clique. ✓

(⟸) Suppose G has a k-clique S. S contains exactly one node per clause (no edges within a clause, so at most one per clause; k nodes and k clauses forces exactly one per clause). Set each literal in S to true. The k literals in S are pairwise non-contradictory (they're pairwise connected), so this is a consistent assignment. Extending to all other variables arbitrarily gives a satisfying assignment. ✓

**Polynomial time:** Creating 3k nodes and at most (3k)²/2 edges is O(k²). ✓

## Classic Reduction 2: 3-SAT ≤_p VERTEX-COVER

**VERTEX-COVER:** Given graph G and integer k, does G have a set S ⊆ V with |S| ≤ k such that every edge has at least one endpoint in S?

**The Reduction.** Given 3-SAT instance φ with n variables and m clauses, set k = n + 2m. Construct G:

**Variable gadgets:** For each variable xᵢ, add an edge between two nodes labeled xᵢ and x̄ᵢ. Exactly one of these must be in any vertex cover of this edge.

**Clause gadgets:** For each clause Cᵢ = (lᵢ₁ ∨ lᵢ₂ ∨ lᵢ₃), add a triangle (three nodes aᵢ, bᵢ, cᵢ connected to each other). Connect aᵢ to the literal node lᵢ₁, bᵢ to lᵢ₂, cᵢ to lᵢ₃ (in the corresponding variable gadget).

**Correctness sketch.**

The n variable gadget edges each need exactly one endpoint → at least n nodes from variable gadgets. The m clause triangles each need at least 2 out of 3 nodes → at least 2m nodes. So k = n + 2m is the minimum possible.

(⟹) A satisfying assignment: for each variable, include the *true* literal node. For each clause, since at least one literal is true, its clause-triangle node connected to a true literal can be *excluded* — include the other two triangle nodes. Total: n + 2m = k nodes. Every edge is covered. ✓

(⟸) A vertex cover of size k: exactly one node per variable gadget → defines an assignment. At least two nodes per clause triangle → at least one triangle node is excluded. The excluded node is connected to a literal node → that literal must be in the cover → that literal is set true → the clause is satisfied. ✓

## Classic Reduction 3: SAT ≤_p 3-SAT

**The Reduction.** Given a CNF formula φ with clauses of arbitrary length, convert each clause to 3-literal clauses:

- **Clause of 1 literal** (l): Replace with (l ∨ y₁ ∨ y₂) ∧ (l ∨ y₁ ∨ ȳ₂) ∧ (l ∨ ȳ₁ ∨ y₂) ∧ (l ∨ ȳ₁ ∨ ȳ₂) where y₁, y₂ are fresh variables. This is satisfiable iff l = true.
- **Clause of 2 literals** (l₁ ∨ l₂): Replace with (l₁ ∨ l₂ ∨ y) ∧ (l₁ ∨ l₂ ∨ ȳ) where y is fresh. Satisfiable iff l₁ ∨ l₂.
- **Clause of k > 3 literals** (l₁ ∨ l₂ ∨ … ∨ lₖ): Introduce fresh variables y₁, …, yₖ₋₃ and replace with:
  ```
  (l₁ ∨ l₂ ∨ y₁) ∧ (ȳ₁ ∨ l₃ ∨ y₂) ∧ (ȳ₂ ∨ l₄ ∨ y₃) ∧ … ∧ (ȳₖ₋₃ ∨ lₖ₋₁ ∨ lₖ)
  ```
  This chain is satisfiable iff at least one lᵢ is true. The y variables propagate the "at least one satisfied" property along the chain.

**Polynomial time:** The output has O(|φ|) clauses. ✓

This reduction shows 3-SAT is NP-hard (SAT is NP-hard, SAT ≤_p 3-SAT, therefore 3-SAT is NP-hard). Combined with 3-SAT ∈ NP, we get 3-SAT is NP-complete.

## Karp's 21 NP-Complete Problems (1972)

Richard Karp's landmark 1972 paper showed 21 fundamental combinatorial problems are NP-complete by a chain of reductions from SAT. This established that NP-completeness is not rare — it is ubiquitous across combinatorics, scheduling, and optimization.

Selected problems and their reductions:

| Problem | Reduced from |
|---------|-------------|
| SAT | Cook-Levin (directly) |
| 3-SAT | SAT |
| CLIQUE | 3-SAT |
| VERTEX-COVER | 3-SAT |
| INDEPENDENT-SET | VERTEX-COVER (complement) |
| SET-COVER | VERTEX-COVER |
| HAM-PATH | VERTEX-COVER |
| TSP (decision) | HAM-PATH |
| SUBSET-SUM | EXACT-COVER |
| 3-COLORING | 3-SAT (gadgets per variable and clause) |
| PARTITION | SUBSET-SUM |
| BIN-PACKING | PARTITION |

## Space Complexity: PSPACE and Beyond

| Class | Definition | Key problems |
|-------|-----------|-------------|
| **L** (logspace) | DTM using O(log n) space | Graph reachability |
| **NL** | NTM with O(log n) space | Graph reachability (NL-complete) |
| **P** | Polynomial time | Everything in P above |
| **NP** | Polynomial time NTM | SAT, CLIQUE, ... |
| **PSPACE** | Polynomial space (any time) | Quantified Boolean Formula (QBF) |
| **EXPTIME** | Exponential time | Chess (n×n board), Go |

**Strict separations known:** P ≠ EXPTIME (time hierarchy), L ≠ PSPACE (space hierarchy). The intermediate separations (P vs NP, NP vs PSPACE) remain open.

**PSPACE-completeness:** TQBF (true quantified Boolean formula) is PSPACE-complete. Intuitively, PSPACE-complete problems require reasoning about all possible move sequences in a two-player game, not just verifying a single certificate.
