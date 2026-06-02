# Reading and Drawing Scheduling Gantt Charts

A **Gantt chart** is the standard tool for visualizing CPU scheduling timelines. Every OS exam question and most interview scheduling problems expect you to draw one correctly. This lesson teaches the conventions and a step-by-step method.

## What a Gantt Chart Shows

A scheduling Gantt chart has:
- A **horizontal time axis** (left = 0, right = completion).
- **Labeled blocks** showing which process owns the CPU at each time slot.
- **Tick marks** at each transition point (arrival, preemption, completion).

```
Gantt chart for 3 processes, Round Robin (quantum = 2):
| P1 | P2 | P3 | P1 | P2 | P3 | P1 |
0    2    4    6    8   10   12   14
```

Idle CPU is shown explicitly as an `IDLE` block:

```
| P1   |  IDLE  | P2 |
0      4        7    10
```

## Step-by-Step: How to Draw a Gantt Chart

**Given information you need:**
- Process names, arrival times, CPU burst lengths.
- Scheduling algorithm and (if preemptive) the time quantum.

### Step 1 — Sort by arrival time

List all processes sorted by their arrival time. Note which processes are available at time 0.

### Step 2 — Apply the algorithm

At each decision point, apply the scheduling rule:

| Algorithm      | Rule at decision point                               |
|----------------|------------------------------------------------------|
| FCFS           | Pick the process that arrived earliest               |
| SJF            | Pick the process with the shortest remaining burst   |
| Round Robin    | Pick the next process in circular order, run for ≤ quantum |
| Priority       | Pick the process with the highest priority number    |

### Step 3 — Advance time, handle arrivals

After each block, note: (a) did the running process finish? (b) did new processes arrive? (c) did the quantum expire? Update the ready queue accordingly.

### Step 4 — Compute metrics from the chart

```
Completion time  = right edge of the process's last block
Turnaround time  = Completion - Arrival
Waiting time     = Turnaround - Burst
Response time    = left edge of the process's FIRST block - Arrival
```

## Worked Example — FCFS

| Process | Arrival | Burst |
|---------|---------|-------|
| P1      | 0       | 5     |
| P2      | 1       | 3     |
| P3      | 2       | 4     |

At t=0: only P1 is ready → run P1 for 5ms.
At t=5: P2 and P3 have both arrived → pick P2 (arrived first).
At t=8: P3 is the only one left → run P3.

```
| P1        | P2    | P3      |
0           5      8         12
```

| Process | Arrival | Burst | Completion | Turnaround | Waiting | Response |
|---------|---------|-------|------------|------------|---------|----------|
| P1      | 0       | 5     | 5          | 5          | 0       | 0        |
| P2      | 1       | 3     | 8          | 7          | 4       | 4        |
| P3      | 2       | 4     | 12         | 10         | 6       | 6        |

Average waiting = (0 + 4 + 6) / 3 = **3.33 ms**

## Worked Example — Round Robin (quantum = 2)

Same processes. Ready queue at t=0: [P1]. Arrivals at t=1: P2, t=2: P3.

```
t=0: Run P1 (q=2). P1 has 5ms left.
t=1: P2 arrives (added to queue end after P1's slot).
t=2: P1 quantum expires. P3 arrives. Ready: [P2, P3, P1(3ms left)].
     Run P2.
t=4: P2 quantum expires (P2 has 1ms left). Ready: [P3, P1, P2(1ms)].
     Run P3.
t=6: P3 quantum expires (P3 has 2ms left). Ready: [P1, P2, P3(2ms)].
     Run P1.
t=8: P1 quantum expires (P1 has 1ms left). Ready: [P2, P3, P1(1ms)].
     Run P2.
t=9: P2 finishes. Ready: [P3, P1].
     Run P3.
t=11: P3 finishes. Ready: [P1].
      Run P1.
t=12: P1 finishes.
```

```
| P1 | P2 | P3 | P1 | P2|P3 | P1|
0    2    4    6    8   9  11  12
```

## Common Pitfalls

- **Off-by-one on arrivals.** A process arriving at t=2 is NOT in the queue when deciding at t=2 if you apply the decision at the very start of t=2. Be consistent — decide at the moment of transition, include all arrivals up to and including that moment.
- **Forgetting to draw IDLE blocks.** If no process is ready at some time t, draw an IDLE block. Missing idle time shifts all subsequent tick marks left and invalidates all metrics.
- **Round Robin queue order.** When multiple processes arrive simultaneously, their order in the initial ready queue matters. Typically sorted by PID or arrival order — be explicit.
- **Reusing the same block for non-contiguous runs.** P1 may appear multiple times in different segments. Each run is a separate block.

## Interview Answer

> "A Gantt chart shows which process runs on the CPU at each time unit. To draw one: sort by arrival, apply the scheduling rule at each transition, advance time, and handle new arrivals. Then read off completion times to compute turnaround, waiting, and response times."
