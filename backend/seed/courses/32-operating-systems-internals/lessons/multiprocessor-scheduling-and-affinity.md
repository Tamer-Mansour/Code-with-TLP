# Multiprocessor Scheduling and CPU Affinity

## From One CPU to Many

Uniprocessor scheduling is hard; multiprocessor scheduling adds a new dimension of complexity. With N CPUs you have N simultaneous schedulers, shared data structures, cache effects, and NUMA topology to manage. The decisions made here have large impact on both throughput and latency.

## Scheduling Approaches

### Asymmetric Multiprocessing (AMP)
One master CPU runs the OS scheduler and assigns work to all other CPUs. Simple — avoids shared-state races — but the master becomes a bottleneck and single-point-of-failure.

### Symmetric Multiprocessing (SMP)
Every CPU runs its own scheduler and can pull work from a shared or per-CPU ready queue. This is the standard in modern OSes (Linux, Windows, macOS).

```
        Global Queue           Per-CPU Queues (Linux default)
        ┌───────────┐          CPU0: [P3][P7]
[P1][P2][P3][P4][P5]          CPU1: [P1][P5]
        └───────────┘          CPU2: [P4]
  All CPUs compete             CPU3: [P2]
```

Per-CPU queues reduce lock contention but require **load balancing** when queues become uneven.

## Load Balancing

**Push migration:** A kernel thread periodically inspects all CPU queues and migrates tasks from overloaded CPUs to idle ones.

**Pull migration:** An idle CPU steals tasks from the busiest CPU's queue (*work stealing*).

Linux uses both: the scheduler runs `load_balance()` on every tick and also when a CPU goes idle.

```c
// Simplified work-stealing logic (conceptual)
void idle_cpu_steal_work(int idle_cpu) {
    int busiest = find_busiest_cpu();
    if (busiest < 0) return;
    migrate_tasks(busiest, idle_cpu, nr_tasks / 2);
}
```

Migration is not free — it breaks cache warmth and can cause NUMA remote-memory access.

## CPU Affinity

**CPU affinity** (or *processor affinity*) is a hint or hard constraint that a thread should run on a specific CPU or subset of CPUs.

**Why affinity matters:**
- **Cache warmth** — a thread's working set is already in L1/L2 cache on the CPU it last ran. Moving it to another CPU causes cold-cache misses.
- **NUMA locality** — in NUMA systems, memory allocated on node 0 is slower to access from a CPU on node 1. Pinning a thread to the same node as its memory is critical for HPC workloads.
- **Real-time isolation** — isolating a real-time thread to a dedicated CPU prevents interference from OS tasks.

### Setting Affinity in Linux

```c
#include <sched.h>

cpu_set_t mask;
CPU_ZERO(&mask);
CPU_SET(2, &mask);          // pin to CPU 2
CPU_SET(3, &mask);          // also allow CPU 3

sched_setaffinity(0, sizeof(mask), &mask);
```

```bash
# From the command line:
taskset -c 2,3 ./my_program

# Check current affinity:
taskset -p $$
```

### Soft vs Hard Affinity

| Type | Behavior | Linux API |
|------|----------|-----------|
| **Soft affinity** | Scheduler prefers the last CPU; migrates if necessary | Default SMP behavior |
| **Hard affinity** | Thread is restricted to specified CPUs; never migrated out | `sched_setaffinity()`, `taskset` |

## NUMA-Aware Scheduling

Non-Uniform Memory Access (NUMA) systems have multiple memory controllers. Accessing local memory takes ~80 ns; remote NUMA memory can take ~150–300 ns.

```
Node 0: CPU0, CPU1 ←→ Memory Bank 0  (fast)
          ↕ QPI/Infinity Fabric (slow)
Node 1: CPU2, CPU3 ←→ Memory Bank 1  (fast)
```

Linux's scheduler domain hierarchy respects NUMA: it prefers to balance within a NUMA node before balancing across nodes, trading some CPU load evenness for memory locality.

## Processor Groups and Hyperthreading

Modern CPUs expose **logical cores** through hyperthreading (Intel) or SMT (AMD). Two logical cores share one physical core's execution units. Scheduling two CPU-bound threads on sibling logical cores is worse than spreading them to separate physical cores — they compete for the same execution resources.

The Linux scheduler treats SMT siblings as a lower preference during load balancing, preferring idle physical cores first.

## Common Pitfalls

- **Pinning everything** — over-affinity prevents load balancing. Only pin when you have measured cache or NUMA benefit.
- **Ignoring SMT topology** — spreading real-time tasks across physical cores, not just logical cores.
- **Lock contention on the global run queue** — early Linux used one big lock; replaced by per-CPU queues with fine-grained locking.
- **Migration storms** — aggressive load balancing that migrates tasks on every imbalance causes cache thrashing. Hysteresis (only migrate when imbalance exceeds a threshold) is necessary.

> **Interview answer:** Multiprocessor scheduling uses per-CPU queues with push/pull load balancing; CPU affinity pins threads to specific cores to preserve cache warmth and NUMA locality, at the cost of reduced load-balancing flexibility.
