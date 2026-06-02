# Exercise: Compute Turnaround and Waiting Times

In this exercise you will compute scheduling metrics — turnaround time and waiting time — for a set of processes given their arrival times, burst times, and a completed execution schedule.

## What You Will Build

Your program reads a completed execution timeline (a list of `(start, end, PID)` intervals) along with each process's arrival time and burst time. It then computes and outputs per-process turnaround and waiting times, plus the averages.

## Key Formulas

```
completion_time  = time at which the last slice of the process ends
turnaround_time  = completion_time - arrival_time
waiting_time     = turnaround_time - burst_time
```

## Input Format

```
First line: N         (number of processes)
Next N lines: PID arrival_time burst_time
Then one line: S      (number of schedule intervals)
Next S lines: start end PID
```

Intervals are given in chronological order and do not overlap. A process may appear in multiple intervals (preemptive scheduling).

## Output Format

For each process in ascending PID order:
```
PID: TAT=X WT=Y
```
Then:
```
Avg Turnaround: X.XX
Avg Waiting: X.XX
```

See the prompt file `arch-scheduler-metrics.prompt.md` for full constraints and sample test cases.

## Getting Started

```python
def compute_metrics(processes, intervals):
    # processes: dict {pid: (arrival, burst)}
    # intervals: list of (start, end, pid)
    completion = {}
    for start, end, pid in intervals:
        completion[pid] = end   # last write wins = actual completion

    results = {}
    for pid, (arrival, burst) in processes.items():
        tat = completion[pid] - arrival
        wt  = tat - burst
        results[pid] = (tat, wt)
    return results
```

Think about:
1. If a PID appears in multiple intervals, which `end` value is the completion time?
2. How to sort PIDs for output order.
3. Rounding to 2 decimal places with Python's `:.2f` format specifier.
