# Count Connected Components

Given an undirected graph with V vertices (0-indexed) and E edges, count the number of **connected components**.

A connected component is a maximal set of vertices such that there is a path between every pair of vertices in the set. Isolated vertices (no edges) each form their own component.

## Input Format

```
V E
u1 v1
u2 v2
...
```

- Line 1: integers V (1 ≤ V ≤ 10000) and E (0 ≤ E ≤ 50000).
- Lines 2..E+1: each line contains two integers `u v` (undirected edge, 0-indexed vertices).

## Output Format

Print a single integer: the number of connected components.

## Examples

Input:
```
6 4
0 1
1 2
3 4
5 5
```
Output:
```
3
```
(Components: {0,1,2}, {3,4}, {5})

Input:
```
5 0
```
Output:
```
5
```
(No edges — every vertex is its own component)

Input:
```
4 6
0 1
0 2
0 3
1 2
1 3
2 3
```
Output:
```
1
```
(Complete graph — one component)

## Notes

- Self-loops (u == v) do not create new components.
- The graph may be disconnected.
