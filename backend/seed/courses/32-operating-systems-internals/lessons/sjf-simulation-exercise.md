# Exercise: Simulate a Non-Preemptive SJF Scheduler

In this exercise you will implement a non-preemptive Shortest-Job-First (SJF) CPU scheduler. The scheduler always picks the process with the shortest burst time from among all processes that have already arrived when the CPU becomes free. Ties are broken by process ID (arrival input order).

## What You Will Implement

- A simulation loop that advances a virtual clock.
- At each scheduling decision point, select the ready process with the minimum burst time.
- Compute per-process completion time, turnaround time, and waiting time.
- Report the averages.

## Concepts Reinforced

- Why SJF produces a lower average waiting time than FCFS.
- How arrival time restricts which processes are eligible at each scheduling decision.
- The effect of CPU idle time when all remaining processes have not yet arrived.

## Key Difference from FCFS

In FCFS you pick whoever arrived first. In SJF you pick whoever has the **shortest burst** among those **already arrived**. Processes that arrive later are not eligible even if they have a shorter burst.

## Starter Hint

```python
import sys

def solve():
    data = sys.stdin.read().split()
    idx = 0
    n = int(data[idx]); idx += 1
    processes = []
    for i in range(n):
        arrival = int(data[idx]); idx += 1
        burst   = int(data[idx]); idx += 1
        processes.append((arrival, burst, i + 1))  # (arrival, burst, pid)

    clock = 0
    completed = {}
    remaining = list(processes)

    while remaining:
        # Find all processes that have arrived by clock time
        eligible = [p for p in remaining if p[0] <= clock]
        if not eligible:
            # CPU idle: jump to next arrival
            clock = min(p[0] for p in remaining)
            continue
        # Pick shortest burst; break ties by pid
        chosen = min(eligible, key=lambda p: (p[1], p[2]))
        remaining.remove(chosen)
        arrival, burst, pid = chosen
        clock += burst
        completed[pid] = clock  # completion time

    # Compute and print metrics
    pass

solve()
```

Trace through a small example by hand before running your code to confirm the scheduling order matches your expectation.
