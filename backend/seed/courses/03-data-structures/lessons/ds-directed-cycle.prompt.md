# Detect Cycle in Directed Graph

Given a directed graph, determine if it contains at least one cycle. Use DFS with three-state colouring (white / gray / black).

## Input Format

- Line 1: V E — number of vertices and edges (1 ≤ V ≤ 10000, 0 ≤ E ≤ 50000)
- Next E lines: u v — directed edge from u to v (0-indexed vertices)

## Output Format

Print `CYCLE` if the graph has at least one cycle, `NO CYCLE` otherwise.

## Examples

**Example 1 — Cycle present:**
```
Input:
4 4
0 1
1 2
2 3
3 1

Output:
CYCLE
```

**Example 2 — DAG (no cycle):**
```
Input:
4 3
0 1
1 2
2 3

Output:
NO CYCLE
```

## Constraints

- Vertices are 0-indexed integers in [0, V−1]
- The graph may have multiple connected components

## Hint

Assign each vertex one of three colours:
- **WHITE (0):** not yet visited
- **GRAY (1):** currently on the DFS recursion stack
- **BLACK (2):** fully processed

A directed cycle exists if and only if DFS encounters a GRAY neighbour (a back edge to an ancestor in the current path).
