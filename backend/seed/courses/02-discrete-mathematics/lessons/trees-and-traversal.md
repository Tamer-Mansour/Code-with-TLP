# Trees, Paths, and Graph Traversal

## Trees

A **tree** is a connected, acyclic undirected graph. Trees are among the most important structures in computer science — they model file systems, parse trees, decision trees, heap structures, and hierarchical data of all kinds.

### Key Properties of Trees (all equivalent for connected graphs with n vertices)

The following statements about a connected graph G with n vertices are all equivalent:

1. G is a tree (connected and acyclic).
2. G has exactly `n − 1` edges.
3. Any two vertices are connected by exactly **one** path.
4. Removing any edge disconnects the graph.
5. Adding any edge between non-adjacent vertices creates exactly one cycle.

**Proof that (1) ⟹ (2) [sketch]:** Use induction on n. A tree with one vertex has 0 = 1−1 edges. For a tree with n > 1 vertices: pick a leaf (a vertex of degree 1 — which must exist in any tree; prove by contradiction using the fact that a finite path must terminate). Remove it and its edge. By induction, the remaining tree has n−2 edges. Adding back the leaf and its edge gives n−1 total. QED.

### Rooted Trees

A **rooted tree** designates one vertex as the **root**, imposing a natural parent-child hierarchy:
- **Parent:** The vertex directly above on the unique path to the root.
- **Children:** Vertices directly below.
- **Leaf:** A vertex with no children.
- **Height:** The length of the longest root-to-leaf path.
- **Depth:** The length of the path from root to a given vertex.

**Binary tree:** Each vertex has at most 2 children. A full binary tree of height h has at most `2^(h+1) − 1` vertices and at least `h + 1` vertices (a path).

**Perfect binary tree:** All leaves at the same depth; exactly `2^(h+1) − 1` vertices. The height of a perfect binary tree with n vertices is `⌊log₂ n⌋`.

**Why binary trees are efficient:** A heap of n elements has height `⌊log₂ n⌋`, so insert and delete operations take `O(log n)` time. A balanced BST of n elements also has `O(log n)` height, giving `O(log n)` search.

### Counting Labeled Trees

**Cayley's Formula:** The number of distinct labeled trees on n vertices is `n^(n−2)`.

- n=2: `2^0 = 1` tree (a single edge).
- n=3: `3^1 = 3` labeled trees.
- n=4: `4^2 = 16` labeled trees.

Cayley's formula is proven via **Prüfer sequences** — a bijection between labeled trees and sequences of length n−2 over {1,…,n}.

## Spanning Trees

A **spanning tree** of a connected graph G is a subgraph T such that:
1. T is a tree (connected and acyclic).
2. T includes every vertex of G.

Every connected graph has at least one spanning tree (remove edges from cycles until none remain).

**Minimum Spanning Tree (MST):** When edges have weights, the MST minimizes the total weight. Solved efficiently by:
- **Kruskal's algorithm:** Sort edges by weight, add each edge if it doesn't form a cycle (use union-find) — `O(|E| log |E|)`.
- **Prim's algorithm:** Grow the tree greedily from one vertex using a priority queue — `O((|V|+|E|) log |V|)` with a binary heap.

**Application:** MST gives the cheapest way to connect n cities with n−1 roads, the minimum cable cost to network a building, and the backbone of Ethernet spanning-tree protocol (STP).

## Graph Traversal: BFS and DFS

The two fundamental ways to explore a graph systematically are **Breadth-First Search (BFS)** and **Depth-First Search (DFS)**. They differ in the order vertices are explored.

### Breadth-First Search (BFS)

Explores layer by layer from a source vertex. Uses a **queue** (FIFO).

```
function BFS(graph, start):
    queue = [start]
    visited = {start}
    distance = {start: 0}
    while queue not empty:
        v = dequeue(queue)
        for each neighbor u of v:
            if u not in visited:
                mark u visited
                distance[u] = distance[v] + 1
                enqueue(queue, u)
```

**Key properties of BFS:**
- Finds the **shortest path** (minimum edge count) from source to every reachable vertex.
- Time complexity: O(|V| + |E|).
- Used in: shortest path in unweighted graphs, level-order tree traversal, finding all vertices within k hops, social network degree separation.

### Depth-First Search (DFS)

Explores as far as possible down one path before backtracking. Uses a **stack** (or recursion).

```
function DFS(graph, v, visited):
    mark v as visited
    process(v)
    for each neighbor u of v:
        if u not visited:
            DFS(graph, u, visited)
```

**Key properties of DFS:**
- Runs in O(|V| + |E|) time.
- **DFS tree / forest:** The edges used to discover new vertices form a forest.
- **DFS timestamps:** Assign a discovery time and finish time to each vertex — used in advanced algorithms.
- **Back edges** (to ancestors): indicate cycles in an undirected graph.
- Used in: cycle detection, topological sorting, strongly connected components (Tarjan's, Kosaraju's).

### BFS vs. DFS Comparison

| Property | BFS | DFS |
|----------|-----|-----|
| Data structure | Queue | Stack (or recursion) |
| Shortest paths? | Yes (unweighted) | No |
| Detects cycles? | Yes | Yes |
| Memory | O(|V|) — entire frontier stored | O(|V|) — recursion depth |
| Applications | Shortest path, level order | Topological sort, SCCs |

## Topological Sorting

A **topological sort** of a DAG is a linear ordering of vertices such that for every directed edge `(u → v)`, u appears before v.

**Algorithm (DFS-based):**
1. Run DFS.
2. When a vertex is **finished** (all descendants processed), push it to a stack.
3. The stack's order (top to bottom) is the topological sort.

**Algorithm (BFS/Kahn's):**
1. Compute in-degrees of all vertices.
2. Add all vertices with in-degree 0 to a queue.
3. Repeat: dequeue v, add v to the order, decrement in-degree of each neighbor; enqueue newly zero-in-degree vertices.

**Example:** Package dependency resolution (apt, npm). Packages are vertices; "A depends on B" is an edge `A → B`. Topological sort gives a valid installation order.

**Cycle detection:** If Kahn's algorithm terminates before outputting all vertices, the remaining vertices form a cycle — the dependency graph is not a DAG.

## Euler and Hamiltonian Paths

### Euler Paths and Circuits

An **Euler path** visits every **edge** exactly once.
An **Euler circuit** (Euler tour) is an Euler path that starts and ends at the same vertex.

**Euler's theorem:**
- An Euler circuit exists iff the graph is connected and **every vertex has even degree**.
- An Euler path (non-circuit) exists iff exactly **two vertices have odd degree** (those become the start and end).

**Proof idea (necessity):** Every time the Euler path enters a vertex (other than start/end), it must also leave — consuming edges in pairs. So all intermediate vertices must have even degree.

**Application:** The Seven Bridges of Königsberg problem (which motivated Euler's original 1736 paper). The Königsberg bridge graph has 4 odd-degree vertices, so no Euler path exists.

**Algorithm:** Hierholzer's algorithm finds an Euler circuit in O(|E|) time: repeatedly pick an unexplored edge, follow it, and "stitch" sub-circuits together.

### Hamiltonian Paths and Circuits

A **Hamiltonian path** visits every **vertex** exactly once.
A **Hamiltonian circuit** returns to the start.

Unlike Euler circuits, **no simple characterization is known** for the existence of Hamiltonian circuits. Deciding if one exists is **NP-complete** in general. The Traveling Salesman Problem (TSP) — find the shortest Hamiltonian circuit in a weighted graph — is NP-hard.

**Dirac's theorem:** If every vertex has degree ≥ n/2 in a simple graph on n ≥ 3 vertices, then a Hamiltonian circuit exists. (Sufficient, but not necessary.)

## Graph Coloring

A **proper k-coloring** assigns colors from `{1,…,k}` to vertices so that no two adjacent vertices share a color.

The **chromatic number** χ(G) is the minimum k for which a proper k-coloring exists.

| Graph type | χ(G) | Reason |
|------------|------|--------|
| Bipartite (non-empty) | 2 | Two sides can get two colors |
| Odd cycle `C₅` | 3 | Odd cycles need 3 colors |
| Complete graph `Kₙ` | n | Every pair adjacent |
| Planar graph | ≤ 4 | Four Color Theorem |
| Tree | 2 | Trees are bipartite |

**Four Color Theorem (1976):** Every planar map can be colored with 4 colors so no two adjacent regions share a color. (Proved with extensive computer assistance.)

**CS Applications:**
- **Exam/meeting scheduling:** Courses sharing students are adjacent; color with time slots — need χ(G) colors to avoid conflicts.
- **Register allocation:** A compiler builds an interference graph where two variables are adjacent if they're live simultaneously. Coloring the graph assigns registers.
- **Frequency assignment:** Cell towers sharing coverage areas need different frequencies.

## Summary

| Concept | Key fact |
|---------|---------|
| Tree | Connected, n−1 edges, no cycles; equivalent characterizations |
| Spanning tree | Exists for every connected graph; MST minimizes total weight |
| BFS | Shortest paths, layer order; O(V+E) |
| DFS | Cycle detection, topological sort, SCCs; O(V+E) |
| Topological sort | Linear ordering of DAG; Kahn's (BFS) or DFS-based |
| Euler circuit | Exists iff all degrees even (connected graph) |
| Hamiltonian | NP-complete to decide; no simple characterization |
| Chromatic number | Min colors for proper coloring; planar graphs need ≤ 4 |
