# BFS Shortest Path

Given an undirected unweighted graph and a source vertex, find the shortest path distance (in number of edges) from the source to every other reachable vertex.

## Input Format

- Line 1: two integers `V` and `E` — the number of vertices (0-indexed: 0 to V-1) and edges.
- The next `E` lines: each line contains two integers `u v` representing an undirected edge between u and v.
- Last line: a single integer `s` — the source vertex.

## Output Format

For each vertex from 0 to V-1, print one line: `vertex distance`  
If a vertex is unreachable from `s` print `vertex -1`.

## Constraints

- `1 <= V <= 500`
- `0 <= E <= 10000`
- `0 <= s < V`

## Examples

**Example 1**
```
Input:
5 5
0 1
0 2
1 3
2 3
3 4
0

Output:
0 0
1 1
2 1
3 2
4 3
```

**Example 2**
```
Input:
4 2
0 1
2 3
0

Output:
0 0
1 1
2 -1
3 -1
```
