# Priority Inversion and Priority Inheritance

Priority inversion is one of the subtlest bugs in real-time and embedded systems: a high-priority task is indirectly blocked by a low-priority task, causing the scheduling guarantees of the system to break down. It famously brought NASA's Mars Pathfinder to its knees in 1997.

## What is Priority Inversion?

In a priority-based preemptive scheduler, a high-priority task should never wait for a low-priority task. Priority inversion occurs when this rule is violated — not because of a direct dependency, but because a **medium-priority task preempts** the low-priority task that holds a resource the high-priority task needs.

### The Classic Three-Task Scenario

| Task | Priority | Status |
|------|----------|--------|
| H | High | Needs mutex M |
| M | Medium | CPU-intensive, no relation to M |
| L | Low | Holds mutex M |

1. L acquires mutex M.
2. H wakes up, preempts L (H is higher priority), then tries to acquire M — **blocks**, because L holds it.
3. M wakes up, preempts L (M > L priority). M runs to completion.
4. L finally runs, releases M.
5. H resumes.

**Result:** H effectively ran at L's priority — even lower, because M ran in between. H's deadline may be missed.

```
Time →
L:    [acquires M]─────[preempted by H, then M]──────────[runs, releases M]
M:                                         [runs to completion]
H:         [wakes, blocked on M]───────────────────────────────────[runs]

High-prio H waited as long as medium-prio M took to finish — inversion!
```

## Priority Inheritance Protocol (PIP)

The most widely used fix. **When a high-priority task blocks on a mutex held by a low-priority task, the low-priority task temporarily inherits the high-priority task's priority** until it releases the mutex.

```
1. L holds M at priority LOW.
2. H blocks on M → L's priority is raised to HIGH.
3. M tries to preempt L — but now L has priority HIGH, so M cannot preempt.
4. L runs at HIGH, quickly releases M.
5. H acquires M, runs at HIGH.
6. M runs at MEDIUM (after both H and L are done).
```

This keeps the blocking time of H bounded by the time L needs to finish its critical section — not by how long M runs.

### PIP in POSIX

```c
#include <pthread.h>

pthread_mutex_t m;
pthread_mutexattr_t attr;

void setup_pi_mutex() {
    pthread_mutexattr_init(&attr);
    // Enable priority inheritance on this mutex
    pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);
    pthread_mutex_init(&m, &attr);
}
```

Linux supports `PTHREAD_PRIO_INHERIT` for real-time threads (`SCHED_FIFO` / `SCHED_RR`).

## Priority Ceiling Protocol (PCP)

An alternative that prevents priority inversion AND deadlock. Assign each mutex a **priority ceiling** equal to the highest priority of any task that might lock it. A task can only lock a mutex if its priority exceeds the ceilings of all *currently locked* mutexes it does not already hold.

- Guarantees that a task can always acquire all the mutexes it needs without blocking (except at entry).
- Used in POSIX with `PTHREAD_PRIO_PROTECT`.
- Common in avionics and automotive RTOS environments (AUTOSAR, VxWorks).

## The Mars Pathfinder Incident (1997)

The spacecraft used VxWorks RTOS. Three tasks:
- **ASI/MET** (meteorological, low priority) held an information bus mutex.
- **bc_dist** (communications, high priority) needed the bus mutex — blocked.
- **bc_sched** (medium priority) ran CPU-intensive tasks.

bc_sched preempted ASI/MET, blocking bc_dist for longer than its watchdog timeout. The system watchdog interpreted this as a system error and repeatedly reset the spacecraft. Engineers diagnosed the bug remotely and enabled priority inheritance via a parameter uplink — fixing a spacecraft 190 million km away through a software patch.

## Comparison

| Protocol | Prevents Inversion | Prevents Deadlock | Overhead |
|----------|-------------------|-------------------|----------|
| **None** | No | No | Zero |
| **Priority Inheritance** | Yes | No | Low (runtime raise/lower) |
| **Priority Ceiling** | Yes | Yes | Higher (ceiling checks per lock) |

## Common Pitfalls

- Priority inheritance is **not transitive by default** — if L holds two nested mutexes, inheritance must propagate through the chain.
- Inheritance only helps if the **scheduler supports priority changes at runtime** (real-time schedulers do; normal `SCHED_OTHER` does not).
- Forgetting to set the mutex attribute is silent — the lock works but without PIP.

## Interview Answer

> "Priority inversion occurs when a high-priority task is blocked waiting for a resource held by a low-priority task that is itself preempted by a medium-priority task. Priority inheritance fixes it by temporarily boosting the low-priority holder to the blocked task's priority, bounding the inversion window. The Mars Pathfinder bug in 1997 is the most famous real-world example."
