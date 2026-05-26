# Deadlock Detector

You are given a **wait-for graph** representing which processes are waiting for resources held by other processes. Detect whether the system is in a **deadlock** state.

A deadlock exists if and only if there is a **cycle** in the wait-for graph.

An edge `u v` means "process u is waiting for process v to release a resource."

## Input Format

- Line 1: two integers `n` and `m` — the number of processes (numbered 1 to n) and the number of wait-for edges.
- Lines 2 to m+1: two integers `u v` per line, meaning process `u` is waiting for process `v`.

There are no self-loops and no duplicate edges.

## Output Format

Print `YES` if the system is deadlocked (there is a cycle), or `NO` otherwise.

## Constraints

- `1 <= n <= 100`
- `0 <= m <= n*(n-1)`

## Examples

**Example 1 — Deadlock**
```
Input:
3 3
1 2
2 3
3 1

Output:
YES
```

Explanation: 1 waits for 2, 2 waits for 3, 3 waits for 1 — a cycle.

**Example 2 — No Deadlock**
```
Input:
3 2
1 2
2 3

Output:
NO
```

Explanation: A linear chain — no cycle.
