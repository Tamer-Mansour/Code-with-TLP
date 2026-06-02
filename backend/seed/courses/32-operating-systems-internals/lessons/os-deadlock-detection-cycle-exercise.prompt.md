# Deadlock Cycle Detector — Exercise Prompt

## Problem Statement

You are given a **Wait-For Graph (WFG)** of N processes. A directed edge from process u to process v means "process u is waiting for a resource currently held by process v." A deadlock exists if and only if the WFG contains a **directed cycle**.

Write a program that determines whether the system is deadlocked. If it is, identify the processes involved in the cycle.

## Input Format

```
N E
u1 v1
u2 v2
...
uE vE
```

- Line 1: Two integers N (number of processes, IDs 0 to N-1) and E (number of directed edges).
- Next E lines: each contains two integers u and v representing a directed edge (u waits for v).
- 1 ≤ N ≤ 1000, 0 ≤ E ≤ 5000
- All process IDs are in range [0, N-1].
- A self-loop (u == v) is a valid edge and represents a trivial deadlock (process waiting for itself).

## Output Format

If a deadlock cycle is detected:
```
DEADLOCK
<space-separated sorted process IDs in the cycle>
```

If no deadlock exists:
```
NO DEADLOCK
```

- The process IDs in the deadlock line must be **sorted in ascending order**.
- If multiple cycles exist, output the one discovered first by a DFS traversal that visits processes in order from ID 0 to N-1.
- Output is compared after trimming trailing whitespace/newline.

## Sample Input 1

```
4 4
0 1
1 2
2 3
3 1
```

## Sample Output 1

```
DEADLOCK
1 2 3
```

**Explanation:** Processes 1, 2, and 3 form the cycle 1→2→3→1. Process 0 is not in the cycle (it waits for 1, but 0 is not waited on by anyone in the cycle).

## Sample Input 2

```
3 2
0 1
1 2
```

## Sample Output 2

```
NO DEADLOCK
```

**Explanation:** The graph is a simple chain 0→1→2 with no cycle.

## Constraints

- Use standard DFS with three-color marking (WHITE/GRAY/BLACK).
- A GRAY node encountered during DFS indicates a back edge — the root of the cycle.
- Reconstruct the cycle by following parent pointers from the current node back to the gray ancestor.
- Report all nodes in the reconstructed cycle (the gray ancestor and every node on the path back to it).

## Hints

- A self-loop (u == v) means process u holds a resource it is also waiting for — detect this as a cycle containing only u.
- Use a parent array to reconstruct the cycle path when a back edge is found.
- Sort the final list of deadlocked process IDs before printing.
