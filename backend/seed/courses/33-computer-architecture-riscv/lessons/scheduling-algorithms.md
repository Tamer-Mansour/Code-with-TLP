# CPU Scheduling Algorithms Overview

The scheduler decides which process runs next. On any uniprocessor (or per-core on a multiprocessor), only one thread executes at a time. The scheduling algorithm determines how fairly CPU time is divided and how quickly jobs complete.

## Key Metrics

Before surveying algorithms, define the terms every interviewer uses:

| Metric | Definition |
|--------|-----------|
| **Arrival time** | When the process enters the ready queue |
| **Burst time** | CPU time the process needs to finish |
| **Completion time** | When the process finishes |
| **Turnaround time** | Completion − Arrival |
| **Waiting time** | Turnaround − Burst |
| **Response time** | Time from arrival to first scheduled run |

## First Come First Served (FCFS)

Processes run in arrival order. Non-preemptive — a process holds the CPU until it blocks or finishes.

```
Processes: A(burst=4), B(burst=3), C(burst=2), all arrive at t=0
Timeline:  |AAAA|BBB|CC|
           0    4   7  9
```

- Average waiting time: (0 + 4 + 7) / 3 = 3.67
- **Convoy effect**: a long job behind a short one inflates waiting time for everyone.

## Shortest Job First (SJF) / Shortest Remaining Time (SRT)

Schedule the process with the shortest burst time. Non-preemptive (SJF) or preemptive (SRT — also called SRTF).

```
Same processes (sorted by burst): C(2), B(3), A(4)
Timeline:  |CC|BBB|AAAA|
           0  2   5    9
```

- Average waiting time: (0 + 2 + 5) / 3 = 2.33 — optimal for average waiting time.
- **Problem**: requires knowing burst time in advance. Real OSes estimate using exponential averaging: `τ_{n+1} = α · t_n + (1-α) · τ_n`.

## Round Robin (RR)

Each process gets a fixed **quantum** Q. If it does not finish, it goes to the back of the queue. Designed for time-sharing.

```
Q=2, Processes: A(burst=4), B(burst=3), C(burst=2)
Timeline: |AA|BB|CC|AA|B|
           0  2  4  6  8 9
```

- Fair: no starvation.
- Response time ≈ Q × (N−1) for N processes.
- **Quantum choice matters**: too small → high context-switch overhead; too large → degenerates to FCFS.

## Priority Scheduling

Each process has a priority; the highest-priority runnable process runs next. Can be preemptive or non-preemptive.

- **Starvation risk**: low-priority processes may never run.
- **Aging fix**: gradually increase priority of waiting processes.

```c
// Simplified ready-queue pick in a priority scheduler
struct proc *next = NULL;
for (struct proc *p = proc_table; p < &proc_table[NPROC]; p++) {
    if (p->state == RUNNABLE)
        if (!next || p->priority > next->priority)
            next = p;
}
```

## Multilevel Feedback Queue (MLFQ)

The most sophisticated and widely used in practice (Linux CFS is a variant). Multiple queues at different priority levels:

1. New processes enter the highest-priority queue.
2. If a process uses its full quantum without blocking, it is demoted to a lower queue (longer quantum).
3. I/O-bound processes that voluntarily yield stay at high priority.

This approximates SJF without needing to know burst times in advance — CPU-bound jobs self-select into lower queues over time.

## Completely Fair Scheduler (Linux CFS)

Linux uses a red-black tree sorted by **virtual runtime** (`vruntime`). The process with the smallest `vruntime` always runs next. Each nanosecond of real CPU time increments `vruntime` by `1 / weight`, where weight reflects priority (nice value). This achieves fairness without discrete time quanta.

## Algorithm Comparison

| Algorithm | Preemptive | Starvation | Best For |
|-----------|-----------|-----------|---------|
| FCFS      | No        | No        | Batch, simple |
| SJF       | No        | Yes       | Minimum avg wait |
| SRT       | Yes       | Yes       | Optimal avg wait |
| RR        | Yes       | No        | Interactive / time-sharing |
| Priority  | Either    | Yes       | Real-time with aging |
| MLFQ      | Yes       | No (with aging) | General purpose |

## Common Pitfalls

- Confusing response time (first run) with waiting time (total wait).
- Assuming SJF is always best — it causes starvation and requires future knowledge.
- Choosing too small a quantum in RR — context-switch overhead dominates.

> **Interview answer:** The classic scheduling algorithms are FCFS (simple FIFO), SJF/SRT (optimal average wait but requires burst-time knowledge), Round Robin (fair time-sharing with a quantum), Priority (hierarchy with starvation risk), and MLFQ (adaptive multi-level approach that approximates SJF without prior knowledge) — Linux CFS is a modern MLFQ variant using virtual runtime in a red-black tree.
