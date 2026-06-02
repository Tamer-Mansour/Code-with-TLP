# SMP vs NUMA Architectures

When multiple processors share a system, how they connect to memory defines the entire performance profile of the machine. Two dominant models emerged: **Symmetric Multiprocessing (SMP)** and **Non-Uniform Memory Access (NUMA)**.

## Symmetric Multiprocessing (SMP)

In a classic SMP system, every processor sees a single, flat address space and takes the same time to access any byte of RAM. The design is "symmetric" because no processor has a privileged view of memory.

```
CPU0   CPU1   CPU2   CPU3
 |      |      |      |
 +------+------+------+
          |
      Shared Bus / Crossbar
          |
        DRAM (single bank or interleaved)
```

**Characteristics:**

- Simple programming model — threads can run on any core transparently.
- The shared interconnect (historically a front-side bus, now a crossbar or ring) becomes a bottleneck as core count grows.
- Scales well to 8–16 processors; beyond that, the bus saturates.

**Practical example — Linux SMP:** The kernel's spinlocks and per-CPU data structures were designed for this model. All processors share one interrupt controller and one global scheduler runqueue (though modern Linux uses per-core runqueues).

## Non-Uniform Memory Access (NUMA)

NUMA partitions memory into **nodes**. Each node has local DRAM and one or more processor sockets attached to it. Processors can still address all memory, but local accesses are faster than remote ones.

```
  Node 0                     Node 1
+----------+  QPI/Infinity  +----------+
| CPU0 CPU1 |<------------->| CPU2 CPU3|
| L3 cache  |               | L3 cache |
| DRAM0     |               | DRAM1    |
+----------+                +----------+
```

**Characteristics:**

- Local memory latency: ~70–100 ns. Remote memory latency: ~140–200 ns (cross-socket hop).
- Scales to hundreds of sockets — large servers (AMD EPYC, Intel Xeon) use 2–8 NUMA nodes.
- NUMA-aware placement of threads and data is critical for performance.

### NUMA Ratios

The **NUMA ratio** is remote latency / local latency. A ratio of 2x means cross-node access costs double. A 4-socket server might have ratios up to 4–5x for the most distant nodes.

## Key Differences at a Glance

| Property | SMP | NUMA |
|---|---|---|
| Memory latency | Uniform | Non-uniform (local vs remote) |
| Scalability | ~8–16 processors | Hundreds of cores |
| Programming complexity | Low | Higher (NUMA-aware needed) |
| Hardware cost | Moderate (shared bus) | Higher (node interconnects) |
| Example hardware | Intel dual-core desktop | AMD EPYC multi-socket server |

## NUMA in Practice

**OS scheduling:** Linux `numactl` and `taskset` pin threads to nodes. The kernel's NUMA balancing subsystem migrates pages toward the node that accesses them most.

**Memory allocation:** `numa_alloc_local()` allocates pages on the calling thread's NUMA node. Allocating on the wrong node is a common performance bug.

```c
#include <numa.h>

// Allocate 4 MB on the local NUMA node
void *buf = numa_alloc_local(4 * 1024 * 1024);

// Bind this thread to node 0
struct bitmask *mask = numa_bitmask_alloc(numa_num_possible_nodes());
numa_bitmask_setbit(mask, 0);
numa_bind(mask);
```

**Common pitfall:** Allocating memory on thread A's node, then processing it exclusively on thread B (a different node) — all accesses become remote. This often shows up as unexpectedly high memory latency in profiling tools like `perf stat -e cache-misses`.

## Hybrid Topologies

Modern processors blur the boundary:

- **AMD EPYC (Zen 3+):** A single socket contains multiple chiplets, each acting like a mini-NUMA node with its own L3 cache and local memory controller.
- **Apple M-series:** Unified memory architecture with a single flat pool but bandwidth-asymmetric access for CPU vs GPU clusters.
- **Intel Alder Lake:** P-cores and E-cores have different cache topologies on the same die.

## Interview Answer

> "SMP means every processor has equal-latency access to all memory, making it simple to program but limited in scalability due to shared-bus bottlenecks. NUMA splits memory into nodes — each processor has fast local memory and slower remote memory — allowing much larger scale. The tradeoff is that NUMA-unaware code can suffer 2–5x memory latency penalties on cross-node accesses, so OS schedulers and applications must place threads close to their data."
