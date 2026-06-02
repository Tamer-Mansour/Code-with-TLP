# OS: Compute Average Waiting and Turnaround Time (FCFS)

Simulate a **First-Come, First-Served (FCFS)** CPU scheduler. Given N processes with arrival times and CPU burst lengths, compute the average turnaround time and average waiting time.

## Definitions

- **Turnaround Time** for process i = Completion\_i - Arrival\_i
- **Waiting Time** for process i = Turnaround\_i - Burst\_i
- If the CPU is idle when the next process arrives (i.e., all previous processes finished before the next one arrives), advance the clock to the process's arrival time.
- Ties in arrival time are broken by the order the process appears in the input (earlier index = higher priority).

## Input Format

```
N
arrival_1 burst_1
arrival_2 burst_2
...
arrival_N burst_N
```

- First line: integer N (1 ≤ N ≤ 100) — number of processes.
- Next N lines: two integers each — arrival time and CPU burst length (0 ≤ arrival ≤ 1000, 1 ≤ burst ≤ 1000).
- Processes are given in input order; FCFS serves them sorted by arrival time, with ties broken by input order.

## Output Format

Two lines:
```
<average_turnaround>
<average_waiting>
```

Each value printed to exactly **2 decimal places**.

## Constraints

- 1 ≤ N ≤ 100
- 0 ≤ arrival\_i ≤ 1000
- 1 ≤ burst\_i ≤ 1000
- All values are non-negative integers.
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input 1

```
3
0 6
1 4
5 2
```

## Sample Output 1

```
7.33
3.33
```

**Trace:**
- P1 arrives at 0, runs 0→6. Turnaround=6, Waiting=0.
- P2 arrives at 1 (was waiting), runs 6→10. Turnaround=9, Waiting=5.
- P3 arrives at 5 (was waiting), runs 10→12. Turnaround=7, Waiting=5.
- Avg Turnaround = (6+9+7)/3 = 22/3 ≈ 7.33
- Avg Waiting = (0+5+5)/3 = 10/3 ≈ 3.33

## Sample Input 2

```
1
0 10
```

## Sample Output 2

```
10.00
0.00
```

## Sample Input 3

```
3
0 3
0 5
0 2
```

## Sample Output 3

```
7.00
3.67
```

All three processes arrive at time 0; served in input order.
