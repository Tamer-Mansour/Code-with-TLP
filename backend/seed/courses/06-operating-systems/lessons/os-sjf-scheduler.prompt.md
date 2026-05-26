# SJF Scheduler

Simulate **non-preemptive Shortest Job First (SJF)** scheduling for a set of processes, all of which arrive at time 0. Compute the average waiting time (integer division, truncating toward zero).

## Input

```
N
b1 b2 ... bN
```

- First line: integer N (1 ≤ N ≤ 100), the number of processes.
- Second line: N space-separated positive integers, the CPU burst time of each process (1 ≤ burst ≤ 1000).

## Output

Print a single integer: the **average waiting time** (integer division, truncating toward zero).

- All processes arrive at time 0.
- Waiting time for process i = time when i starts executing (since arrival = 0).
- Sort processes by burst time ascending (shortest first) — this is SJF.
- Average = total waiting time ÷ N (integer division).

## Examples

**Example 1**
```
Input:
4
6 3 8 1

Output:
3
```
*Explanation:* Sort by burst: 1, 3, 6, 8.
Start times: 0, 1, 4, 10.
Waiting times: 0, 1, 4, 10. Total = 15. 15 ÷ 4 = 3 (integer division).

**Example 2**
```
Input:
1
10

Output:
0
```
*Explanation:* Single process starts immediately, waiting time = 0.

**Example 3**
```
Input:
3
5 5 5

Output:
5
```
*Explanation:* Equal bursts. Start times: 0, 5, 10. Waiting: 0, 5, 10. Total = 15. 15 ÷ 3 = 5.

## Constraints

- All processes arrive at time 0.
- Burst times are positive integers.
- Use integer division (floor toward zero) for the average.
- Output exactly one integer with no trailing spaces or newlines beyond the default.
