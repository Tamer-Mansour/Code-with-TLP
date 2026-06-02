# Prompt: Compute Turnaround and Waiting Times

## Problem Description

Given a set of processes (each with an arrival time and a CPU burst time) and a completed execution timeline (a list of non-overlapping schedule intervals), compute the turnaround time and waiting time for each process, then output the per-process results and the averages.

**Formulas:**
- completion_time = the end time of the last scheduled interval for that process
- turnaround_time = completion_time - arrival_time
- waiting_time = turnaround_time - burst_time

## Input Format

```
N
PID_1 arrival_1 burst_1
...
PID_N arrival_N burst_N
S
start_1 end_1 PID_a
...
start_S end_S PID_z
```

- Intervals are in chronological order and do not overlap.
- A process may appear in multiple intervals (preemptive scheduling).
- `1 <= N <= 10`, `1 <= S <= 30`
- All times are non-negative integers.

## Output Format

For each process in **ascending PID order**, print:
```
PID: TAT=X WT=Y
```
Then:
```
Avg Turnaround: X.XX
Avg Waiting: X.XX
```

Averages are rounded to 2 decimal places.

## Sample Input 1

```
3
1 0 4
2 0 3
3 0 2
3
0 4 1
4 7 2
7 9 3
```

## Sample Output 1

```
1: TAT=4 WT=0
2: TAT=7 WT=4
3: TAT=9 WT=7
Avg Turnaround: 6.67
Avg Waiting: 3.67
```

## Sample Input 2

```
3
1 0 4
2 0 3
3 0 2
5
0 2 1
2 4 2
4 6 3
6 8 1
8 9 2
```

## Sample Output 2

```
1: TAT=8 WT=4
2: TAT=9 WT=6
3: TAT=6 WT=4
Avg Turnaround: 7.67
Avg Waiting: 4.67
```

## Constraints

- Time limit: 3000 ms
- Memory limit: 256 MB
- Use only Python standard library
- Read from stdin, print to stdout
