# CPU Scheduling Algorithms

The CPU **scheduler** decides which ready process runs next. This decision has profound impact on system responsiveness, throughput, and fairness. Every OS ships with at least one scheduling algorithm; modern OSes use hybrid approaches that combine multiple policies.

## Key Metrics

| Metric | Definition | Formula |
|--------|-----------|---------|
| **Arrival time** | When the process enters the ready queue | Given |
| **Burst time** | CPU execution time needed | Given |
| **Completion time** | When the process finishes | Computed |
| **Turnaround time** | Total elapsed time from submission to completion | `completion − arrival` |
| **Waiting time** | Time spent in the ready queue (not executing) | `turnaround − burst` |
| **Response time** | Time from submission to first CPU use | Computed |
| **Throughput** | Processes completed per unit time | `count / total_time` |
| **CPU utilization** | Fraction of time the CPU is busy | `busy_time / total_time` |

## First-Come, First-Served (FCFS)

The simplest policy: processes are served in the order they arrive. **Non-preemptive** — once a process starts, it runs to completion.

**Example:** Three processes all arrive at t=0.

```
Process  Arrival  Burst
P1         0       24
P2         0        3
P3         0        3

Gantt chart (FCFS, ties broken by submission order P1→P2→P3):
|←── P1 (0–24) ──────────────→|← P2 →|← P3 →|
0                              24     27     30

Completion: P1=24, P2=27, P3=30
Turnaround: P1=24, P2=27, P3=30  → Average = 27ms
Waiting:    P1=0,  P2=24, P3=27  → Average = 17ms
```

Now reverse order (P2, P3, P1):

```
Gantt: | P2 (0–3) | P3 (3–6) |←── P1 (6–30) ──────────────→|
0       3          6                                          30

Waiting: P2=0, P3=3, P1=6  → Average = 3ms
```

**The Convoy Effect:** short processes stuck behind a long one cause high average waiting time. FCFS is fair (in arrival order) but not efficient.

## Shortest Job First (SJF)

Schedule the process with the shortest next CPU burst. **Provably optimal** for minimizing average waiting time when all processes arrive simultaneously — but requires knowing burst length in advance.

**Non-preemptive SJF example** (same 3 processes, all at t=0):

```
Sort by burst: P2(3), P3(3), P1(24)

Gantt: | P2 (0–3) | P3 (3–6) |←── P1 (6–30) ──────────────→|

Waiting: P2=0, P3=3, P1=6  → Average = 3ms  ✓ (optimal)
```

**Preemptive SJF (SRTF — Shortest Remaining Time First):** A new arrival with shorter remaining burst preempts the running process.

```
Process  Arrival  Burst
P1         0        7
P2         2        4
P3         4        1
P4         5        4

Timeline (SRTF):
t=0: P1 arrives, starts   (remaining: P1=7)
t=2: P2 arrives           (remaining: P1=5, P2=4) → P2 preempts P1
t=4: P3 arrives           (remaining: P1=5, P2=2, P3=1) → P3 preempts P2
t=5: P3 done; P4 arrives  (remaining: P1=5, P2=2, P4=4) → P2 resumes (shortest)
t=7: P2 done              (remaining: P1=5, P4=4) → P4 starts
t=11: P4 done             (remaining: P1=5) → P1 resumes
t=16: P1 done

Gantt: |P1(0-2)|P2(2-4)|P3(4-5)|P2(5-7)|P4(7-11)|P1(11-16)|

Completion: P1=16, P2=7, P3=5, P4=11
Turnaround: P1=16, P2=5, P3=1, P4=6   → Average = 7ms
Waiting:    P1=9,  P2=1, P3=0, P4=2   → Average = 3ms
```

**Problem:** burst prediction. In practice, the OS estimates future bursts using an **exponential average** (aging formula):

```
τ(n+1) = α × t(n) + (1 − α) × τ(n)
```

where `t(n)` is the actual last burst, `τ(n)` is the previous estimate, and `α` (typically 0.5) controls how quickly old history decays.

## Round-Robin (RR)

Each process gets a fixed **time quantum** (time slice). After the quantum expires, the process goes to the back of the ready queue. **Preemptive** and **fair** — no process waits more than `(n−1) × quantum` before its next turn.

**Example:** Quantum = 4ms, three processes at t=0.

```
Process  Burst
P1        24
P2         3
P3         3

Queue initially: [P1, P2, P3]

t= 0: P1 runs 4ms → remaining=20; queue: [P2, P3, P1]
t= 4: P2 runs 3ms → P2 DONE (burst ≤ quantum); queue: [P3, P1]
t= 7: P3 runs 3ms → P3 DONE; queue: [P1]
t=10: P1 runs 4ms → remaining=16; queue: [P1]
...P1 gets the CPU alone now, finishes in 6 more rounds...
t=10,14,18,22,26,30: P1 runs its remaining 20ms in chunks of 4ms

Gantt: |P1(0-4)|P2(4-7)|P3(7-10)|P1(10-14)|P1(14-18)|P1(18-22)|P1(22-26)|P1(26-30)|

Completion: P1=30, P2=7, P3=10
Turnaround: P1=30, P2=7, P3=10   → Average = 15.67ms
Waiting:    P1=6,  P2=4, P3=7    → Average = 5.67ms
```

**Quantum size matters critically:**

| Quantum | Effect |
|---------|--------|
| Very small (1ms) | Excellent response time; excessive context-switch overhead |
| Very large (→∞) | Degenerates to FCFS; poor response time for short jobs |
| Typical (10–100ms) | Balance between responsiveness and efficiency |

Rule of thumb: ~80% of CPU bursts should be shorter than the quantum (OSTEP).

## Priority Scheduling

Each process has a priority number. The CPU goes to the highest-priority ready process. Can be preemptive (new arrival with higher priority preempts) or non-preemptive.

**Example (preemptive, lower number = higher priority):**

```
Process  Arrival  Burst  Priority
P1         0        10      3
P2         1         1      1   ← highest priority
P3         2         2      4
P4         3         1      5
P5         4         5      2

t= 0: P1 starts
t= 1: P2 arrives (priority 1) → preempts P1
t= 2: P2 done; P3 arrives (priority 4); P5 not here yet → P1 resumes (best available)
      Actually: at t=2, ready: P1(pri 3), P3(pri 4); P1 runs
t= 4: P5 arrives (priority 2) → preempts P1
t= 9: P5 done; ready: P1 (remaining=8), P3(2), P4(1) → P1 runs (priority 3)
...

Average waiting computed from completion times.
```

**Starvation:** low-priority processes may never run if high-priority processes keep arriving.

**Aging solution (Linux niceness):** Every N milliseconds in the ready queue, the OS increases a process's effective priority by 1. Eventually even the lowest-priority process becomes the highest priority.

## Multilevel Feedback Queue (MLFQ)

Real OSes use MLFQ (or variants) to get the best of all algorithms without knowing burst lengths in advance:

```
Queue Q1 (highest priority, quantum=8ms)
Queue Q2 (medium priority, quantum=16ms)
Queue Q3 (lowest priority, FCFS)

Rules:
1. New processes enter Q1.
2. If a process uses its full quantum in Qi, demote to Q(i+1).
3. If a process voluntarily yields (I/O), keep it in Qi or promote.
4. Periodically, boost all processes back to Q1 (anti-starvation).
```

Short/interactive jobs stay in Q1 (good response time). Long CPU-bound jobs sink to Q3 (good throughput, low overhead).

## Linux: Completely Fair Scheduler (CFS)

Linux's default scheduler (since 2.6.23) does not use fixed time slices. Instead, it tracks each process's **virtual runtime** (`vruntime`) — how much CPU time it has consumed, weighted by priority (nice value):

```python
# Simplified CFS logic
# vruntime increases faster for low-priority (high nice) tasks
vruntime += actual_runtime × (NICE_0_LOAD / task.weight)

# Always run the task with the lowest vruntime
next_task = min(runqueue, key=lambda t: t.vruntime)
```

CFS stores runnable tasks in a **red-black tree** keyed by vruntime — O(log n) scheduling. The leftmost node is always the next task. On a 16-core machine with 1000 threads, each scheduling decision costs about 10 µs.

## Windows: Priority-Based Preemptive Scheduler

Windows uses 32 priority levels (0–31). Real-time threads use levels 16–31; normal user threads use 1–15. Level 0 is the zero-page thread. The scheduler is preemptive with dynamic priority boosts: a thread completing I/O receives a temporary boost so interactive applications feel responsive.

## Key Takeaways

- **FCFS** is simple but suffers from the convoy effect; average waiting time varies wildly by arrival order.
- **SJF/SRTF** minimizes average waiting time but requires burst prediction (exponential averaging in practice).
- **Round-Robin** provides fairness and good response time; quantum size is critical — 10–100ms is typical.
- **Priority scheduling** needs **aging** to prevent low-priority starvation.
- **MLFQ** adapts to workload mix without requiring burst lengths in advance.
- **Linux CFS** tracks virtual runtime in a red-black tree; **Windows** uses 32 priority levels with I/O boosts.
