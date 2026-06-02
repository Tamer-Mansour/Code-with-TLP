# Choosing the Right Time Quantum

The time quantum is the single most important tuning parameter for Round Robin scheduling. Get it right and the system feels snappy with high throughput. Get it wrong and you pay either in sluggish response times or wasted CPU cycles on context switches.

## The Two Extremes

### Quantum → ∞ (Very Large)

Round Robin degenerates into FCFS. Each process runs to completion before the next one starts. Response time suffers for all processes behind a long-running job, and the convoy effect returns.

### Quantum → 0 (Very Small)

Every process appears to run simultaneously — this is **processor sharing**, the theoretical ideal for fairness. In practice, however, the context switch overhead dominates. If the quantum is 10 µs and a context switch costs 5 µs, the CPU spends 33% of its time just switching, not doing useful work.

```
Useful CPU fraction = quantum / (quantum + ctx_switch_cost)

quantum = 10 µs, ctx_switch = 5 µs  →  10/15 = 67% useful
quantum = 1 ms,  ctx_switch = 5 µs  →  1000/1005 ≈ 99.5% useful
quantum = 100 ms, ctx_switch = 5 µs →  ~100% useful (but poor response)
```

## Rule of Thumb

A widely cited heuristic: **choose a quantum such that roughly 80% of CPU bursts complete within one quantum**. This means:

- Most processes finish or voluntarily block without being preempted — low context-switch overhead.
- The few long-running CPU-bound processes get preempted fairly.
- Response time stays bounded.

On Linux (since kernel 2.6), the default scheduling period is typically 6–100 ms depending on the number of runnable tasks, with individual quanta derived from that period.

## Measuring the Impact

Consider 5 processes each with burst time 10 ms. Compare quanta:

| Quantum | Avg Turnaround | Context Switches | Overhead |
|---------|---------------|------------------|----------|
| 1 ms    | ~50 ms        | ~50              | High     |
| 5 ms    | ~50 ms        | ~10              | Medium   |
| 10 ms   | ~50 ms (FCFS) | 5                | Low      |
| 12 ms   | ~50 ms (FCFS) | 5                | Low      |

With identical burst times, turnaround does not change much — but overhead does. With varied burst times, a smaller quantum helps short jobs finish sooner at the cost of more switching.

## Workload-Driven Selection

| Workload Type       | Recommendation              | Reason                                   |
|---------------------|-----------------------------|------------------------------------------|
| Interactive desktop | 10–50 ms                    | Human perceives < 100 ms as instantaneous |
| Server/batch mix    | 50–200 ms                   | Fewer switches, higher throughput        |
| Real-time soft      | Fixed, often 1–10 ms        | Hard response deadline required          |
| Database/CPU-bound  | Larger (100+ ms)            | Rarely benefit from preemption           |

## The Response Time Bound

For n processes each needing at most one quantum, the worst-case response time (time from arrival to first CPU access) is:

```
response_time ≤ (n − 1) × quantum
```

If you need a 200 ms response guarantee and you have at most 20 processes:

```
quantum ≤ 200 / (20 − 1) ≈ 10.5 ms  →  use 10 ms
```

This formula is a useful back-of-the-envelope sizing tool.

## Adaptive Quanta

Modern schedulers like Linux's Completely Fair Scheduler (CFS) do not use a fixed quantum. Instead, they allocate CPU time proportionally based on weights (nice values), dynamically adjusting the effective time slice per task. The conceptual lesson still applies: the time slice must be tuned to balance overhead and responsiveness.

## Common Pitfalls

- **Setting the quantum equal to the average burst:** That makes most jobs run exactly one slice, maximizing context switches. Set it slightly above the 80th percentile burst.
- **Ignoring cache effects:** After a context switch, the new process may cause cache misses. A slightly larger quantum amortizes this cost.
- **Assuming one-size-fits-all:** Different process classes (interactive vs. batch) often benefit from different quanta — hence multi-level feedback queues.

> **Interview answer:** "The time quantum should be large enough so context-switch overhead is small (the rule of thumb is 80% of bursts finish within one quantum), but small enough to keep response time bounded. Too small wastes CPU on switching; too large degrades to FCFS and increases response time."
