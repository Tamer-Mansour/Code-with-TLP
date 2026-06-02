# Rate-Monotonic and Earliest-Deadline-First

## Two Algorithms, One Goal

Real-time scheduling offers two classical uniprocessor algorithms with strong theoretical foundations:

- **Rate-Monotonic (RM):** A static-priority algorithm. Assign priorities at design time based on task frequency — the more frequent the task, the higher its priority.
- **Earliest-Deadline-First (EDF):** A dynamic-priority algorithm. At every scheduling point, run whichever task has the nearest absolute deadline.

Both are optimal in their respective classes. Understanding when to use each, and why, is a common interview and systems design question.

## Rate-Monotonic Scheduling

**Rule:** Priority ∝ 1/Period. Short-period (fast) tasks get the highest priority.

```
Task A: C=3ms, T=10ms  → priority 1 (highest, shortest period)
Task B: C=2ms, T=15ms  → priority 2
Task C: C=2ms, T=20ms  → priority 3 (lowest, longest period)

Total utilization U = 3/10 + 2/15 + 2/20 = 0.30 + 0.133 + 0.10 = 0.533
RM bound (n=3): 3(2^(1/3) − 1) ≈ 0.780
0.533 ≤ 0.780 → schedulable under RM ✓
```

**Timeline (first 20 ms):**

```
t= 0: A runs (3ms)
t= 3: B runs (2ms)
t= 5: C runs (2ms)
t= 7: CPU idle until t=10
t=10: A runs again (3ms)
t=13: B runs — but B's next period is t=15, so it starts now
t=15: A period 3 starts, preempts B (A has higher priority)
...
```

RM priorities are **fixed at runtime** — no recalculation needed. This makes RM easy to implement and analyze, and predictable for certification (avionics, medical devices).

## Earliest-Deadline-First Scheduling

**Rule:** At every scheduling event, run the ready task whose absolute deadline is soonest.

```python
import heapq

class EDFScheduler:
    def __init__(self):
        self.ready = []          # min-heap: (absolute_deadline, task_id)

    def add_task(self, task_id, deadline):
        heapq.heappush(self.ready, (deadline, task_id))

    def next_task(self):
        if self.ready:
            deadline, task_id = heapq.heappop(self.ready)
            return task_id, deadline
        return None, None
```

**Same task set as above, EDF:**

```
t= 0: Deadlines: A=10, B=15, C=20 → run A (earliest)
t= 3: Deadlines: B=15, C=20 → run B
t= 5: Deadlines: C=20, A=10(next at t=10) → run C
t= 7: Idle
t=10: A arrives (deadline=20), C has deadline=20 — TIE → run A or C
...
```

EDF dynamically reorders tasks as deadlines change, achieving **100% utilization** on feasible task sets (no wasted idle time as long as U ≤ 1.0).

## Direct Comparison

| Property | Rate-Monotonic | EDF |
|----------|---------------|-----|
| Priority type | Static (fixed) | Dynamic (changes at runtime) |
| Max utilization guarantee | n(2^(1/n)−1) → ~69% | 100% |
| Optimality | Optimal among fixed-priority | Optimal among all uniprocessor |
| Implementation complexity | Simple | Moderate (heap maintenance) |
| Overload behavior | Lowest-priority task misses | Arbitrary task may miss |
| Certification friendliness | High (ARINC 653, DO-178C) | Lower (dynamic hard to verify) |

## Why RM Is Preferred in Safety-Critical Systems

Even though EDF handles higher utilization, RM's static priorities make its behavior **deterministic and verifiable**. In an overloaded system:

- **RM:** The lowest-priority (longest-period) task misses its deadline. This is predictable — you know *which* task fails.
- **EDF:** Any task can miss, depending on the exact timing of arrivals. The failure mode is non-deterministic.

Avionics and medical standards prefer predictable failure modes.

## The Liu & Layland Bound in Detail

The RM utilization bound n(2^(1/n) − 1):

```
n=1: 1.000 (one task, always schedulable if U ≤ 1.0)
n=2: 0.828
n=3: 0.780
n=5: 0.743
n=∞: ln(2) ≈ 0.693
```

This is a **sufficient** condition, not necessary. A task set can be schedulable under RM even with U > 0.693 — exact analysis (response-time analysis) can prove schedulability up to U=1.0 for specific task sets.

## Practical Notes

- **Linux SCHED_DEADLINE** implements EDF with CBS (Constant Bandwidth Server) to isolate tasks and prevent one task's overrun from affecting others.
- **Mixed criticality** systems often run hard-RT tasks under RM and soft-RT tasks under EDF on separate cores.
- **Jitter** — if task periods are not perfectly aligned, peak-load moments can be worse than the average utilization suggests. Factor in worst-case phasing when computing schedulability.

> **Interview answer:** Rate-Monotonic assigns static priorities by frequency (shortest period = highest priority) and is schedulable if U ≤ ln(2) ≈ 69%; EDF dynamically runs the task with the nearest deadline and can achieve 100% utilization — RM is preferred in safety-critical systems for its predictable failure mode.
