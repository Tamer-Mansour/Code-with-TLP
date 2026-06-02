# Video: CPU Scheduling Algorithms

This video walks through the major CPU scheduling algorithms — FCFS, SJF, Round-Robin, and priority scheduling — and shows how to compute key performance metrics like waiting time, turnaround time, and CPU utilization.

## What This Video Covers

- Scheduling criteria: CPU utilization, throughput, turnaround time, waiting time, response time
- First-Come-First-Served (FCFS) and its convoy effect
- Shortest-Job-First (SJF) — both preemptive (SRTF) and non-preemptive variants
- Round-Robin scheduling and the quantum selection trade-off
- Priority scheduling and starvation; aging as a remedy
- Multilevel feedback queues (MLFQ) used by real OSes

## Key Timestamps

| Timestamp | Topic |
|-----------|-------|
| 0:00 | Scheduling criteria and Gantt charts |
| ~15 min | FCFS and convoy effect |
| ~30 min | SJF and preemptive SRTF |
| ~45 min | Round-Robin with varying quantum |
| ~60 min | Priority scheduling + aging |
| ~75 min | Multilevel feedback queues |

## Key Takeaways

No single algorithm is optimal for all workloads. Round-Robin gives the best **response time** for interactive systems (small quantum), while SJF minimizes average **waiting time** but requires future knowledge of burst lengths. Real operating systems (Linux's CFS, Windows MLFQ) use adaptive schemes that approximate SJF behavior using historical CPU burst data, while guaranteeing bounded waiting through aging or virtual runtimes.
