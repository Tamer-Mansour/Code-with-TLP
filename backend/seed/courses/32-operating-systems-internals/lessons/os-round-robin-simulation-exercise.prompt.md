# Round Robin Scheduler Simulation

## Problem Description

Simulate a preemptive Round Robin (RR) CPU scheduler with a given time quantum.

Rules:
1. Processes are dispatched in FIFO order from a ready queue.
2. A process runs for at most `quantum` time units. If it finishes early it releases the CPU voluntarily.
3. When the quantum expires the process is preempted and added to the **tail** of the ready queue.
4. Whenever the CPU becomes free (process finishes or is preempted), admit all processes whose `arrival <= current_clock` to the tail of the ready queue **before** re-queueing any preempted process. That is, new arrivals at exactly `clock` join before the preempted process.
5. If the ready queue is empty and processes still remain, advance the clock to the next arrival time and admit those processes.

Compute for each process:
- **Completion time (CT)**: the clock value when it finishes.
- **Turnaround time (TAT)** = CT − arrival time.
- **Waiting time (WT)** = TAT − burst time.

Print averages rounded to 2 decimal places.

## Input Format

```
n quantum
arrival_1 burst_1
arrival_2 burst_2
...
arrival_n burst_n
```

- First line: two integers `n` (1 ≤ n ≤ 100) and `quantum` (1 ≤ quantum ≤ 100).
- Next `n` lines: `arrival_i` and `burst_i` (0 ≤ arrival ≤ 1000, 1 ≤ burst ≤ 100).
- Process IDs are 1-indexed in input order.
- Initially sort processes by arrival time, then by process ID for ties.

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
- 1 ≤ quantum ≤ 100
- 0 ≤ arrival ≤ 1000
- 1 ≤ burst ≤ 100

## Sample Input 1

```
3 4
0 10
0 4
0 6
```

## Sample Output 1

```
P1 CT=20 TAT=20 WT=10
P2 CT=8 TAT=8 WT=4
P3 CT=18 TAT=18 WT=12
Average WT=8.67 Average TAT=15.33
```

## Explanation of Sample 1

- t=0: Queue [P1,P2,P3]. Dispatch P1 for 4 → clock=4, P1 remaining=6.
  No new arrivals. Enqueue P1 → queue [P2,P3,P1].
- t=4: Dispatch P2 for 4 → clock=8, P2 done (CT=8).
  Queue [P3,P1].
- t=8: Dispatch P3 for 4 → clock=12, P3 remaining=2.
  Queue [P1,P3].
- t=12: Dispatch P1 for 4 → clock=16, P1 remaining=2.
  Queue [P3,P1].
- t=16: Dispatch P3 for 2 → clock=18, P3 done (CT=18).
  Queue [P1].
- t=18: Dispatch P1 for 2 → clock=20, P1 done (CT=20).

## Sample Input 2

```
1 5
0 3
```

## Sample Output 2

```
P1 CT=3 TAT=3 WT=0
Average WT=0.00 Average TAT=3.00
```

## Sample Input 3

```
3 2
0 5
2 3
4 1
```

## Sample Output 3

```
P1 CT=9 TAT=9 WT=4
P2 CT=8 TAT=6 WT=3
P3 CT=7 TAT=3 WT=2
Average WT=3.00 Average TAT=6.00
```

## Notes

- The key subtlety: at the moment a process is preempted (clock advances), first enqueue any processes that have arrived by that clock value, then enqueue the preempted process.
- All values are integers except the printed averages (2 decimal places).
