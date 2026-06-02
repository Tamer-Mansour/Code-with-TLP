# First-Come First-Served (FCFS) and the Convoy Effect

First-Come First-Served (FCFS) is the simplest CPU scheduling algorithm: processes are dispatched in the exact order they arrive in the ready queue. There is no preemption — a process holds the CPU until it either terminates or blocks on I/O.

## How FCFS Works

1. Each arriving process is appended to the tail of a FIFO ready queue.
2. The scheduler always picks the process at the head of the queue.
3. Once a process starts, it runs to completion (or until an I/O block).
4. After a process finishes or blocks, the next process at the head is dispatched.

No priority. No preemption. First in, first out.

## Worked Example

| Process | Arrival Time | Burst Time |
|---------|-------------|------------|
| P1      | 0           | 24 ms      |
| P2      | 1           | 3 ms       |
| P3      | 2           | 3 ms       |

Gantt chart:

```
| P1 (0–24) | P2 (24–27) | P3 (27–30) |
0          24          27          30
```

- **Waiting time:** P1 = 0, P2 = 23, P3 = 25
- **Average waiting time:** (0 + 23 + 25) / 3 = **16 ms**

If the order were P2, P3, P1:

```
| P2 (0–3) | P3 (3–6) | P1 (6–30) |
0          3          6          30
```

- **Waiting time:** P1 = 6, P2 = 0, P3 = 3
- **Average waiting time:** (6 + 0 + 3) / 3 = **3 ms**

Same workload, five times better average wait just by reordering. This sensitivity to arrival order is the core weakness of FCFS.

## The Convoy Effect

The convoy effect occurs when one long CPU-bound process holds the CPU while many shorter processes queue behind it, just like a slow truck causing a traffic jam on a single-lane road.

**Why it matters:**

- Short I/O-bound processes that need the CPU for only a few milliseconds must wait behind a process that runs for hundreds of milliseconds.
- While the long job runs, I/O devices sit idle because their associated processes cannot complete their tiny CPU bursts and re-issue I/O requests.
- Overall system throughput drops even though the CPU appears busy.

```
Ready queue:  [P_long (100ms)] [P_short1 (2ms)] [P_short2 (2ms)] [P_short3 (2ms)]

Timeline:
0       100      102      104      106
|  P_long  | P_s1 | P_s2 | P_s3 |
              ^--- each short job waited ~100ms for no reason
```

## Key Properties

| Property             | FCFS                     |
|----------------------|--------------------------|
| Preemptive           | No                       |
| Starvation possible  | No (every job eventually runs) |
| Overhead             | Very low (simple queue)  |
| Turnaround fairness  | Poor when burst times vary |
| Best case            | All jobs arrive with similar burst times |
| Worst case           | Long job arrives first (convoy) |

## Common Pitfalls

- **Assuming FCFS is fair:** It is arrival-order fair, not burst-time fair. Short jobs suffer.
- **Forgetting non-preemption:** A long job cannot be interrupted even if urgent processes arrive.
- **Ignoring I/O:** The convoy effect is worst in mixed workloads where I/O devices starve.

## Where FCFS Is Used

FCFS is used in batch systems where turnaround time matters less than simplicity, in disk I/O queues as a baseline, and in network packet queues (though usually with enhancements). It is rarely used alone in interactive or real-time systems.

> **Interview answer:** "FCFS schedules processes in arrival order with no preemption. Its main flaw is the convoy effect — one long process can block many short ones, inflating average waiting time and starving I/O devices."
