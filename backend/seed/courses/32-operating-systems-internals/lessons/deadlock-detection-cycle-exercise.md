# Exercise: Detect a Deadlock Cycle in a Wait-For Graph

In this exercise you will implement a deadlock detector that operates on a **Wait-For Graph (WFG)**. A WFG is a directed graph where an edge from process A to process B means "process A is waiting for a resource currently held by process B." A deadlock exists if and only if the WFG contains a directed cycle.

## What You Will Implement

Write a program that:
1. Reads a directed graph (the WFG) from standard input.
2. Determines whether the graph contains a cycle (deadlock).
3. If a deadlock exists, outputs `DEADLOCK` followed by the sorted list of process IDs involved in the cycle.
4. If no deadlock exists, outputs `NO DEADLOCK`.

## Key Concepts to Apply

- **DFS with coloring:** Use three colors — WHITE (unvisited), GRAY (in current recursion stack), BLACK (fully visited). A back edge to a GRAY node reveals a cycle.
- **Cycle reconstruction:** When you find the back edge, trace the path from the current node back to the gray ancestor to identify every process in the deadlock.
- **Graph representation:** An adjacency list is sufficient. Processes with no outgoing edges (not waiting for anything) are not deadlocked.

## Input Format

```
N E
u1 v1
u2 v2
...
```

Where N is the number of processes (IDs 0 to N-1), E is the number of edges, and each line `u v` represents a directed edge from process u to process v (u waits for v).

## Expected Output

If deadlock: `DEADLOCK` on the first line, then the sorted space-separated process IDs involved in the cycle.

If no deadlock: `NO DEADLOCK`

## Example

Input:
```
4 4
0 1
1 2
2 3
3 1
```

Output:
```
DEADLOCK
1 2 3
```

Processes 1, 2, and 3 form a cycle (1→2→3→1).

## Hints

- If there are multiple cycles, report the one found first by your DFS traversal, then output the IDs sorted.
- The starter code includes a `solve()` stub and stdin reading pattern — fill in the cycle detection logic.
