# Graph Basics: Definitions and Terminology

A **graph** `G = (V, E)` consists of a finite set of **vertices** (nodes) V and a set of **edges** E, where each edge connects two vertices. Graphs are one of the most versatile structures in computer science — they model networks, relationships, dependencies, and state transitions.

## Types of Graphs

| Type | Description | CS Example |
|------|-------------|-----------|
| **Simple graph** | No self-loops, no multi-edges | Social network (users and friendships) |
| **Multigraph** | Multiple edges allowed between the same pair | Transport routes (multiple roads between cities) |
| **Directed graph (digraph)** | Edges have direction: `(u → v)` | Web links; dependency graphs |
| **Weighted graph** | Edges carry a numerical weight | Road distances; network bandwidth |
| **Bipartite graph** | Vertices split into two disjoint sets; edges only cross | Job-worker assignment; bipartite matching |
| **DAG (directed acyclic graph)** | Directed, no cycles | Task scheduling; package dependencies; neural nets |

## Basic Terminology

- **Adjacent (neighbors):** Vertices connected by an edge. In a directed graph, u is an **out-neighbor** of v if `(v → u)` exists.
- **Degree** `deg(v)`: number of edges incident to vertex v.
  - In a directed graph: **in-degree** `indeg(v)` (edges arriving) and **out-degree** `outdeg(v)` (edges leaving).
- **Path:** A sequence `v₀, v₁, …, vₖ` of vertices where each consecutive pair `(vᵢ, vᵢ₊₁)` is an edge, with no vertex repeated.
- **Cycle:** A path that starts and ends at the same vertex (with `k ≥ 1`).
- **Connected graph:** An undirected graph where every pair of vertices has a path between them.
- **Strongly connected** (directed): Every vertex is reachable from every other vertex.
- **Weakly connected** (directed): The underlying undirected graph (ignoring edge directions) is connected.

## The Handshaking Lemma

In any undirected graph:
```
Σᵥ deg(v) = 2|E|
```

Every edge contributes exactly 2 to the total degree sum — once for each endpoint.

**Corollary:** The number of vertices with odd degree is always **even**.

**Proof:** `Σ_odd + Σ_even = 2|E|` (even). Since `Σ_even` is even, `Σ_odd` must also be even. Since each odd-degree vertex contributes an odd amount, there must be an even number of them.

**CS application:** In a network where each device has a connection count, the total connection count is always even — useful for consistency checking in network topology databases.

**Directed version:** `Σᵥ indeg(v) = Σᵥ outdeg(v) = |E|`. Each directed edge contributes 1 to in-degree and 1 to out-degree totals.

## Common Graph Families

| Name | Notation | Vertices | Edges | Description |
|------|---------|----------|-------|-------------|
| Complete graph | `Kₙ` | n | `n(n−1)/2` | Every pair connected |
| Cycle graph | `Cₙ` | n | n | Single cycle through all |
| Path graph | `Pₙ` | n | `n−1` | Linear chain |
| Complete bipartite | `Kₘ,ₙ` | m+n | mn | Every left-right pair connected |
| Tree | — | n | `n−1` | Connected, acyclic |

**Why `Kₙ` has `n(n−1)/2` edges:** C(n,2) — choosing 2 vertices from n for each edge.

## Representing Graphs

The two standard representations trade space for time efficiency:

### Adjacency Matrix

An `n × n` matrix A where `A[i][j] = 1` if edge `(i,j)` exists (0 otherwise). For weighted graphs, store the weight instead of 1.

- **Space:** O(n²) — even if the graph is sparse (few edges).
- **Edge lookup:** O(1) — just check `A[i][j]`.
- **Enumerate neighbors:** O(n) — scan a whole row.
- **Best for:** Dense graphs (where `|E| ≈ n²`).

### Adjacency List

Each vertex stores a list of its neighbors. Total space is proportional to the number of edges.

- **Space:** O(n + |E|) — optimal for sparse graphs.
- **Edge lookup:** O(degree(v)) — scan the list.
- **Enumerate neighbors:** O(degree(v)) — just iterate.
- **Best for:** Sparse graphs (most real-world graphs: social networks, road maps, the web).

**Comparison example:** A graph of 1,000 vertices with 2,000 edges:
- Adjacency matrix: 1,000,000 entries.
- Adjacency list: ~4,000 entries. 250× more efficient.

**Implementation note:** In Python, an adjacency list is typically a `dict[int, list[int]]` or `list[list[int]]`.

```python
# Adjacency list for a 4-vertex graph
adj = {1: [2, 3], 2: [1, 4], 3: [1, 4], 4: [2, 3]}
```

## Graph Isomorphism

Two graphs G₁ = (V₁, E₁) and G₂ = (V₂, E₂) are **isomorphic** if there is a bijection `f: V₁ → V₂` such that `(u, v) ∈ E₁` iff `(f(u), f(v)) ∈ E₂`. Isomorphic graphs have the same structure — just different vertex labels.

**Quick checks for NON-isomorphism:**
- Different number of vertices or edges.
- Different degree sequences (multiset of all vertex degrees).
- Different number of cycles of some length.
- Different number of connected components.

Graph isomorphism is a fascinating open problem in complexity theory: it is not known to be in P or NP-complete. The best general algorithms run in quasi-polynomial time.

## Subgraphs and Connectivity

- A **subgraph** H of G is a graph with `V(H) ⊆ V(G)` and `E(H) ⊆ E(G)`.
- An **induced subgraph** on vertex set S contains all edges of G between vertices of S.
- **Connected components** are the maximal connected subgraphs.

For a graph G with n vertices and c connected components:
```
|E| ≥ n − c
```
Equality holds precisely when G is a forest (acyclic graph — a collection of c trees).

## Bipartite Graphs

A graph G is **bipartite** iff its vertices can be 2-colored — partitioned into sets L and R so every edge goes from L to R.

**Theorem:** G is bipartite iff it contains **no odd-length cycles**.

**CS applications:**
- **Matching problems:** Assigning workers to tasks, students to dorms. Bipartite maximum matching is solvable in polynomial time (e.g., Hungarian algorithm, Hopcroft-Karp).
- **Scheduling:** Jobs and machines form a bipartite graph; an edge means the job can run on that machine.
- **Recommendation systems:** Users on one side, items on the other; edges are ratings.

## Planarity

A graph is **planar** if it can be drawn in the plane without edge crossings.

**Euler's formula for connected planar graphs:**
```
V − E + F = 2
```
where F is the number of faces (regions), including the outer infinite face.

**Corollary:** For simple planar graphs with `V ≥ 3`: `E ≤ 3V − 6`.

**Example:** `K₅` has 10 edges but `3(5)−6 = 9`, so `K₅` is non-planar. Similarly, `K₃,₃` is non-planar. **Kuratowski's theorem:** G is planar iff it contains no subdivision of `K₅` or `K₃,₃` as a subgraph.

**CS application:** PCB routing — electronic components connected by non-crossing wires must form a planar graph.

## Summary

Graphs model pairwise relationships. Understanding their vocabulary — vertices, edges, degree, paths, and connectivity — is the foundation for algorithms like BFS, DFS, shortest paths, maximum flow, and minimum spanning trees that appear throughout computer science.

| Concept | Key fact |
|---------|---------|
| Handshaking Lemma | `Σ deg = 2|E|`; number of odd-degree vertices is even |
| Complete graph Kₙ | `n(n−1)/2` edges |
| Adjacency matrix | O(n²) space; O(1) lookup |
| Adjacency list | O(n+|E|) space; best for sparse graphs |
| Bipartite | Bipartite iff no odd cycles |
| Planar | V − E + F = 2; E ≤ 3V − 6 |
