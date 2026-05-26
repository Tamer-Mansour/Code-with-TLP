# Topological Sort — Lexicographically Smallest Order

Given a directed acyclic graph (DAG) with N vertices (labeled 1 to N) and M directed edges, output the **lexicographically smallest** valid topological ordering.

A valid topological ordering places vertex u before vertex v for every directed edge `(u → v)`.

## Input

- Line 1: two integers N and M (vertices and edges).
- Next M lines: each line contains two integers u and v representing a directed edge from u to v.

Constraints: `1 ≤ N ≤ 1000`, `0 ≤ M ≤ N*(N−1)/2`.

## Output

N space-separated integers: the lexicographically smallest topological ordering.

## Examples

**Input:**
```
4 3
1 3
2 3
3 4
```
**Output:** `1 2 3 4`

**Input:**
```
3 0
```
**Output:** `1 2 3`

## Hint

Use Kahn's algorithm with a min-heap (Python's `heapq`) to always pick the smallest available vertex next.
