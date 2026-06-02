# Video: Graph Theory — From Definitions to Traversal Algorithms

This video introduces graph theory at a comfortable pace: undirected and directed graphs, trees, connectivity, Euler circuits, Hamiltonian paths, BFS, DFS, and graph coloring, with CS applications highlighted throughout.

**Key takeaways:**

- Graph terminology: vertices, edges, degree, paths, cycles, connected components, and the handshaking lemma (Σ deg = 2|E|).
- Trees are connected acyclic graphs with exactly n−1 edges; spanning trees generalize this to arbitrary connected graphs.
- Euler circuit (visits every edge once) exists iff every vertex has even degree (Königsberg bridges theorem).
- BFS explores level by level and finds shortest paths in unweighted graphs; DFS is recursive and identifies back edges (cycles).
- Graph coloring: the chromatic number χ(G) is the minimum number of colors needed so no two adjacent vertices share a color — NP-hard in general but polynomial for special classes (bipartite: χ = 2).

Watch for the explanation of Kahn's topological sort algorithm and its use in build systems and dependency resolution.
