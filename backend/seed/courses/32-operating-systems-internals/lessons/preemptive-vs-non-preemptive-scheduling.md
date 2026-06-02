# Preemptive vs Non-Preemptive Scheduling

One of the most fundamental design axes in CPU scheduling is whether the OS can forcibly remove a running process from the CPU before it voluntarily yields. This distinction shapes every scheduling algorithm.

## Non-Preemptive Scheduling

In a **non-preemptive** (cooperative) scheduler, once a process is given the CPU, it keeps the CPU until it either:

1. Terminates, or
2. Voluntarily blocks on I/O or a system call.

The scheduler only runs at these two transition points — there is no "time's up" interrupt.

**Advantages:**
- Simple to implement — no timer interrupt or forced context switch.
- No mid-computation state corruption risk in naive kernels.
- Lower context-switch overhead (switches happen less often).

**Disadvantages:**
- A CPU-bound process can monopolize the CPU, starving interactive tasks.
- Poor average response time for I/O-bound and interactive processes.
- A buggy or malicious process can lock out the entire system.

**Historical use:** Windows 3.x used cooperative multitasking. One frozen application froze the entire desktop.

```
Timeline (non-preemptive, P1 gets CPU first):
P1 runs for its entire 10ms burst...
|---------- P1 ----------|--- P2 ---|-- P3 --|
0                        10        14       18
P2 and P3 must wait for P1 to finish — even if P2 was interactive.
```

## Preemptive Scheduling

In a **preemptive** scheduler, the OS can interrupt a running process at any time and switch to another process. The typical trigger is a **timer interrupt** (hardware timer fires every quantum, e.g., 10 ms), though higher-priority processes becoming ready can also trigger a preemption.

**Advantages:**
- Fair CPU sharing among processes.
- Better response time for interactive / high-priority tasks.
- A runaway process cannot monopolize the CPU.

**Disadvantages:**
- Higher overhead — context switches happen more frequently.
- Race conditions in kernel code become possible (shared data structures may be partially updated when preemption occurs — requires spinlocks or disabling interrupts).
- Requires hardware timer support.

**Used by:** Linux, Windows NT+, macOS — all modern general-purpose OSes.

```c
// Kernel timer interrupt handler (simplified)
void timer_interrupt_handler(void) {
    current->remaining_quantum--;
    if (current->remaining_quantum == 0) {
        current->state = READY;
        enqueue(ready_queue, current);
        schedule();   // pick next process
    }
}
```

## Comparison Table

| Property              | Non-Preemptive         | Preemptive              |
|-----------------------|------------------------|-------------------------|
| CPU release trigger   | Voluntary only         | Voluntary OR timer/priority |
| Response time         | Poor (can be high)     | Good                    |
| Throughput            | Depends on workload    | Generally better        |
| Implementation        | Simple                 | Complex (locking needed)|
| Starvation risk       | High for short tasks   | Managed by policy       |
| OS examples           | Early Windows, DOS     | Linux, Windows NT+, macOS |

## The Kernel Re-entrancy Problem

Preemption introduces a subtle danger: what if the scheduler preempts a process while the kernel itself is executing on behalf of that process (e.g., inside a system call)? Early UNIX kernels were **non-preemptible in kernel mode** — a process could not be evicted while running in the kernel. Modern kernels (Linux 2.6+, with CONFIG_PREEMPT) allow preemption even inside the kernel, protected by fine-grained spinlocks.

```
Process state machine — preemption adds a new transition:
READY → RUNNING  (scheduler dispatches)
RUNNING → READY  (preemption by timer or higher-priority process)  ← NEW
RUNNING → BLOCKED (voluntary I/O wait)
BLOCKED → READY  (I/O complete)
```

## Choosing Between Them

- **Batch systems** with long-running jobs and no interactivity can use non-preemptive scheduling safely — FCFS or SJF are common.
- **Interactive systems** (desktops, web servers, real-time systems) require preemptive scheduling to maintain responsiveness.
- **Real-time OSes** use preemptive schedulers with strict priority rules to meet deadlines.

## Common Pitfalls

- Thinking non-preemptive means the OS cannot multitask. It can — it just waits for the current process to yield before switching.
- Forgetting that I/O blocking is a yield. Non-preemptive schedulers still switch on I/O waits, so I/O-bound workloads still get interleaved.
- Assuming preemption is always better. For tightly coupled batch jobs, the extra context-switch overhead of preemption may reduce throughput.

## Interview Answer

> "Non-preemptive scheduling lets a process keep the CPU until it voluntarily yields; preemptive scheduling allows the OS to forcibly evict a running process via a timer interrupt. All modern general-purpose OSes use preemptive scheduling to ensure responsiveness and fairness."
