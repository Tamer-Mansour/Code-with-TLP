# BFS Shortest Path

Given an undirected graph and two node IDs, find the **length** (number of edges) of the shortest path between them using Breadth-First Search. If no path exists, output `-1`.

## Input Format

```
N E
u1 v1
u2 v2
...
src dst
```

- First line: `N` nodes (numbered `0` to `N-1`) and `E` edges.
- Next `E` lines: each edge as two space-separated integers `u v`.
- Last line: source node `src` and destination node `dst`.

## Output Format

A single integer: the shortest path length, or `-1` if unreachable.

## Examples

**Example 1**
```
Input:
4 4
0 1
1 2
2 3
0 3
0 3

Output:
1
```
(Direct edge from 0 to 3.)

**Example 2**
```
Input:
5 4
0 1
1 2
2 3
3 4
0 4

Output:
4
```
(Path: 0 → 1 → 2 → 3 → 4.)

**Example 3**
```
Input:
4 2
0 1
2 3
0 3

Output:
-1
```
(Nodes 0 and 3 are in different components.)
