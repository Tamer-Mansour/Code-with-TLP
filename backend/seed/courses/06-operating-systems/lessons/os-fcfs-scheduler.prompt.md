# FCFS Scheduler

Simulate a **First-Come, First-Served (FCFS)** CPU scheduler and compute the **average waiting time** (integer division, truncated).

Processes that arrive at the same time are scheduled in the order given (lowest index first). If the CPU is idle when the next process arrives, it starts immediately.

**Waiting time** for a process = time it starts executing − its arrival time.

## Input Format

- Line 1: a single integer `n` — the number of processes.
- Lines 2 to n+1: two integers per line: `arrival_time burst_time` for process `i` (1-indexed).

## Output Format

Print a single integer: the **average waiting time** using integer (floor) division.

## Constraints

- `1 <= n <= 100`
- `0 <= arrival_time <= 1000`
- `1 <= burst_time <= 100`

## Examples

**Example 1**
```
Input:
3
0 24
0 3
0 3

Output:
17
```

Explanation: P1 waits 0 ms, P2 waits 24 ms, P3 waits 27 ms. Average = (0+24+27)/3 = 17.

**Example 2**
```
Input:
3
0 5
2 3
4 1

Output:
2
```

Explanation: P1 starts at 0 (wait=0), P2 starts at 5 (wait=3), P3 starts at 8 (wait=4). Average = 7/3 = 2.
