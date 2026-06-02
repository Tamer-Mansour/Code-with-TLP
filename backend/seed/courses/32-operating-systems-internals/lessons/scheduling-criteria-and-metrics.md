# Scheduling Metrics: Throughput, Turnaround, Waiting, Response

To compare scheduling algorithms fairly, we need precise definitions. Four metrics dominate OS textbooks and interview questions. Understanding what each measures — and how to compute it from a Gantt chart — is essential.

## The Four Core Metrics

### 1. Throughput

**Throughput** = number of processes completed per unit time.

```
Throughput = (number of processes completed) / (total elapsed time)
```

A scheduler that completes 5 processes in 20 ms has throughput of 0.25 processes/ms (250 processes/sec). Higher is better. Throughput is most relevant for batch workloads.

### 2. Turnaround Time

**Turnaround time** = time from process submission to process completion.

```
Turnaround Time = Completion Time - Arrival Time
```

It captures the total experience of a process — waiting in the ready queue + executing + waiting for I/O + executing again. Lower is better.

### 3. Waiting Time

**Waiting time** = total time a process spends in the **ready queue** (not running, not doing I/O).

```
Waiting Time = Turnaround Time - Burst Time
            = (Completion Time - Arrival Time) - CPU Burst Time
```

Note: waiting time counts only idle time in the ready queue, not I/O wait time. Lower is better. Most scheduling algorithms optimize this metric.

### 4. Response Time

**Response time** = time from submission until the process **first** receives CPU time.

```
Response Time = First CPU Start Time - Arrival Time
```

Response time is critical for interactive systems. A user pressing a key wants acknowledgment immediately, even if the full computation takes longer. Lower is better.

## Worked Example

Three processes arrive at time 0 with the following CPU bursts (assume no I/O):

| Process | Arrival | Burst |
|---------|---------|-------|
| P1      | 0       | 6 ms  |
| P2      | 0       | 3 ms  |
| P3      | 0       | 4 ms  |

**FCFS order (P1 → P2 → P3):**

```
| P1     | P2  | P3   |
0        6     9     13
```

| Process | Arrival | Burst | Completion | Turnaround | Waiting | Response |
|---------|---------|-------|------------|------------|---------|----------|
| P1      | 0       | 6     | 6          | 6          | 0       | 0        |
| P2      | 0       | 3     | 9          | 9          | 6       | 6        |
| P3      | 0       | 4     | 13         | 13         | 9       | 9        |

- Average Turnaround = (6 + 9 + 13) / 3 = **9.33 ms**
- Average Waiting    = (0 + 6 + 9) / 3  = **5 ms**
- Average Response  = (0 + 6 + 9) / 3  = **5 ms**
- Throughput = 3 / 13 ≈ **0.23 processes/ms**

If we instead ran **SJF (P2 → P3 → P1)**:

```
| P2  | P3   | P1     |
0     3      7       13
```

- Average Turnaround = (3 + 7 + 13) / 3 = **7.67 ms** (improvement)
- Average Waiting    = (0 + 3 + 7) / 3  = **3.33 ms** (improvement)

SJF minimizes average waiting time among non-preemptive algorithms.

## Additional Criteria

Beyond the four core metrics, real schedulers also consider:

- **CPU Utilization** — keep the CPU as busy as possible (target: 40–90%).
- **Fairness** — no process should starve indefinitely.
- **Priority** — high-priority tasks should not wait behind low-priority ones.
- **Deadline** — real-time systems require processes to complete before a hard deadline.

## Optimization Trade-offs

No single algorithm maximizes all metrics simultaneously. Common trade-offs:

| Algorithm | Best for           | Weakness              |
|-----------|--------------------|-----------------------|
| FCFS      | Simplicity         | High average wait (convoy effect) |
| SJF       | Min average wait   | Needs burst prediction; starvation |
| Round Robin | Response time   | High context-switch overhead |
| Priority  | Differentiated SLA | Starvation of low-priority tasks |

## Common Pitfalls

- Confusing **waiting time** and **turnaround time**. Turnaround includes burst time; waiting does not.
- Confusing **response time** and **waiting time**. Response time measures the first CPU touch; waiting time accumulates across all ready-queue stints.
- Forgetting that **arrival time** matters. If all processes arrive at time 0, turnaround = completion. If they stagger, you must subtract the arrival time.

## Interview Answer

> "Turnaround time is completion minus arrival; waiting time is turnaround minus burst; response time is first CPU access minus arrival. SJF minimizes average waiting time but requires predicting burst length."
