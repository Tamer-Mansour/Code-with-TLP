# Exercise: Topological Sort

Given a directed acyclic graph (DAG), output the **lexicographically smallest** valid topological ordering of its vertices.

A topological ordering is a linear sequence of vertices such that for every directed edge `(u → v)`, vertex u appears before vertex v in the sequence.

Use **Kahn's algorithm** (BFS-based):
1. Compute the in-degree of every vertex.
2. Initialize a min-heap with all vertices of in-degree 0.
3. Repeatedly extract the smallest-numbered vertex from the heap, add it to the result, and decrement the in-degree of its neighbors (adding newly zero-in-degree neighbors to the heap).
4. Output the result as space-separated vertex numbers.

The input graph is guaranteed to be a DAG (no cycles).
