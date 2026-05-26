# Banker's Algorithm: Safe State Check

Given the current state of a multi-process, multi-resource system, determine whether it is in a **safe state** using the Banker's Algorithm. If safe, output the safe sequence; if not, output `UNSAFE`.

## Input

```
N M
avail_1 avail_2 ... avail_M
alloc_11 alloc_12 ... alloc_1M
...
alloc_N1 alloc_N2 ... alloc_NM
need_11 need_12 ... need_1M
...
need_N1 need_N2 ... need_NM
```

- First line: N (number of processes, 1 ≤ N ≤ 10) and M (number of resource types, 1 ≤ M ≤ 5).
- Second line: M integers — currently available resources.
- Next N lines: the allocation matrix (what each process currently holds).
- Next N lines: the need matrix (how much more each process might request).

All values are non-negative integers ≤ 100. Processes are numbered 1 through N.

## Output

- If a safe sequence exists: `SAFE` followed by the process numbers in the safe sequence, all on one line separated by spaces.
- If no safe sequence exists: `UNSAFE`

**Tie-breaking:** when multiple processes are eligible at the same step, choose the one with the **lowest process number**.

## Examples

**Example 1** (classic Silberschatz example)
```
Input:
5 3
3 3 2
0 1 0
2 0 0
3 0 2
2 1 1
0 0 2
7 4 3
1 2 2
6 0 0
0 1 1
4 3 1

Output:
SAFE 2 4 5 1 3
```

**Example 2**
```
Input:
2 1
0
1
1
2
2

Output:
UNSAFE
```
*Explanation:* Work=0, P1 needs 2 > 0, P2 needs 2 > 0 → no process can start.

**Example 3**
```
Input:
1 2
3 2
1 1
2 1

Output:
SAFE 1
```
*Explanation:* Need=[2,1] ≤ Available=[3,2] → P1 runs → done.

## Constraints

- All matrix values are non-negative integers.
- The input is always consistent (need values are non-negative).
- Output exactly `SAFE` followed by a sequence, or exactly `UNSAFE`.
