# Round-Robin Scheduler with Arrival Times

Simulate a Round-Robin CPU scheduler. Read N processes each with an **arrival time** and **burst time**, plus a time quantum Q.

Output the order in which processes **finish**, their completion time, turnaround time (TAT = completion − arrival), and waiting time (WT = TAT − burst).

**Tie-breaking rule:** Processes that arrive at the same time as a preemption should be enqueued in order of their process ID (lower ID first), before the preempted process is re-added.

If the CPU becomes idle (ready queue is empty), jump the clock forward to the next arrival.

After listing all processes in finish order, print:

```
Average TAT: X.XX
Average WT: X.XX
```

Both averages are rounded to exactly 2 decimal places.

## Input Format

```
N Q
arrival_1 burst_1
arrival_2 burst_2
...
arrival_N burst_N
```

- First line: number of processes N and quantum Q (space-separated)
- Next N lines: arrival time and burst time for P1 through PN

## Output Format

One line per process in finish order:

```
P<id> finishes at t=<ct>, TAT=<tat>, WT=<wt>
```

Followed by:

```
Average TAT: X.XX
Average WT: X.XX
```

## Sample Input

```
4 2
0 5
1 3
2 1
4 2
```

## Sample Output

```
P3 finishes at t=4, TAT=2, WT=1
P2 finishes at t=8, TAT=7, WT=4
P4 finishes at t=10, TAT=6, WT=4
P1 finishes at t=11, TAT=11, WT=6
Average TAT: 6.50
Average WT: 3.75
```

## Constraints

- 1 ≤ N ≤ 20
- 1 ≤ Q ≤ 100
- 0 ≤ arrival time ≤ 1000
- 1 ≤ burst time ≤ 200
