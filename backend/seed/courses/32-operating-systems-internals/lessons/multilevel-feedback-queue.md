# Multilevel Feedback Queue Scheduling

## The Key Innovation

The multilevel feedback queue (MLFQ) solves the central weakness of fixed multilevel queues: processes can **move between queues** based on their observed behavior. A CPU-bound process that monopolizes the CPU is demoted to a lower queue; an I/O-bound process that voluntarily releases the CPU early is promoted to a higher queue. The scheduler learns what each process is without being told upfront.

> **Interview answer:** MLFQ starts every process in the highest-priority queue and demotes it as it uses more CPU, so short interactive jobs get fast service and long CPU-bound jobs are pushed to lower queues — approximating SJF without knowing burst lengths in advance.

## Structure and Rules

```
Queue 0 (highest priority): quantum = 8 ms
Queue 1:                     quantum = 16 ms
Queue 2 (lowest priority):   quantum = ∞ (FCFS)
```

Classic MLFQ rules (Arpaci-Dusseau formulation):

1. If Priority(A) > Priority(B), A runs.
2. If Priority(A) == Priority(B), A and B run in RR.
3. A new process enters at the top (Queue 0).
4. If a process uses its entire quantum, it is demoted one level.
5. If a process releases the CPU before its quantum expires (I/O wait), it stays at its current level.
6. Periodically, all processes are moved back to Queue 0 (**priority boost**).

Rule 6 prevents starvation and re-adapts to processes that change behavior (e.g., a compiler that starts interactive then shifts to heavy computation).

## Worked Timeline

```
Three processes: A (CPU-bound), B (interactive), C (new batch)
Quanta: Q0=8ms, Q1=16ms

t=0:  A and B enter Q0. A gets CPU → uses all 8ms → demoted to Q1
t=8:  B gets CPU → yields at 3ms (I/O) → stays in Q0
t=11: B returns from I/O → Q0. A in Q1.
      B runs again (short burst). A waits in Q1.
...
t=50: Priority boost → A, B both return to Q0.
```

Interactive B consistently gets short turnarounds. CPU-bound A gets its work done in Q1 and Q2 without starving B.

## Implementation Parameters

| Parameter | Typical Value | Effect |
|-----------|--------------|--------|
| Number of queues | 3–8 | More queues = finer grained |
| Quantum per queue | Doubles each level | Long jobs tolerate large quanta |
| Priority boost interval | 1–5 seconds | Prevents starvation, re-evaluates behavior |
| Demotion rule | Full quantum used | Penalizes CPU-hungry processes |

## Python Simulation Skeleton

```python
from collections import deque

NUM_QUEUES = 3
QUANTA = [4, 8, 16]
BOOST_INTERVAL = 20

queues = [deque() for _ in range(NUM_QUEUES)]
clock = 0
boost_timer = 0

def schedule():
    for q in range(NUM_QUEUES):
        if queues[q]:
            return q, queues[q].popleft()
    return None, None

def run(proc, queue_level):
    global clock, boost_timer
    quantum = QUANTA[queue_level]
    run_time = min(proc.remaining, quantum)
    proc.remaining -= run_time
    clock += run_time
    boost_timer += run_time

    if proc.remaining > 0:
        next_q = min(queue_level + 1, NUM_QUEUES - 1)
        queues[next_q].append(proc)   # demote
    # else: process finished

    if boost_timer >= BOOST_INTERVAL:
        boost_timer = 0
        for q in range(1, NUM_QUEUES):
            queues[0].extend(queues[q])
            queues[q].clear()
```

## Gaming the MLFQ

A cunning process can issue a spurious I/O call just before its quantum expires to avoid demotion. Real OS implementations counter this by:

- Tracking **total CPU usage** over a window, not just the current burst.
- Measuring **I/O request frequency** — too-frequent short I/Os from a CPU-bound process trigger throttling.
- Accounting CPU time **across all quanta** at a given level before promotion/demotion.

## Where MLFQ Lives Today

- **Linux:** The O(1) scheduler used MLFQ-like active/expired arrays. CFS replaced it but some realtime and batch queues still use MLFQ concepts.
- **Windows:** The thread dispatcher uses 32 priority levels with MLFQ-inspired quantum stretching and shrinking.
- **FreeBSD:** ULE scheduler explicitly implements multilevel feedback with priority decay.

## Key Tradeoffs vs Other Algorithms

| Algorithm | Needs burst estimate? | Prevents starvation? | Adapts to behavior? |
|---|---|---|---|
| SJF | Yes | No | No |
| RR | No | Yes | No |
| Priority | No | No | No |
| **MLFQ** | **No** | **Yes (with boost)** | **Yes** |

MLFQ is the closest to a general-purpose optimal scheduler without oracle knowledge.
