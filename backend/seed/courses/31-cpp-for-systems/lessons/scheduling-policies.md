# CPU Scheduling: FCFS, Round Robin, Priority

The OS scheduler decides which ready process gets the CPU next. Knowing the major algorithms, their trade-offs, and how to compute metrics like turnaround time and waiting time is essential for OS interviews.

## Key Scheduling Metrics

| Metric | Definition |
|---|---|
| **Arrival time** | When the process enters the ready queue |
| **Burst time** | CPU time the process needs to finish |
| **Completion time** | When the process finishes |
| **Turnaround time** | Completion time − Arrival time |
| **Waiting time** | Turnaround time − Burst time |
| **Response time** | Time from arrival until first CPU access |

## First-Come, First-Served (FCFS)

The simplest policy: processes are served in arrival order. Non-preemptive — a running process holds the CPU until it finishes or blocks.

**Example:** Three processes arrive at t=0 with burst times 10, 5, 8.

```
Gantt: | P1 (0-10) | P2 (10-15) | P3 (15-23) |
Turnaround: P1=10, P2=15, P3=23   Average = 16
Waiting:    P1=0,  P2=10, P3=15   Average = 8.33
```

**Problem:** The **convoy effect** — a long job blocks many short jobs behind it.

> **Interview answer:** FCFS is simple but suffers from the convoy effect; average waiting time is high when long jobs arrive first.

## Round Robin (RR)

Each process gets a fixed **time quantum** (e.g., 4 ms). When the quantum expires, the process is preempted and moves to the back of the ready queue.

**Example:** P1 burst=10, P2 burst=5, P3 burst=8, quantum=4, all arrive at t=0.

```
Gantt: | P1(0-4) | P2(4-8) | P3(8-12) | P1(12-16) | P2(16-17) | P3(17-21) | P1(21-23) |
Completion: P1=23, P2=17, P3=21
Turnaround: P1=23, P2=17, P3=21   Average = 20.33
Waiting:    P1=13, P2=12, P3=13   Average = 12.67
```

**Trade-offs:**

- Good **response time** and **fairness** — every process makes progress.
- Higher **context-switch overhead** and worse turnaround than FCFS for CPU-bound loads.
- A very large quantum degrades to FCFS; a very small quantum wastes CPU on context switches.

> **Interview answer:** Round robin gives fairness and good response time but increases context-switch overhead; the quantum size critically controls the trade-off.

## Shortest Job First (SJF) / Shortest Remaining Time (SRTF)

SJF picks the process with the smallest burst time. Non-preemptive (SJF) or preemptive (SRTF / SRTN).

- Provably **optimal for average waiting time** when burst times are known.
- **Practical problem:** burst time is unknown in advance; OS must estimate using exponential averaging.

```
Estimated burst = α × actual_last + (1 − α) × previous_estimate
```

## Priority Scheduling

Each process has a priority number. The highest-priority ready process runs next. Can be preemptive or non-preemptive.

**Starvation problem:** low-priority processes may never run if high-priority ones keep arriving.

**Solution — Aging:** gradually increase the priority of waiting processes over time.

```
priority(t) = initial_priority + (wait_time / aging_factor)
```

## Multilevel Feedback Queue (MLFQ)

The most practical real-world scheduler. Multiple queues with decreasing priority and increasing quantum:

1. New processes enter the **top queue** (small quantum, high priority).
2. If a process uses its full quantum, it drops to the **next lower queue**.
3. If it voluntarily yields (I/O), it stays or rises — rewarding interactive behavior.

MLFQ approximates SJF without knowing burst times: short jobs finish quickly in the top queue; long CPU-bound jobs sink to lower queues.

## Summary Comparison

| Policy | Preemptive | Optimal For | Weakness |
|---|---|---|---|
| FCFS | No | Simplicity | Convoy effect |
| Round Robin | Yes | Fairness, response time | High context-switch cost |
| SJF | No | Avg waiting time | Needs burst-time knowledge |
| SRTF | Yes | Avg waiting time | Starvation of long jobs |
| Priority | Both | Differentiated service | Starvation without aging |
| MLFQ | Yes | General-purpose | Complex to tune |

## C++ Simulation Skeleton (FCFS)

```cpp
#include <vector>
#include <algorithm>
#include <cstdio>

struct Process { int id, arrival, burst; };

void fcfs(std::vector<Process> procs) {
    std::sort(procs.begin(), procs.end(),
              [](auto& a, auto& b){ return a.arrival < b.arrival; });
    int time = 0;
    for (auto& p : procs) {
        time = std::max(time, p.arrival);
        int start = time;
        time += p.burst;
        printf("P%d: start=%d finish=%d turnaround=%d\n",
               p.id, start, time, time - p.arrival);
    }
}
```
