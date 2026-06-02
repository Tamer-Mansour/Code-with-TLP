# Exercise: Simulate a Round Robin Scheduler With a Given Quantum

In this exercise you will build a Round Robin (RR) CPU scheduler simulator. Given a set of processes and a time quantum, your program tracks the circular ready queue, dispatches each process for at most one quantum, and computes the standard scheduling metrics.

## What You Will Implement

- A circular FIFO queue (can be modeled with a Python `collections.deque`).
- A simulation loop that:
  1. Adds newly arrived processes to the tail of the queue.
  2. Dispatches the process at the head for `min(remaining_burst, quantum)` time units.
  3. Advances the clock and re-queues or completes the process.
- Per-process completion time, turnaround time, and waiting time.
- Averages of waiting and turnaround times.

## Concepts Reinforced

- The circular nature of the RR ready queue.
- How newly arriving processes enter at the tail after the current process is re-queued.
- Why response time is bounded but average waiting time may be worse than SJF.
- The role of the quantum in determining how often a context switch occurs.

## Ordering Rule for Arrivals

At each scheduling decision point (when the CPU becomes free), admit all processes whose arrival time ≤ current clock into the queue before picking the next process. When a preempted process returns to the queue and new arrivals happen at the same instant, enqueue new arrivals **before** the preempted process (they joined while it was running).

## Starter Hint

```python
import sys
from collections import deque

def solve():
    data = sys.stdin.read().split()
    idx = 0
    n       = int(data[idx]); idx += 1
    quantum = int(data[idx]); idx += 1
    processes = []
    for i in range(n):
        arrival = int(data[idx]); idx += 1
        burst   = int(data[idx]); idx += 1
        processes.append([i + 1, arrival, burst, burst])  # pid, arrival, burst, remaining

    processes.sort(key=lambda p: (p[1], p[0]))  # sort by arrival, then pid
    clock = 0
    queue = deque()
    # ... simulation loop ...

solve()
```

Trace the sample case step by step before coding: draw a Gantt chart on paper, then verify your code matches it.
