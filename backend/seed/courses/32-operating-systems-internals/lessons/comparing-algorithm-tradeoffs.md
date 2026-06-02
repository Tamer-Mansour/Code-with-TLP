# Comparing FCFS, SJF, and RR Trade-offs

No single scheduling algorithm is universally best. Each algorithm optimizes for different goals and makes different assumptions about the workload. Understanding the trade-offs lets you reason about which algorithm — or combination — fits a given system design.

## The Key Metrics

| Metric                  | Definition                                        |
|-------------------------|---------------------------------------------------|
| **Waiting time (WT)**   | Time a process spends ready but not running       |
| **Turnaround time (TAT)** | Total time from arrival to completion (CT − arrival) |
| **Response time (RT)**  | Time from arrival to first CPU access             |
| **Throughput**          | Processes completed per unit time                 |
| **CPU utilization**     | Fraction of time CPU does useful work             |
| **Fairness**            | No process waits disproportionately long          |

## Side-by-Side Comparison

| Criterion               | FCFS                       | SJF (non-preemptive)        | Round Robin                   |
|-------------------------|----------------------------|-----------------------------|-------------------------------|
| Preemptive              | No                         | No                          | Yes                           |
| Optimal avg WT          | No                         | Yes (among non-preemptive)  | No                            |
| Optimal response time   | No                         | No                          | Best among the three          |
| Starvation              | No                         | Yes (long jobs)             | No                            |
| Convoy effect           | Yes                        | No                          | No                            |
| Burst knowledge needed  | No                         | Yes (estimation)            | No                            |
| Context switch overhead | Low                        | Low                         | High (every quantum)          |
| Best for                | Batch, simple systems      | Batch with known bursts     | Interactive, time-sharing     |

## Concrete Scenario Comparisons

### Scenario A: Mixed Short and Long Jobs

Three processes: P1(burst=50), P2(burst=2), P3(burst=3). All arrive at t=0.

- **FCFS (P1→P2→P3):** Avg WT = (0 + 50 + 52)/3 = 34 ms. Convoy effect visible.
- **SJF (P2→P3→P1):** Avg WT = (0 + 2 + 5)/3 = 2.33 ms. Dramatic improvement.
- **RR quantum=4:** P1 preempted repeatedly. Avg WT ≈ much higher than SJF but P2 and P3 finish early. Good response time for short jobs.

### Scenario B: Equal Burst Times

Five processes each with burst=10, all arrive at t=0.

- **FCFS:** Avg WT = (0+10+20+30+40)/5 = 20 ms.
- **SJF:** Same as FCFS (all bursts equal). Avg WT = 20 ms.
- **RR quantum=10:** Same as FCFS (each finishes in one slice). Avg WT = 20 ms.
- **RR quantum=5:** P1 finishes at 50, P2 at 50, ... Avg WT = same 20 ms, but all processes get CPU earlier → better response time.

## When Each Algorithm Wins

### Use FCFS when:
- Workload consists of jobs with similar burst times (convoy effect is negligible).
- Simplicity and zero overhead are paramount (e.g., a simple batch job queue).
- Implementation resources are constrained (embedded systems, simple batch processing).

### Use SJF when:
- Burst times are predictable or can be estimated accurately.
- Minimizing average waiting time is the primary goal.
- Starvation can be tolerated or mitigated with aging.
- Batch workloads dominate (no interactive users waiting for a response).

### Use Round Robin when:
- The system is interactive and users expect quick response.
- Fairness matters — every process must make progress.
- Burst times are unknown or highly variable.
- You need a bounded worst-case response time: (n−1) × quantum.

## The Response Time vs. Waiting Time Trade-off

```
Optimize waiting time  →  SJF (short jobs finish quickly, fewer total wait cycles)
Optimize response time →  RR with small quantum (everyone gets the CPU fast)
```

These goals conflict. SJF can leave a long job waiting until all short jobs complete. RR ensures every process runs within (n−1) quanta, even if it ultimately takes longer to finish each one.

## Real-World Systems Combine All Three

Modern OS schedulers such as Linux's CFS or Windows' HPET scheduler use **multi-level feedback queues (MLFQ)** that combine ideas from all three:
- New processes start with a small quantum (like RR) to catch short-burst interactive tasks.
- Processes that repeatedly use their full quantum are moved to lower-priority queues with larger quanta (approaching FCFS for CPU-bound jobs).
- I/O-bound processes are boosted (approximating SJF's preference for short jobs).

## Common Interview Pitfalls

- Saying "RR is always better": it trades waiting time for response time.
- Forgetting that SJF requires burst prediction, which is never exact.
- Overlooking starvation in SJF without aging.
- Claiming FCFS causes starvation: it does not — every job runs eventually.

> **Interview answer:** "FCFS is simple but suffers the convoy effect. SJF minimizes average waiting time but requires burst prediction and risks starvation. Round Robin guarantees bounded response time and fairness but increases context switches and average waiting time compared to SJF. Real schedulers combine them in a multi-level feedback queue."
