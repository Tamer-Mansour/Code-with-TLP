# Multilevel Queue Scheduling

## Motivation

A single ready queue forces every process to compete under one policy. In practice, processes fall into well-known classes with very different scheduling needs:

- **System/kernel processes** — need near-instant response; latency is unacceptable.
- **Interactive (foreground) processes** — user is waiting; must feel responsive.
- **Batch (background) processes** — throughput matters; latency is acceptable.

**Multilevel queue scheduling** creates a separate queue for each class and applies the most appropriate algorithm to each one.

## Structure

```
Priority Level 0 (highest)
┌─────────────────────────────┐
│  System Processes           │ ← Round-Robin, small quantum
└─────────────────────────────┘
          ↓ (only if Level 0 is empty)
Priority Level 1
┌─────────────────────────────┐
│  Interactive Processes      │ ← Round-Robin, medium quantum
└─────────────────────────────┘
          ↓ (only if Level 1 is empty)
Priority Level 2 (lowest)
┌─────────────────────────────┐
│  Batch Processes            │ ← FCFS (no preemption needed)
└─────────────────────────────┘
```

The scheduler always services the highest non-empty queue before looking at lower queues.

## Queue Assignment

Each process is **permanently assigned** to one queue at creation based on its type. This is the key difference from multilevel *feedback* queues — in the base multilevel scheme, a process cannot move between queues.

Assignment criteria:

| Queue | Assignment Basis | Examples |
|-------|-----------------|---------|
| System | Created by OS | `kthreadd`, interrupt handlers |
| Interactive | Has a controlling terminal (tty) | shells, text editors, browsers |
| Batch | No tty, long-running | compilers, ML training, backups |

## Scheduling Within Each Queue

Each queue can run its own independent algorithm:

```
System queue      → Preemptive RR, quantum = 5 ms
Interactive queue → Preemptive RR, quantum = 20 ms
Batch queue       → FCFS or non-preemptive SJF
```

This flexibility is the main advantage over a flat priority scheme — you can tune each class independently.

## Between-Queue Scheduling

The simplest policy is **strict priority**: never service a lower queue while a higher queue has ready processes. This is efficient but can starve lower queues entirely.

A balanced alternative allocates **CPU time percentages** across queues:

```
System queue      → 10% of CPU time
Interactive queue → 60% of CPU time
Batch queue       → 30% of CPU time
```

The OS uses a timer wheel or weighted counter to enforce these percentages.

## Implementation Sketch (C-like pseudocode)

```c
#define NUM_QUEUES 3
Queue queues[NUM_QUEUES];   // 0 = highest priority

Process* select_next() {
    for (int q = 0; q < NUM_QUEUES; q++) {
        if (!is_empty(&queues[q])) {
            return dequeue(&queues[q]);
        }
    }
    return NULL;  // CPU idle
}

void admit_process(Process* p) {
    int q = classify(p);   // returns 0, 1, or 2
    enqueue(&queues[q], p);
}
```

## Advantages and Limitations

**Advantages:**
- Simple to understand and implement.
- Policy tuned per class without affecting other classes.
- Predictable for high-priority processes.

**Limitations:**
- **No migration** — a batch job that becomes interactive (e.g., a script waiting for user input) stays in the wrong queue.
- **Starvation** — under load, the batch queue may never run.
- **Rigid classification** — real workloads are messier than three clean categories.

These limitations motivate the **multilevel feedback queue**, which adds migration between queues.

## Worked Example

Three processes arrive at t=0:

| PID | Queue | Burst |
|-----|-------|-------|
| S1  | System (0) | 8 ms |
| I1  | Interactive (1) | 20 ms |
| B1  | Batch (2) | 50 ms |

With strict priority and RR quantum=8 ms for System:

- t=0–8: S1 runs (finishes).
- t=8–28: I1 runs (finishes).
- t=28–78: B1 runs (finishes).

All queues drained. B1's wait of 28 ms is acceptable because its nature is batch.

> **Interview answer:** Multilevel queue scheduling partitions processes into fixed classes, each with its own scheduling algorithm, and always prefers the highest non-empty class — simple and efficient, but processes cannot migrate between queues.
