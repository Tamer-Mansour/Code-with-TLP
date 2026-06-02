# Prompt: Simulate a Round-Robin Scheduler

## Problem Statement

Simulate a preemptive Round Robin CPU scheduler. For each process, output its completion time, turnaround time, and waiting time.

## Scheduling Rules

1. Processes that have arrived by the current time are placed in the ready queue, ordered by arrival time (ties broken by process ID, ascending).
2. The CPU runs the front process for `min(remaining_burst, quantum)` time units.
3. After the quantum expires, add any processes that arrived during that quantum (in arrival/PID order) to the back of the queue, then re-enqueue the preempted process if it still has remaining burst.
4. If the queue is empty and unstarted processes remain, advance the clock to the next arrival.

## Input Format

```
Line 1: n q         (n = number of processes, q = time quantum; space-separated)
Next n lines: pid arrival burst   (three integers per line, pid is 1-indexed)
```

Processes are given in order of PID (1 to n), but may have different arrival times.

## Output Format

Print one line per process, **sorted by PID ascending**:

```
pid completion_time turnaround_time waiting_time
```

All values are integers separated by single spaces.

## Constraints

- `1 <= n <= 10`
- `1 <= q <= 100`
- `0 <= arrival_time <= 1000`
- `1 <= burst_time <= 100`
- All PIDs are unique integers from 1 to n.

## Sample Input

```
3 4
1 0 10
2 0 5
3 0 8
```

## Sample Output

```
1 23 23 13
2 17 17 12
3 21 21 13
```

## Explanation

Quantum = 4. All processes arrive at t=0. Queue order initially: P1, P2, P3.

```
t=0-4:   P1 runs (remaining=6)
t=4-8:   P2 runs (remaining=1)
t=8-12:  P3 runs (remaining=4)
t=12-16: P1 runs (remaining=2)
t=16-17: P2 runs (remaining=0) → P2 done at t=17
t=17-21: P3 runs (remaining=0) → P3 done at t=21
t=21-23: P1 runs (remaining=0) → P1 done at t=23
```

Turnaround = completion - arrival; Waiting = turnaround - burst.
