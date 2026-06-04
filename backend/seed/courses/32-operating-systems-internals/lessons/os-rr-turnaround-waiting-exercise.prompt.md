# Round Robin Scheduling: Average Turnaround and Waiting Time

## Problem Description

Given a set of processes with arrival times and CPU burst times, simulate **Round Robin (RR)** scheduling with a given time quantum. Compute and print the **average turnaround time** and **average waiting time**, each rounded to 2 decimal places.

### Definitions

- **Turnaround time** for process i = completion\_time\_i - arrival\_time\_i
- **Waiting time** for process i = turnaround\_time\_i - burst\_time\_i

### Simulation Rules

1. Sort processes by arrival time (ties broken by input order — earlier index first).
2. Maintain a FIFO ready queue. Enqueue all processes with `arrival <= current_clock` at the start and after each scheduling event.
3. Dispatch the process at the head for `min(remaining_burst, quantum)` time units. Advance the clock.
4. After advancing the clock, enqueue newly arrived processes (arrival <= new clock, in arrival/input order) **before** re-enqueuing the preempted process.
5. If a process finishes, record its completion time.
6. If the ready queue is empty and processes remain unfinished, advance the clock to the next arrival time.

## Input Format

```
Line 1: N Q           (N processes, time quantum Q)
Lines 2..N+1: process_id arrival_time burst_time
```

- `process_id` is a string (e.g., `P1`, `P2`, ...).
- `arrival_time` and `burst_time` are non-negative integers.

## Output Format

```
Average Turnaround Time: <value>
Average Waiting Time: <value>
```

Each value printed to exactly **2 decimal places**.

## Constraints

- `1 <= N <= 20`
- `1 <= Q <= 50`
- `0 <= arrival_time <= 500`
- `1 <= burst_time <= 100`

## Sample Input 1

```
4 2
P1 0 5
P2 1 3
P3 2 8
P4 3 6
```

## Sample Output 1

```
Average Turnaround Time: 15.25
Average Waiting Time: 9.75
```

## Sample Input 2

```
3 4
P1 0 10
P2 0 4
P3 0 6
```

## Sample Output 2

```
Average Turnaround Time: 15.33
Average Waiting Time: 8.67
```

## Sample Input 3

```
1 5
P1 0 3
```

## Sample Output 3

```
Average Turnaround Time: 3.00
Average Waiting Time: 0.00
```

## Notes for Implementers

- The key subtlety: when the clock advances by a slice, enqueue processes that arrived at or before the new clock value **before** re-enqueuing the preempted process.
- Use `collections.deque` for the ready queue.
- Collect completion times in a dict keyed by process id, then compute TAT and WT per process.
