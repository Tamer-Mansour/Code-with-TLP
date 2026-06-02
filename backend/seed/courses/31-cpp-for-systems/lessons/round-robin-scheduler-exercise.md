# Exercise: Simulate a Round-Robin Scheduler

In this exercise you will implement a complete Round Robin CPU scheduler simulation — the kind of problem that appears in OS courses and systems interviews.

## What You Will Implement

Given a set of processes (each with an arrival time and a CPU burst time) and a fixed time quantum, simulate Round Robin scheduling and compute the **completion time**, **turnaround time**, and **waiting time** for each process.

## Scheduling Rules

1. Processes that arrive at or before the current time are placed in the ready queue in order of arrival (ties broken by process ID).
2. The CPU serves the front of the ready queue. It runs the process for `min(remaining_burst, quantum)` time units.
3. After each quantum, newly arrived processes (arrived during that quantum) are added to the back of the queue before re-queuing the preempted process.
4. If the ready queue is empty and processes are still pending, the CPU is idle until the next arrival.

## Metrics to Compute

```
turnaround_time = completion_time - arrival_time
waiting_time    = turnaround_time - burst_time
```

## Input / Output Format

See the prompt file for the exact specification and a worked example.

## Learning Goals

After completing this exercise you will be able to:

- Implement Round Robin scheduling using a queue and a simulation clock.
- Correctly handle varying arrival times and idle CPU gaps.
- Compute turnaround and waiting time from first principles.
- Explain Round Robin's trade-offs in an interview with concrete numbers.
