# Round Robin Scheduling and the Time Quantum

Round Robin (RR) is the de-facto scheduling algorithm for time-sharing systems. It extends FCFS with **preemption via a fixed time slice** called the **time quantum** (or time slice), so every process gets a fair turn on the CPU and no single process can monopolize it.

## How Round Robin Works

1. Processes are held in a circular FIFO ready queue.
2. The scheduler picks the process at the head and lets it run for **at most one quantum**.
3. If the process finishes or blocks on I/O before the quantum expires, the CPU is released voluntarily.
4. If the quantum expires and the process is still running, a **timer interrupt** fires, the process is preempted, added to the tail of the queue, and the next process runs.
5. Repeat.

```
Ready queue (circular):  [P1] → [P2] → [P3] → (back to P1)
Quantum = 4 ms

Timeline:
| P1(0-4) | P2(4-8) | P3(8-12) | P1(12-16) | P2(16-20) | P3(20-24) | ...
```

## Worked Example

| Process | Arrival Time | Burst Time |
|---------|-------------|------------|
| P1      | 0           | 10 ms      |
| P2      | 0           | 4 ms       |
| P3      | 0           | 6 ms       |

Quantum = 4 ms.

```
| P1(0-4) | P2(4-8) | P3(8-12) | P1(12-16) | P3(16-18) | P1(18-20) |
0         4        8          12           16           18           20
```

Step through:
- t=0: Dispatch P1 (runs 4ms, remaining = 6).
- t=4: Dispatch P2 (runs 4ms, **finishes**).
- t=8: Dispatch P3 (runs 4ms, remaining = 2).
- t=12: Dispatch P1 (runs 4ms, remaining = 2).
- t=16: Dispatch P3 (runs 2ms, **finishes**).
- t=18: Dispatch P1 (runs 2ms, **finishes**).

**Completion times:** P1 = 20, P2 = 8, P3 = 18.

**Waiting times** (completion − arrival − burst):
- P1 = 20 − 0 − 10 = 10 ms
- P2 = 8 − 0 − 4 = 4 ms
- P3 = 18 − 0 − 6 = 12 ms

**Average waiting time:** (10 + 4 + 12) / 3 = **8.67 ms**

**Average response time** (first CPU access − arrival):
- P1 = 0, P2 = 4, P3 = 8 → average = **4 ms**

Response time is often better with RR than with SJF, making RR the preferred choice for interactive workloads.

## The Role of the Timer Interrupt

The kernel programs a hardware timer before dispatching each process. When the timer fires:

```
Hardware timer fires
    → CPU raises interrupt
    → Kernel preempts current process (saves registers to PCB)
    → Scheduler picks next process from head of queue
    → Kernel restores registers from new process's PCB
    → CPU resumes new process
```

This **context switch** has a real cost — saving and restoring the process control block (PCB) typically takes 1–10 microseconds on modern hardware.

## Quantum vs. Context Switch Overhead

```
Effective CPU utilization = quantum / (quantum + context_switch_time)
```

If quantum = 1 ms and context switch = 0.1 ms:
- Utilization = 1 / 1.1 ≈ 91%

If quantum = 0.01 ms and context switch = 0.1 ms:
- Utilization = 0.01 / 0.11 ≈ 9% — most time is wasted on overhead!

## Starvation and Fairness

Round Robin does **not** starve processes. Because every process returns to the tail after each quantum, all n processes get CPU time at least once every n × quantum milliseconds. This bound makes RR the standard for interactive and real-time soft systems.

## Key Properties

| Property             | Round Robin                   |
|----------------------|-------------------------------|
| Preemptive           | Yes (timer-based)             |
| Starvation possible  | No                            |
| Response time        | Bounded by (n−1) × quantum    |
| Optimal avg wait?    | No (SJF beats it)             |
| Best for             | Interactive, time-sharing OS  |
| Tunable knob         | Time quantum                  |

## Common Pitfalls

- **Treating RR as fair for I/O-bound processes:** An I/O-bound process rarely uses its full quantum, so it gets less CPU time but also voluntarily releases, causing I/O-bound jobs to be starved relative to CPU-bound jobs in some implementations.
- **Ignoring context switch cost:** A very small quantum makes the system look responsive but wastes CPU on overhead.
- **Confusing response time with waiting time:** RR excels at response time but average waiting time can be worse than SJF.

> **Interview answer:** "Round Robin gives each process a fixed time quantum in cyclic order. It prevents starvation and bounds response time to (n−1)×quantum, making it ideal for interactive systems. The trade-off is that too small a quantum inflates context-switch overhead, while too large a quantum degrades toward FCFS."
