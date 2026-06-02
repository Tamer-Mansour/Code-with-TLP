# Video: Synchronization — Locks, Semaphores, Deadlock, and the Banker's Algorithm

This video covers the OS synchronization toolkit in depth: mutexes, semaphores, monitors, and the four necessary conditions for deadlock along with detection and avoidance strategies including the Banker's Algorithm.

## What This Video Covers

- Mutexes and spinlocks: when to sleep vs spin
- Semaphores: binary vs counting, and the classic producer-consumer pattern
- Monitors and condition variables: the correct use of `wait()` inside a `while` loop
- The four Coffman conditions for deadlock: mutual exclusion, hold-and-wait, no preemption, circular wait
- Deadlock detection via cycle detection in resource-allocation graphs
- Deadlock avoidance: the Banker's Algorithm safety check
- Priority inversion and priority inheritance (Mars Pathfinder, 1997)

## Key Timestamps

| Timestamp | Topic |
|-----------|-------|
| 0:00 | Mutex and spinlock internals |
| ~20 min | Semaphores and producer-consumer |
| ~40 min | Monitors and condition variables |
| ~60 min | Deadlock conditions |
| ~75 min | Banker's Algorithm walkthrough |
| ~90 min | Priority inversion case study |

## Key Takeaways

Deadlock requires all four Coffman conditions simultaneously — break any one to prevent it. The Banker's Algorithm prevents deadlock by only granting resource requests that keep the system in a "safe state" (a state from which all processes can complete in some order). In practice, most systems opt for deadlock detection and recovery rather than avoidance, because avoidance requires knowing maximum resource needs in advance.
