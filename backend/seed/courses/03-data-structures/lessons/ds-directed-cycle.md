# Exercise: Detect Cycle in Directed Graph

Use DFS with white-gray-black colouring to detect cycles in a directed graph.

## What You'll Practice

- DFS on directed graphs
- Three-state colouring: unvisited (white), in current path (gray), fully processed (black)
- Recognising a back edge (gray-to-gray) as proof of a cycle

## Key Insight

In an undirected graph, any visited-but-not-parent neighbour indicates a cycle. In a directed graph, you need to distinguish between a node that is "currently on the DFS path" (gray) versus one already fully processed (black). Only a gray-to-gray edge is a cycle — a black node was reached via a different path and is not a problem.

## Input Format

- Line 1: V E (vertices, edges)
- Next E lines: u v (directed edge u → v)

## Output Format

Print `CYCLE` if a cycle exists, `NO CYCLE` otherwise.

## Example

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

Edge 3→1 creates the cycle 1→2→3→1.
