# Practice: Banker's Algorithm

Dijkstra's Banker's Algorithm determines whether a system is in a **safe state** — one from which all processes can eventually complete without deadlock. If safe, it produces a safe sequence; otherwise it reports unsafe.

## What You'll Practice

Given the current resource state (available resources, each process's allocation, and each process's remaining need), determine if the state is safe or not.

## The Safety Algorithm

```
Work = Available (copy)
Finish[i] = false for all i

Repeat:
  Find process i where:
    Finish[i] = false  AND  Need[i] <= Work (component-wise)
  If found:
    Work += Allocation[i]   (process i finishes, releases its resources)
    Finish[i] = true
    Add i to safe sequence
  Until no such i found

If all Finish[i] = true → SAFE (print sequence)
Else → UNSAFE
```

**Tie-breaking:** when multiple processes are eligible, always pick the lowest-numbered one first (process numbering starts at 1).

## Example

3 resource types, 3 processes. Available = [2, 1, 0].

```
         Allocation   Need
P1        [1, 0, 0]   [1, 1, 0]
P2        [0, 1, 0]   [0, 0, 1]
P3        [0, 0, 1]   [0, 1, 0]
```

Safety check:
- Work = [2, 1, 0]
- P1: need=[1,1,0] ≤ [2,1,0]? Yes → work=[3,1,0], seq=[1]
- P2: need=[0,0,1] ≤ [3,1,0]? No (need 1 of type 3, work has 0)
- P3: need=[0,1,0] ≤ [3,1,0]? Yes → work=[3,1,1], seq=[1,3]
- P2: need=[0,0,1] ≤ [3,1,1]? Yes → work=[3,2,1], seq=[1,3,2]

Output: `SAFE 1 3 2`
