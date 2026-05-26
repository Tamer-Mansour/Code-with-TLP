# Detect Cycle in Undirected Graph

Given an undirected graph, determine whether it contains **at least one cycle**. Use Union-Find (Disjoint Set Union) for an elegant O(E · α(V)) solution.

## Input Format

```
V E
u1 v1
u2 v2
...
```

- Line 1: integers V (vertices, 1 ≤ V ≤ 10000) and E (edges, 0 ≤ E ≤ 20000).
- Lines 2..E+1: each line contains two integers `u v` representing an undirected edge between vertex u and vertex v (0-indexed vertices).

## Output Format

Print `YES` if the graph contains a cycle, otherwise print `NO`.

## Examples

Input:
```
4 4
0 1
1 2
2 3
3 0
```
Output:
```
YES
```

Input:
```
4 3
0 1
1 2
2 3
```
Output:
```
NO
```

## Notes

- A graph with no edges (E=0) has no cycle.
- A graph with V vertices needs at least V edges to guarantee a cycle.
- Self-loops (u == v) count as a cycle.
