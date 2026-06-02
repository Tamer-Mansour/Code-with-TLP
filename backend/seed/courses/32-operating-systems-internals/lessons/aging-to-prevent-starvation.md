# Aging: Preventing Starvation in Priority Schedulers

## The Problem Aging Solves

Pure priority scheduling guarantees that low-priority processes can wait indefinitely. **Aging** is the standard countermeasure: the OS gradually increases the effective priority of a process the longer it waits, so every process eventually becomes the highest priority in the queue.

> **Interview answer:** Aging periodically boosts the priority of waiting processes so no process starves, while still honoring priority for recently arrived work.

## How Aging Works

The scheduler maintains two values per process:

- **Static (base) priority** — assigned at creation or by the user; never changes.
- **Dynamic (effective) priority** — the value the scheduler actually uses; recalculated periodically.

A simple linear aging formula:

```
effective_priority = base_priority - (waiting_time / aging_factor)
```

A lower number wins (higher priority), so subtracting from the base priority makes the process rise over time.

## Python Implementation

```python
class Process:
    def __init__(self, pid, base_priority, burst):
        self.pid            = pid
        self.base_priority  = base_priority
        self.burst          = burst
        self.waiting_time   = 0

    def effective_priority(self, aging_factor=10):
        return self.base_priority - (self.waiting_time // aging_factor)

def aging_scheduler_step(ready_queue, aging_factor=10):
    """Called once per time quantum."""
    for p in ready_queue:
        p.waiting_time += 1          # increment all waiters

    # Pick lowest effective priority value (= highest urgency)
    ready_queue.sort(key=lambda p: p.effective_priority(aging_factor))
    chosen = ready_queue[0]
    return chosen
```

## Choosing the Aging Factor

| Aging factor | Effect |
|---|---|
| Very small (e.g., 1) | Priority rises fast — nearly FCFS, starving becomes impossible but priority ordering loses meaning |
| Moderate (e.g., 10–50) | Balanced — high-priority processes still get preference; low-priority eventually runs |
| Very large (e.g., 1000) | Priority rises so slowly that starvation reappears in practice |

Typical production systems use a factor that ensures a process at the lowest priority tier reaches the top within seconds to minutes, not hours.

## Aging in Real Operating Systems

**Linux (nice / CFS):** The Completely Fair Scheduler uses *virtual runtime* (`vruntime`) rather than explicit priorities. Processes that have run less accumulate less `vruntime` and naturally rise to the front — implicit aging built into the fairness invariant.

**Windows:** The dispatcher applies a *boost* when a thread has been starved for ~3–4 seconds, temporarily elevating it to priority 15 (just below real-time range), then decaying it back over time.

**POSIX SCHED_OTHER:** Implementations often apply a *dynamic bonus* based on recent sleep time, rewarding I/O-bound behavior and indirectly preventing starvation of interactive threads.

## Interaction With Priority Inheritance

Aging and priority inheritance solve different sub-problems:

| Problem | Solution |
|---|---|
| Low-priority process never scheduled | Aging |
| High-priority process blocked on resource held by low-priority process | Priority inheritance / priority ceiling |

Using both together is correct and common; they are complementary, not redundant.

## Common Pitfalls

- **Forgetting to reset aging state** — when a process finally runs, its waiting counter should reset to zero. Without the reset, the process immediately shoots back to the top even after receiving service.
- **Aging across suspension** — a process that voluntarily sleeps should not accumulate waiting-time credit, or it returns from sleep with unfair priority.
- **Integer overflow** — in embedded or long-running systems, an unbounded waiting counter can overflow. Cap it or use a rolling window.

## Worked Example

| PID | Base Priority | Waiting Time (quanta) | Effective Priority (factor=10) |
|-----|---------------|-----------------------|-------------------------------|
| P1  | 1             | 0                     | 1                             |
| P2  | 5             | 30                    | 5 - 3 = **2**                 |
| P3  | 8             | 60                    | 8 - 6 = **2**                 |

After 60 quanta of waiting, P3 (originally lowest) ties with P2 and is close to overtaking P1. Without aging, P3 would never run as long as P1 keeps arriving.
