# Round Robin Scheduling: Turnaround and Waiting Time

Understanding how to compute **turnaround time** and **waiting time** under Round Robin (RR) scheduling is essential for OS interviews and exams. This lesson walks through the mechanics and introduces the two key metrics.

## Definitions

Given processes with arrival times and CPU burst times, simulated under RR with a given quantum `q`:

- **Completion time (CT):** the clock value when the process finishes all its CPU work.
- **Turnaround time (TAT):** `CT - arrival_time`. Total elapsed time from arrival to completion.
- **Waiting time (WT):** `TAT - burst_time`. Time spent in the ready queue, not executing.

## Simulation Rules

1. Maintain a FIFO ready queue. At time 0 (or whenever the CPU first becomes free), enqueue all processes whose arrival time has been reached.
2. Dispatch the process at the head for `min(remaining_burst, quantum)` time units.
3. Advance the clock by the run time.
4. After advancing the clock, enqueue any processes that arrived during the slice (arrival <= new clock), in arrival order.
5. If the dispatched process is not yet done, re-enqueue it at the tail **after** newly arrived processes.
6. If the ready queue is empty and processes still remain, jump the clock forward to the next arrival.

## Worked Example

| Process | Arrival | Burst |
|---------|---------|-------|
| P1      | 0       | 5     |
| P2      | 1       | 3     |
| P3      | 2       | 8     |
| P4      | 3       | 6     |

Quantum = 2.

```
Time  0: Queue [P1]. Run P1 for 2. Clock=2.
         Arrived by t=2: P2, P3. Enqueue P2, P3, then re-enqueue P1(rem=3).
         Queue: [P2, P3, P1(rem=3)].
Time  2: Run P2 for 2. Clock=4.
         Arrived by t=4: P4. Enqueue P4, then re-enqueue P2(rem=1).
         Queue: [P3, P1(rem=3), P4, P2(rem=1)].
Time  4: Run P3 for 2. Clock=6. Queue: [P1(rem=3), P4, P2(rem=1), P3(rem=6)].
Time  6: Run P1 for 2. Clock=8. Queue: [P4, P2(rem=1), P3(rem=6), P1(rem=1)].
Time  8: Run P4 for 2. Clock=10. Queue: [P2(rem=1), P3(rem=6), P1(rem=1), P4(rem=4)].
Time 10: Run P2 for 1 (finishes). CT(P2)=11. Queue: [P3(rem=6), P1(rem=1), P4(rem=4)].
Time 11: Run P3 for 2. Clock=13. Queue: [P1(rem=1), P4(rem=4), P3(rem=4)].
Time 13: Run P1 for 1 (finishes). CT(P1)=14. Queue: [P4(rem=4), P3(rem=4)].
Time 14: Run P4 for 2. Clock=16. Queue: [P3(rem=4), P4(rem=2)].
Time 16: Run P3 for 2. Clock=18. Queue: [P4(rem=2), P3(rem=2)].
Time 18: Run P4 for 2 (finishes). CT(P4)=20. Queue: [P3(rem=2)].
Time 20: Run P3 for 2 (finishes). CT(P3)=22.
```

Results:

| Process | CT | TAT = CT-Arrival | WT = TAT-Burst |
|---------|----|------------------|----------------|
| P1      | 14 | 14 - 0 = 14      | 14 - 5 = 9     |
| P2      | 11 | 11 - 1 = 10      | 10 - 3 = 7     |
| P3      | 22 | 22 - 2 = 20      | 20 - 8 = 12    |
| P4      | 20 | 20 - 3 = 17      | 17 - 6 = 11    |

Average turnaround time = (14 + 10 + 20 + 17) / 4 = **15.25**
Average waiting time = (9 + 7 + 12 + 11) / 4 = **9.75**

## The Critical Ordering Rule

The most common simulation bug is the ordering of new arrivals vs the preempted process. The rule is:

> At the moment the current process is preempted (clock just advanced), first enqueue **newly arrived** processes, then enqueue the preempted process.

This matches real OS behavior: the currently running process was "waiting" for this moment to be re-queued, while new arrivals entered the ready queue during the slice.

## Sensitivity to Quantum Size

```
Large quantum → approaches FCFS, higher average waiting time for later processes.
Small quantum → many context switches, overhead dominates, but better response time.
Rule of thumb: quantum should be larger than 80% of CPU burst lengths.
```

## Further Reading

- **OSTEP Chapter 7: Scheduling Introduction** (https://pages.cs.wisc.edu/~remzi/OSTEP/) — clear narrative on turnaround vs response time trade-offs.
- **MIT 6.1810 Lecture Notes** (https://ocw.mit.edu/courses/6-1810-operating-system-engineering-fall-2023/) — xv6 scheduler code and discussion of multi-level feedback queues.
