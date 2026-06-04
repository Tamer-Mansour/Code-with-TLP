# Banker's Algorithm: Safety Check

## Problem Description

Implement Dijkstra's **Banker's Algorithm** to determine whether a given system state is **safe**. A state is safe if there exists at least one sequence in which every process can complete, assuming each process may request up to its declared maximum.

### Algorithm

1. Compute `Need[i][j] = Max[i][j] - Allocation[i][j]` for all processes and resource types.
2. Set `Work = Available` (a working copy of available resources).
3. Mark all processes as unfinished (`Finish[i] = false`).
4. Repeatedly find an unfinished process `i` where `Need[i] <= Work` (component-wise). If found, simulate its completion: add `Allocation[i]` back to `Work`, mark `Finish[i] = true`, and record it in the safe sequence.
5. If all processes finish, the state is **SAFE**; otherwise **UNSAFE**.

## Input Format

```
Line 1: N M              (N processes, M resource types)
Line 2: M integers       (Available resources vector)
Lines 3..N+2: M integers each  (Allocation matrix, one row per process)
Lines N+3..2N+2: M integers each  (Maximum demand matrix, one row per process)
```

Processes are numbered P0, P1, ..., P(N-1) in input order.

## Output Format

If safe:
```
SAFE
Safe sequence: P<i> P<j> ...
```

If unsafe:
```
UNSAFE
```

When multiple safe sequences exist, output the one produced by scanning processes from P0 to P(N-1) at each step (greedy first-fit in index order).

## Constraints

- `1 <= N <= 10`
- `1 <= M <= 5`
- All resource counts are non-negative integers fitting in 32-bit signed integers.
- `Allocation[i][j] <= Max[i][j]` is guaranteed.

## Sample Input 1

```
5 3
3 3 2
0 1 0
2 0 0
3 0 2
2 1 1
0 0 2
7 5 3
3 2 2
9 0 2
2 2 2
4 3 3
```

## Sample Output 1

```
SAFE
Safe sequence: P1 P3 P0 P2 P4
```

## Sample Input 2

```
3 2
0 0
1 0
0 1
0 1
2 1
1 1
2 0
```

## Sample Output 2

```
UNSAFE
```

## Sample Input 3

```
2 2
2 1
1 0
0 1
3 2
1 2
```

## Sample Output 3

```
SAFE
Safe sequence: P1 P0
```

## Notes for Implementers

- The greedy scan (try P0, P1, ... in order at each step) is sufficient for finding a safe sequence when one exists, and the first found determines the output order.
- Use `all(need[i][j] <= work[j] for j in range(m))` for the feasibility check.
- When a process is selected, add its allocation back to `work` before looking for the next candidate.
