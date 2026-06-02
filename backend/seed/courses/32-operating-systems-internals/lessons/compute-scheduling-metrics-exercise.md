# Exercise: Compute Average Waiting and Turnaround Time

In this exercise you will implement a **FCFS (First-Come, First-Served)** CPU scheduler simulator. Given a list of processes with their arrival times and CPU burst lengths, your program will compute the average waiting time and average turnaround time and output them rounded to two decimal places.

## What You Will Implement

- Read N processes from standard input, each with an arrival time and a burst time.
- Simulate the FCFS scheduling algorithm (processes are served in order of arrival; ties broken by process index).
- Compute for each process:
  - **Completion time** — when does it finish?
  - **Turnaround time** = completion time - arrival time
  - **Waiting time** = turnaround time - burst time
- Output the **average turnaround time** and **average waiting time**, each on its own line, rounded to 2 decimal places.

## Key Concepts Practiced

- Building a Gantt chart programmatically.
- Handling idle CPU time (when the next process arrives after the CPU is free).
- Computing the four scheduling metrics from first principles.

## Starter Code

```python
import sys

def solve():
    data = sys.stdin.read().split()
    # TODO: parse input, simulate FCFS, print results
    pass

solve()
```

## Example

**Input:**
```
3
0 6
1 4
5 2
```

**Output:**
```
8.33
4.33
```

Trace through the schedule yourself before running your code — that is the best way to build intuition for scheduling metrics.
