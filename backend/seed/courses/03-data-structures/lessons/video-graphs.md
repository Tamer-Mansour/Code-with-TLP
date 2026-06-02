# Video: Graph Algorithms — BFS, DFS, and Shortest Paths

This video covers the two fundamental graph traversal algorithms (BFS and DFS), demonstrates how BFS finds shortest paths in unweighted graphs, and introduces Dijkstra's algorithm for weighted graphs.

**Key takeaways:**
- Mark nodes as visited on **enqueue** (BFS) or on **first visit** (DFS), never on dequeue/pop, to guarantee O(V + E) time without re-processing nodes.
- BFS distance from a source gives the minimum hop count; for weighted shortest paths you need Dijkstra's algorithm (a BFS generalised with a priority queue).
- Topological sort (Kahn's algorithm) is just BFS restricted to DAGs — processing nodes whose in-degree drops to zero first.

**Approximate timestamps:**
- 0:00 — Adjacency list vs. adjacency matrix: which to pick
- 10:00 — BFS: queue, distance array, shortest path proof
- 22:00 — DFS: recursive vs. iterative, pre/post-order, cycle detection
- 34:00 — Topological sort: Kahn's BFS algorithm
- 44:00 — Dijkstra's algorithm with a min-heap (intro)
