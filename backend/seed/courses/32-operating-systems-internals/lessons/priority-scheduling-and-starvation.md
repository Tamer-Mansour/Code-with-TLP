# Priority Scheduling and Starvation

## What Is Priority Scheduling?

Priority scheduling assigns every process a numeric priority. The scheduler always runs the highest-priority ready process. When a higher-priority process becomes ready, it either **preempts** the running process immediately (preemptive variant) or waits until the CPU is voluntarily released (non-preemptive variant). Most modern operating systems use preemptive priority scheduling.

Priority values are typically integers. Conventions vary: Linux uses negative-is-higher (nice values from -20 to +19), while many textbooks use lower-number-is-higher.

## How It Works

```
Ready Queue (sorted by priority):
[P1, pri=1] [P3, pri=3] [P5, pri=5] [P7, pri=7]
                ^
         CPU dispatched here (lowest number = highest priority)
```

At every scheduling event (new arrival, I/O completion, time-slice expiry) the scheduler picks the front of this priority-sorted queue.

```python
import heapq

class PriorityScheduler:
    def __init__(self):
        self.ready = []          # min-heap: (priority, arrival, pid)
        self.time  = 0

    def add_process(self, pid, priority, arrival, burst):
        heapq.heappush(self.ready, (priority, arrival, pid, burst))

    def run_next(self):
        if not self.ready:
            return None
        priority, arrival, pid, burst = heapq.heappop(self.ready)
        self.time += burst
        return pid, self.time   # pid finished at self.time
```

## Internal vs External Priority

| Source | Description | Example |
|--------|-------------|---------|
| **External** | Set by user or administrator | `nice -n -5 ./myapp` |
| **Internal** | Computed by the OS from process behavior | I/O-bound process gets a boost |
| **Hybrid** | Base from user, adjusted by OS | Linux CFS nice + vruntime |

## Preemptive vs Non-Preemptive

With **preemptive** priority scheduling, a newly arrived high-priority process kicks out the currently running process immediately. This minimises response time for urgent tasks but increases context-switch overhead.

With **non-preemptive** priority scheduling, the running process finishes its current CPU burst before the scheduler re-evaluates. Simpler to implement but high-priority processes can still wait.

## The Starvation Problem

**Starvation** (also called *indefinite blocking*) occurs when a low-priority process never gets CPU time because a continuous stream of higher-priority processes keeps arriving. This is not a hypothetical edge case — production systems have had processes starved for hours or days.

```
Timeline (new priority-1 job arrives every quantum):

P_low (pri=10): [waiting........waiting........waiting........NEVER RUNS]
P_hi  (pri=1):  [run][run][run][run][run][run][run][run][run][run]...
```

Starvation is a direct consequence of the design: optimising for high-priority responsiveness at the cost of low-priority fairness.

## Common Pitfalls

- **Priority inversion** — a high-priority process is blocked waiting for a resource held by a low-priority process. The Mars Pathfinder mission experienced this in 1997. The fix is **priority inheritance**: the low-priority holder temporarily runs at the blocker's priority.
- **Priority assignment errors** — giving too many processes the same high priority defeats the purpose and creates a de-facto FCFS queue at the top.
- **Ignoring I/O vs CPU bound** — a pure priority scheme without behavioral adjustment will unfairly penalize I/O-intensive interactive tasks.

## Worked Example

Three processes arrive at t=0:

| PID | Priority | Burst |
|-----|----------|-------|
| P1  | 3        | 10 ms |
| P2  | 1        | 4 ms  |
| P3  | 2        | 6 ms  |

Preemptive scheduling order: P2 (finishes t=4) → P3 (finishes t=10) → P1 (finishes t=20).

Average waiting time = (16 + 0 + 4) / 3 = **6.67 ms** (compare with FCFS average of 10 ms for the same set).

> **Interview answer:** Priority scheduling always runs the highest-priority ready process; the main hazard is starvation of low-priority processes, which is solved with aging or priority inheritance.
