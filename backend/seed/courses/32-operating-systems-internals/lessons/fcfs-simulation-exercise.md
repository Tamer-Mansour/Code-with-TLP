# Exercise: Simulate an FCFS Scheduler

In this exercise you will implement a First-Come First-Served (FCFS) CPU scheduler simulator. Your program reads a list of processes — each with an arrival time and a CPU burst time — and computes the waiting time, turnaround time, and completion time for every process, then prints the average waiting and average turnaround times.

## What You Will Implement

- A simple FIFO ready queue that admits processes in arrival order.
- Simulation logic that advances a virtual clock, dispatching the next process as the CPU becomes free.
- Calculation of per-process metrics and their averages.

## Concepts Reinforced

- FCFS dispatching order and the effect of arrival time.
- The relationship: **turnaround = completion − arrival** and **waiting = turnaround − burst**.
- How idle CPU time arises when the next process has not yet arrived.

## Input / Output

Read from standard input and print to standard output. See the prompt file for exact format details, constraints, and sample cases.

## Starter Hint

```python
import sys

def solve():
    data = sys.stdin.read().split()
    # Parse n, then n pairs of (arrival, burst)
    # Sort processes by arrival time
    # Simulate FCFS: advance clock, dispatch, compute metrics
    pass

solve()
```

Work through the small examples by hand first — trace the clock value step by step — before writing code.
