# Non-Preemptive SJF Scheduler Simulation

## Problem Description

Simulate a non-preemptive Shortest-Job-First (SJF) CPU scheduler.

When the CPU becomes free, select the process with the **shortest burst time** from among all processes that have arrived at or before the current clock time. If two eligible processes have equal burst times, dispatch the one with the smaller process ID (1-indexed input order). If no process has arrived yet, advance the clock to the earliest arrival time.

Compute for each process:
- **Completion time (CT)**: when the process finishes.
- **Turnaround time (TAT)** = CT − arrival time.
- **Waiting time (WT)** = TAT − burst time.

Then print the average WT and average TAT rounded to 2 decimal places.

## Input Format

```
n
arrival_1 burst_1
arrival_2 burst_2
...
arrival_n burst_n
```

- First line: integer `n` (1 ≤ n ≤ 100).
- Next `n` lines: `arrival_i` and `burst_i` (0 ≤ arrival ≤ 1000, 1 ≤ burst ≤ 100).
- Process IDs are 1-indexed in input order.

## Output Format

Print `n` lines in process ID (input) order:
```
P<id> CT=<completion> TAT=<turnaround> WT=<waiting>
```

Then:
```
Average WT=<avg_wt> Average TAT=<avg_tat>
```

with averages rounded to 2 decimal places.

## Constraints

- 1 ≤ n ≤ 100
- 0 ≤ arrival ≤ 1000
- 1 ≤ burst ≤ 100

## Sample Input 1

```
4
0 8
1 4
2 9
3 5
```

## Sample Output 1

```
P1 CT=8 TAT=8 WT=0
P2 CT=12 TAT=11 WT=7
P3 CT=26 TAT=24 WT=15
P4 CT=17 TAT=14 WT=9
Average WT=7.75 Average TAT=14.25
```

## Explanation of Sample 1

- t=0: Only P1 ready → run P1 (burst 8), finishes at t=8.
- t=8: P2(burst 4), P3(burst 9), P4(burst 5) all arrived. Shortest = P2 (burst 4) → finishes at t=12.
- t=12: P3(burst 9), P4(burst 5) ready. Shortest = P4 (burst 5) → finishes at t=17.
- t=17: Only P3 left → runs to t=26.

## Sample Input 2

```
1
5 10
```

## Sample Output 2

```
P1 CT=15 TAT=10 WT=0
Average WT=0.00 Average TAT=10.00
```

## Sample Input 3

```
3
0 5
0 5
0 5
```

## Sample Output 3

```
P1 CT=5 TAT=5 WT=0
P2 CT=10 TAT=10 WT=5
P3 CT=15 TAT=15 WT=10
Average WT=5.00 Average TAT=10.00
```

## Notes

- Non-preemptive: once a process starts, it runs to completion.
- Break burst-time ties by process ID (lower ID first).
- CPU may be idle if all remaining processes have not yet arrived.
