# Practice: Deadlock Detection

A **deadlock** in a wait-for graph corresponds to a cycle in the directed graph. This exercise has you implement a cycle detector for such graphs.

## Review: Cycle Detection with DFS

```
Algorithm (DFS with recursion stack):
  For each unvisited node:
    Mark as visited AND in recursion stack
    For each neighbor:
      If not visited: recurse; if recursion returns True → cycle found
      If in recursion stack: cycle found
    Remove from recursion stack
  Return False if no cycle found
```

## Why the Recursion Stack Matters

A regular visited set is not enough for cycle detection in directed graphs:

```
  1 → 2 → 3
  4 → 2      ← 4 visits an already-visited node (2), but this is NOT a cycle
```

Only when you re-encounter a node that is currently in your DFS call stack is it a back edge (cycle).

## Worked Example

```
n=4, edges: 1→2, 2→3, 3→4, 4→2

DFS from 1: stack=[1]
  Visit 2: stack=[1,2]
    Visit 3: stack=[1,2,3]
      Visit 4: stack=[1,2,3,4]
        Visit 2: 2 is in stack! → CYCLE found → output YES
```

Now implement the deadlock detector.
