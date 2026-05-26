# Practice: SJF Scheduling Metrics

Shortest Job First (SJF) scheduling always runs the ready process with the smallest burst time next (non-preemptive). When all processes arrive at time 0, SJF minimizes the average waiting time.

## What You'll Practice

Given a list of processes with arrival times and burst times (all arriving at time 0 in this version), compute SJF scheduling metrics.

## Key Formulas

- **Completion time**: the clock time when the process finishes
- **Turnaround time** = completion time − arrival time
- **Waiting time** = turnaround time − burst time
- **Average waiting time** = sum of waiting times ÷ number of processes (integer division, truncating toward zero)

## Example Walkthrough

Input: 4 processes all at t=0 with bursts `[6, 3, 8, 1]`

Sort by burst ascending: P4(1), P2(3), P1(6), P3(8)

```
Gantt:
| P4 (0–1) | P2 (1–4) | P1 (4–10) | P3 (10–18) |

Completion: P4=1, P2=4, P1=10, P3=18
Waiting:    P4=0, P2=1, P1=4,  P3=10
Average waiting = (0+1+4+10) / 4 = 15 / 4 = 3  (integer division → 3)
```

Output: `3`

Now open the coding exercise to implement this!
