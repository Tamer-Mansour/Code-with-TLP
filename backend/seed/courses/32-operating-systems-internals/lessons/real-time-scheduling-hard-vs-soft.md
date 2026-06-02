# Real-Time Scheduling: Hard vs Soft Deadlines

## What Makes Scheduling "Real-Time"?

In general-purpose scheduling, "fast" means a good average. In **real-time scheduling**, correctness depends on *timing* — a result delivered after its deadline is wrong, regardless of how good the computation was. The scheduler must make and honor **timing guarantees**, not just optimize throughput or fairness.

Real-time systems are common in:
- Anti-lock braking systems (ABS)
- Cardiac pacemakers
- Industrial robot controllers
- Audio/video codecs
- Trading systems

## Hard vs Soft Real-Time

| Property | Hard Real-Time | Soft Real-Time |
|----------|---------------|----------------|
| Deadline miss | **System failure** (catastrophic) | Degraded quality (tolerable) |
| Examples | Airbag trigger, fly-by-wire | Video playback, audio buffering |
| Guarantee required | Deterministic, provable | Statistical (e.g., 99.9th percentile) |
| OS examples | VxWorks, FreeRTOS, QNX | Linux with PREEMPT_RT, Windows |

A missed deadline in a hard real-time system is not just a performance bug — it can cause physical harm or legal liability.

## Key Real-Time Terminology

**Period (T):** How frequently a task recurs. A sensor task with T=10 ms must execute once every 10 ms.

**Deadline (D):** By when the task must finish. Often D = T (deadline equals period), but some tasks have D < T (must finish early) or D > T (relaxed deadline).

**Worst-Case Execution Time (WCET):** The maximum CPU time a task ever needs in one instance. This is the critical value for feasibility analysis. Measuring accurate WCET is notoriously hard — modern CPUs with caches and pipelines make WCET estimation an active research area.

**Utilization (U):** Fraction of CPU time consumed by a task:

```
U_i = C_i / T_i    (C = WCET, T = period)

Total utilization: U = Σ (C_i / T_i)
```

If U > 1.0, the system is **overloaded** — deadlines *will* be missed no matter the scheduler.

## Schedulability Analysis

For a task set to be feasible (all deadlines always met), the scheduler must be able to prove it. Two classical results:

1. **Rate-Monotonic (RM) bound:** A set of n periodic tasks is schedulable under RM if:
   ```
   U ≤ n(2^(1/n) − 1)
   ```
   This converges to ln(2) ≈ 0.693 as n → ∞. So RM can leave 30% of the CPU idle even when tasks are schedulable.

2. **EDF optimal:** EDF can schedule any feasible task set up to U = 1.0. No deadline-based algorithm does better on a uniprocessor.

## Preemption and Latency

Hard real-time requires **bounded preemption latency** — the time from when a high-priority task becomes ready to when it actually runs on the CPU. Sources of latency:

```
Total latency = interrupt latency
              + scheduler decision time
              + context switch time
              + cache/pipeline refill time
```

General-purpose OSes (vanilla Linux) have latencies of milliseconds. Real-time kernels (PREEMPT_RT Linux, VxWorks) reduce this to tens of microseconds by making almost all kernel code preemptible.

## Soft Real-Time in Practice

Linux provides soft real-time through POSIX scheduling policies:

```c
struct sched_param sp = { .sched_priority = 50 };

// SCHED_FIFO: run until blocked or preempted by higher priority
sched_setscheduler(0, SCHED_FIFO, &sp);

// SCHED_RR: like FIFO but with a round-robin quantum
sched_setscheduler(0, SCHED_RR, &sp);

// SCHED_DEADLINE: EDF-based, specify runtime/deadline/period
struct sched_attr attr = {
    .sched_policy   = SCHED_DEADLINE,
    .sched_runtime  = 5000000,   // 5 ms WCET
    .sched_deadline = 10000000,  // 10 ms deadline
    .sched_period   = 10000000,  // 10 ms period
};
syscall(SYS_sched_setattr, 0, &attr, 0);
```

## Common Pitfalls

- **Confusing soft and hard** — calling a system "real-time" because it uses SCHED_FIFO does not make it hard real-time.
- **Ignoring WCET** — using average execution time instead of worst-case makes feasibility analysis meaningless.
- **Priority inversion** — can cause hard-RT tasks to miss deadlines; always pair with priority inheritance on shared resources.
- **Overloaded systems** — when U > 1, no scheduler can save you; the only fix is more CPU, fewer tasks, or shorter WCETs.

> **Interview answer:** Hard real-time systems treat a missed deadline as a failure and require provably bounded latency; soft real-time systems tolerate occasional misses with degraded quality. Schedulability analysis (RM bound, EDF optimality) determines whether a task set can meet its deadlines.
