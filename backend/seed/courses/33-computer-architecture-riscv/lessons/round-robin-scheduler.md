# Exercise: Simulate a Round-Robin Scheduler

In this exercise you will implement a Round-Robin (RR) CPU scheduler simulator in Python.

## What You Will Build

Given a set of processes with arrival times and CPU burst durations, and a fixed time quantum, your program will simulate the RR scheduling algorithm and print the order in which processes run, then output the average turnaround time and average waiting time.

## Key Concepts to Apply

- **Round Robin** adds each arriving process to a FIFO ready queue.
- At each scheduler step the front process runs for `min(quantum, remaining_burst)` time units.
- If the process is not finished it goes to the back of the ready queue.
- New processes that arrive during a running quantum are added to the ready queue in arrival order (ties broken by process ID).

## Input Format

```
First line: N Q          (number of processes, quantum)
Next N lines: PID arrival_time burst_time
```

## Output Format

```
Schedule: PID PID PID ...   (each slice on one run)
Avg Turnaround: X.XX
Avg Waiting: X.XX
```

See the prompt file `arch-round-robin-scheduler.prompt.md` for full constraints and sample test cases.

## Getting Started

```python
from collections import deque

def simulate_rr(processes, quantum):
    # processes: list of (pid, arrival, burst)
    # Sort by arrival, then pid
    processes = sorted(processes, key=lambda p: (p[1], p[0]))
    remaining = {p[0]: p[2] for p in processes}
    # ... your simulation here
    pass
```

Think carefully about:
1. How to handle multiple processes arriving at the same time step.
2. When to stop — the simulation ends when all processes complete.
3. How to accumulate turnaround and waiting time per process.
