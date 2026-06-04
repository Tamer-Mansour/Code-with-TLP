# Practice: Round-Robin Scheduler with Arrival Times

In this exercise you implement a complete Round-Robin CPU scheduler that tracks each process's **arrival time** alongside its burst time, and reports per-process turnaround time (TAT) and waiting time (WT) in addition to summary averages.

## Background

The simplified RR model assumes all processes arrive at t=0. Real schedulers must handle processes arriving at different times while the CPU is already busy. Key rules:

- At time of a preemption, any process that arrived **at or before** the current clock tick is added to the ready queue before the running process is re-queued.
- Ties at the same arrival time are broken by process ID (lower ID first).
- If the CPU is idle (no ready process) it jumps to the next arrival time.

## Input Format

```
N Q
arrival_1 burst_1
arrival_2 burst_2
...
arrival_N burst_N
```

- `N`: number of processes (1 ≤ N ≤ 20)
- `Q`: time quantum (1 ≤ Q ≤ 100)
- Processes are given in order (P1, P2, …, PN)

## Output Format

Print each process in the order it **finishes**, one per line:

```
P<id> finishes at t=<ct>, TAT=<tat>, WT=<wt>
```

Then two lines for averages (rounded to 2 decimal places):

```
Average TAT: X.XX
Average WT: X.XX
```

## Example

**Input:**
```
4 2
0 5
1 3
2 1
4 2
```

**Output:**
```
P3 finishes at t=4, TAT=2, WT=1
P2 finishes at t=8, TAT=7, WT=4
P4 finishes at t=10, TAT=6, WT=4
P1 finishes at t=11, TAT=11, WT=6
Average TAT: 6.50
Average WT: 3.75
```

## Further Reading

- OSTEP Chapter 7 — Scheduling Introduction: https://pages.cs.wisc.edu/~remzi/OSTEP/
- xv6 Book (MIT) — Scheduling chapter: https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/3def8fcd397933ebb846fb479bdcf556_MIT6_828F12_xv6-book-rev7.pdf
