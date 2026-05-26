# Round-Robin Scheduler

Simulate a **Round-Robin CPU scheduler** with a fixed time quantum. All processes arrive at time 0 and are initially placed in the ready queue in order (P1, P2, …, Pn).

When a process's remaining burst fits within the quantum, it runs for exactly its remaining time and completes. The ready queue is FIFO; processes that don't finish their quantum are re-queued at the back.

Compute the **average waiting time** using integer (floor) division.

Waiting time for process i = finish_time_i − burst_time_i (since all arrive at time 0).

## Input Format

- Line 1: two integers `n` and `q` — the number of processes and the time quantum.
- Line 2: `n` integers — the CPU burst time for processes P1, P2, …, Pn.

## Output Format

Print a single integer: the **average waiting time** (integer division).

## Constraints

- `1 <= n <= 20`
- `1 <= q <= 100`
- `1 <= burst_time <= 200`

## Examples

**Example 1**
```
Input:
3 4
24 3 3

Output:
5
```

Explanation: P2 finishes at t=7 (wait=4), P3 at t=10 (wait=7), P1 at t=30 (wait=6). Average = 17//3 = 5.

**Example 2**
```
Input:
1 5
10

Output:
0
```

Explanation: One process, no waiting.
