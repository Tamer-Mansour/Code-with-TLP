# Dispatch Latency and the Ready Queue

Every context switch has a cost. **Dispatch latency** is the overhead introduced by the dispatcher — the time between the scheduler selecting a process and that process actually executing its first instruction. Minimizing it is a core kernel engineering goal.

## What Is Dispatch Latency?

Dispatch latency is the time the dispatcher needs to:

1. **Save** the current process's CPU context (registers, PC, SP, flags) into its PCB.
2. **Load** the next process's saved context from its PCB.
3. **Switch** the memory map (e.g., flush or reload the TLB if address spaces differ).
4. **Return to user mode** via a privileged instruction (e.g., `iret` on x86, `eret` on ARM).

```
|  Running P1  | dispatch latency |  Running P2  |
              ^                  ^
         preemption          first instruction of P2
```

The latency "gap" is pure overhead — no useful work happens during it. On modern hardware it ranges from a few hundred nanoseconds (same address space, hot TLB) to several microseconds (different address spaces, cold TLB).

## What Contributes to Dispatch Latency?

| Source                    | Approximate Cost       |
|---------------------------|------------------------|
| Register save/restore     | ~10–50 ns              |
| TLB flush (address space change) | ~100–1000 ns    |
| Cache pollution (cold cache after switch) | amortized, ~µs |
| Kernel locking (spinlock on ready queue) | ~10–100 ns    |

Cache pollution is often the dominant hidden cost. After a switch, the new process's working set is cold in L1/L2 cache and must be refetched from RAM, causing a burst of cache misses.

## The Ready Queue Structure

The **ready queue** holds all processes in the READY state, waiting for CPU time. Its internal structure varies by scheduling algorithm:

| Algorithm       | Ready Queue Data Structure     |
|-----------------|-------------------------------|
| FCFS            | FIFO linked list               |
| SJF (non-preemptive) | Min-heap by burst length  |
| Priority        | Priority queue / sorted list   |
| Round Robin     | Circular FIFO queue            |
| Linux CFS       | Red-black tree (key = virtual runtime) |
| Multi-level feedback | Array of FIFO queues      |

```c
// Simplified ready queue operations
void enqueue_ready(struct pcb *p) {
    p->state = READY;
    list_add_tail(&p->sched_node, &ready_queue);
}

struct pcb *dequeue_next(void) {
    // FCFS: take head
    return list_first_entry(&ready_queue, struct pcb, sched_node);
}
```

## Dispatch Latency and Real-Time Systems

Real-time systems have the strictest requirements on dispatch latency. A hard real-time OS guarantees that a high-priority task will receive the CPU within a bounded time after it becomes ready. This bound is typically in the range of tens of microseconds for OSes like VxWorks or Zephyr.

For general-purpose OSes like Linux, dispatch latency is probabilistic and depends on:
- Whether kernel preemption is enabled (`CONFIG_PREEMPT`)
- The depth of kernel lock nesting at the moment of preemption
- Hardware interrupt load

```bash
# Measure scheduling latency on Linux:
cyclictest --mlockall -t1 -p99 -n -i100 -l10000
# Reports min/avg/max latency in microseconds
```

## Minimizing Dispatch Latency

Kernel engineers use several techniques:

- **Thread Local Storage (TLS) / per-CPU data** — avoids cross-CPU locking.
- **Lazy TLB flushing** — if two threads share the same address space, TLB does not need flushing.
- **ASID (Address Space Identifier)** tags on ARM and RISC-V — avoids full TLB flush on context switch between different address spaces.
- **Kernel preemption points** — coarse-grain locks held only where necessary, releasing preemption as soon as safe.

## Common Pitfalls

- Treating context switch cost as zero in theoretical analyses. In practice, frequent context switches (very small time quanta) can waste 10–30% of CPU time on overhead alone.
- Conflating dispatch latency with scheduling overhead. Scheduling (choosing who runs next) and dispatching (performing the switch) are separate costs. On complex schedulers like CFS, the scheduling decision itself can touch the red-black tree and cost extra cycles.
- Ignoring TLB effects. Switching between processes in the same memory map (e.g., threads) is far cheaper than switching between processes with different virtual address spaces.

## Interview Answer

> "Dispatch latency is the overhead between the scheduler selecting a process and that process executing its first instruction. It includes saving/restoring registers, switching address spaces (TLB flush), and returning to user mode — typically hundreds of nanoseconds to a few microseconds on modern hardware."
