# FCFS Scheduler Simulation

## Problem Description

Simulate a non-preemptive First-Come First-Served (FCFS) CPU scheduler.

Given `n` processes, each with an arrival time and a CPU burst time, compute:
- The **completion time** of each process (the moment it finishes executing).
- The **turnaround time** = completion time − arrival time.
- The **waiting time** = turnaround time − burst time.
- The **average waiting time** and **average turnaround time**, rounded to 2 decimal places.

Processes are dispatched strictly in arrival order. If two processes arrive at the same time, dispatch the one with the smaller process ID (1-indexed input order) first.

If the CPU is idle when the next process arrives, the clock jumps to that process's arrival time.

## Input Format

```
n
arrival_1 burst_1
arrival_2 burst_2
...
arrival_n burst_n
```

- First line: integer `n` (1 ≤ n ≤ 100).
- Next `n` lines: two integers each — `arrival_i` and `burst_i` (0 ≤ arrival_i ≤ 1000, 1 ≤ burst_i ≤ 100).
- Processes are given in input order (P1, P2, …, Pn) and should be sorted by arrival time before simulation (stable sort to preserve ID order on ties).

## Output Format

Print `n` lines, one per process (in process ID order):
```
P<id> CT=<completion> TAT=<turnaround> WT=<waiting>
```

Then print:
```
Average WT=<avg_wt> Average TAT=<avg_tat>
```

where `<avg_wt>` and `<avg_tat>` are rounded to 2 decimal places.

## Constraints

- 1 ≤ n ≤ 100
- 0 ≤ arrival ≤ 1000
- 1 ≤ burst ≤ 100

## Sample Input 1

```
3
0 24
1 3
2 3
```

## Sample Output 1

```
P1 CT=24 TAT=24 WT=0
P2 CT=27 TAT=26 WT=23
P3 CT=30 TAT=28 WT=25
Average WT=16.00 Average TAT=26.00
```

## Sample Input 2

```
3
0 3
0 6
0 4
```

## Sample Output 2

```
P1 CT=3 TAT=3 WT=0
P2 CT=9 TAT=9 WT=3
P3 CT=13 TAT=13 WT=9
Average WT=4.00 Average TAT=8.33
```

## Notes

- Clock starts at 0.
- When the CPU becomes free, if no process has arrived yet, advance the clock to the next arrival time.
- All values printed as integers except the averages (2 decimal places).
