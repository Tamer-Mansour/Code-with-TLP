# Prompt: Simulate a Round-Robin Scheduler

## Problem Description

Simulate a preemptive Round-Robin CPU scheduler. Given N processes each with an arrival time and a CPU burst time, and a scheduling quantum Q, determine the execution schedule and compute the average turnaround time and average waiting time.

**Rules:**
- Processes that have arrived by time 0 are placed in the ready queue sorted by arrival time then by PID (ascending).
- At each scheduling event, the process at the front of the ready queue runs for `min(Q, remaining_burst)` time units.
- After a slice ends, add any newly arrived processes (arrival_time <= current_time) to the back of the ready queue sorted by arrival time then PID; then if the running process is not done, re-queue it at the back.
- If the ready queue is empty and processes still remain, advance time to the next arrival.

**Metrics:**
- Turnaround time = completion_time - arrival_time
- Waiting time = turnaround_time - burst_time
- Output averages rounded to 2 decimal places.

## Input Format

```
N Q
PID_1 arrival_1 burst_1
PID_2 arrival_2 burst_2
...
PID_N arrival_N burst_N
```

- `1 <= N <= 10`
- `1 <= Q <= 20`
- `0 <= arrival_i <= 50`
- `1 <= burst_i <= 30`
- PIDs are unique positive integers

## Output Format

```
Schedule: PID_a PID_b PID_c ...
Avg Turnaround: X.XX
Avg Waiting: X.XX
```

The Schedule line lists the PID of the process running each time slice (one PID per slice). Values separated by single spaces.

## Sample Input 1

```
3 2
1 0 4
2 0 3
3 0 2
```

## Sample Output 1

```
Schedule: 1 2 3 1 2
Avg Turnaround: 7.67
Avg Waiting: 4.67
```

## Sample Input 2

```
2 3
1 0 6
2 3 4
```

## Sample Output 2

```
Schedule: 1 2 1 2
Avg Turnaround: 8.00
Avg Waiting: 3.00
```

## Constraints

- Time limit: 3000 ms
- Memory limit: 256 MB
- Use only Python standard library (no third-party packages)
- Read from stdin, print to stdout
