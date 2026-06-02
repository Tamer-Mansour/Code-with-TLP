# Shortest-Job-First (SJF) and Shortest-Remaining-Time

Shortest-Job-First (SJF) selects the process with the smallest CPU burst next. It is provably optimal for minimizing average waiting time among non-preemptive algorithms — but it comes with significant practical challenges.

## Two Variants

### Non-Preemptive SJF (Classic SJF)

When the CPU becomes free, the scheduler picks the ready process with the shortest burst time. Once a process starts, it runs to completion.

### Preemptive SJF — Shortest-Remaining-Time First (SRTF)

Whenever a new process arrives, the scheduler compares its burst time against the **remaining** burst of the currently running process. If the new arrival is shorter, the current process is preempted immediately.

SRTF minimizes average waiting time across all scheduling algorithms, but the preemption overhead and the burst-time prediction problem limit its practical use.

## Worked Example — Non-Preemptive SJF

| Process | Arrival Time | Burst Time |
|---------|-------------|------------|
| P1      | 0           | 8 ms       |
| P2      | 1           | 4 ms       |
| P3      | 2           | 9 ms       |
| P4      | 3           | 5 ms       |

At time 0 only P1 is available, so P1 runs.

```
| P1 (0–8) | P2 (8–12) | P4 (12–17) | P3 (17–26) |
0          8          12           17           26
```

- **Waiting times:** P1 = 0, P2 = 7, P3 = 15, P4 = 9
- **Average waiting time:** (0 + 7 + 15 + 9) / 4 = **7.75 ms**

Compare that to FCFS order (P1, P2, P3, P4): average = (0 + 7 + 11 + 18) / 4 = **9 ms**. SJF wins.

## Worked Example — Preemptive SRTF

Using the same processes:

```
Time 0: P1 starts (remaining = 8)
Time 1: P2 arrives (burst 4 < remaining 7) → preempt P1, run P2
Time 2: P3 arrives (burst 9 > remaining 3) → P2 continues
Time 3: P4 arrives (burst 5 > remaining 2) → P2 continues
Time 5: P2 finishes. Ready: P1(r=7), P3(r=9), P4(r=5) → P4 runs
Time 10: P4 finishes. Ready: P1(r=7), P3(r=9) → P1 runs
Time 17: P1 finishes. P3 runs.
Time 26: P3 finishes.

Gantt: |P1(0-1)|P2(1-5)|P4(5-10)|P1(10-17)|P3(17-26)|
```

- **Waiting times:** P1 = (1–0) + (10–5) = 6... wait = total_time - burst = (17–0) - 8 = 9... actually:
  - P1: finishes at 17, arrived 0, burst 8 → waiting = 17 - 0 - 8 = 9
  - P2: finishes at 5, arrived 1, burst 4 → waiting = 5 - 1 - 4 = 0
  - P3: finishes at 26, arrived 2, burst 9 → waiting = 26 - 2 - 9 = 15
  - P4: finishes at 10, arrived 3, burst 5 → waiting = 10 - 3 - 5 = 2
- **Average waiting time:** (9 + 0 + 15 + 2) / 4 = **6.5 ms** — better than non-preemptive SJF.

## The Burst-Time Prediction Problem

The OS cannot know the future. In practice, burst time is **estimated** using an exponential average of past bursts:

```
τ_(n+1) = α * t_n + (1 - α) * τ_n
```

- `t_n` = actual CPU burst of the nth burst
- `τ_n` = predicted burst for the nth burst
- `α` ∈ [0, 1] controls how much weight recent history gets (typically α = 0.5)

```python
# Exponential average prediction
def predict_next(alpha, actual, predicted):
    return alpha * actual + (1 - alpha) * predicted
```

With α = 0.5 and initial τ₀ = 10 ms, actual bursts [6, 4, 6, 4]:
- τ₁ = 0.5*6 + 0.5*10 = 8
- τ₂ = 0.5*4 + 0.5*8 = 6
- τ₃ = 0.5*6 + 0.5*6 = 6
- τ₄ = 0.5*4 + 0.5*6 = 5

The prediction converges toward the true average over time.

## Starvation Risk

SJF can cause **starvation**: a long process may wait indefinitely if short processes keep arriving. The solution is **aging** — incrementally increasing a waiting process's priority so it eventually gets scheduled.

## Key Properties

| Property             | SJF (non-preemptive) | SRTF (preemptive)       |
|----------------------|---------------------|-------------------------|
| Optimal avg wait?    | Yes (among non-preemptive) | Yes (overall)      |
| Starvation           | Possible            | Possible                |
| Overhead             | Low                 | Higher (context switches) |
| Burst time known?    | Must be estimated   | Must be estimated        |
| Practical use        | Batch systems       | Rare; too much overhead  |

## Common Pitfalls

- **Claiming SJF is always optimal:** It is optimal only for average waiting time, not for response time or fairness.
- **Forgetting the estimation problem:** In real systems you can never know exact burst times.
- **Ignoring starvation:** Without aging, long jobs may never run.

> **Interview answer:** "SJF minimizes average waiting time by always running the shortest available job, but it requires predicting future burst times (usually via exponential averaging) and risks starving long processes. SRTF is the preemptive variant that is globally optimal for average waiting time."
