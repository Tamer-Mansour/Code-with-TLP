# Why Multicore? The End of Frequency Scaling

For decades, CPU designers followed a simple playbook: shrink transistors, raise clock frequency, and software runs faster for free. That era ended around 2004. Understanding why reveals one of the most consequential architectural pivots in computing history.

## Dennard Scaling and Its Collapse

**Dennard scaling** (1974) stated that as transistors shrink, power density stays constant — you can pack more transistors and run them faster without increasing total chip power. This held remarkably well for 30 years.

The relationship breaks down because:

- **Leakage current** grows as gate oxide thins below ~5 nm; transistors leak even when "off".
- **Threshold voltage** cannot scale as fast as supply voltage, so the power-to-performance ratio worsens.
- **Heat dissipation** limits: a chip cooled by air can safely dissipate roughly 100–150 W. Beyond that, reliability collapses.

The result is the **Power Wall**: clock frequencies stalled near 3–5 GHz around 2004 and have barely moved since.

## The Memory Wall

A second wall had already been building: DRAM latency improved ~7% per year while CPU speed improved ~55% per year through the 1990s. The growing gap between processor speed and memory speed meant cores spent more and more time waiting — a phenomenon called the **memory wall**.

Caches mitigated this, but the fundamental mismatch remained.

## ILP Limits — The ILP Wall

Designers tried to extract more work from each clock cycle via **Instruction-Level Parallelism (ILP)**:

- Out-of-order execution
- Superscalar dispatch (multiple instructions per cycle)
- Speculative execution and branch prediction

By the early 2000s, returns were diminishing. Wider issue windows hit diminishing returns in available ILP, and the control logic consumed increasing chip area and power.

## Multicore as the Answer

With frequency scaling dead and ILP mostly exhausted, the industry turned to **Thread-Level Parallelism (TLP)**:

> Instead of one fast core, put multiple moderate cores on the same die and divide the work.

| Approach | Frequency | Cores | Performance | Power |
|---|---|---|---|---|
| Single fast core (2004) | 4 GHz | 1 | 1x | 100 W |
| Dual moderate cores | 3 GHz | 2 | ~1.5–1.8x | ~80 W |
| Many small cores | 2 GHz | 8 | up to 4x (parallel) | ~100 W |

The key insight: doubling frequency roughly doubles power (P ∝ f·V²), but doubling cores at lower voltage can deliver more throughput for the same wattage — if software can exploit the parallelism.

## Amdahl's Law — The Catch

Not all workloads parallelize equally. **Amdahl's Law** quantifies the limit:

```
Speedup = 1 / (S + (1-S)/N)
```

Where `S` is the serial fraction of the program and `N` is the number of cores.

- If 5% of the code is serial, max speedup is 20x regardless of core count.
- This motivates minimizing serial bottlenecks (locks, I/O, startup costs).

## What Changed in Hardware and Software

- **Hardware**: chip designers added coherent cache hierarchies, interconnects (rings, meshes), and hardware memory ordering support.
- **OS**: schedulers became NUMA-aware; thread affinity APIs emerged.
- **Languages/runtimes**: Java, C#, Go, and Rust added concurrency primitives; compilers gained auto-vectorization and parallelization passes.

## Interview Answer

> "Dennard scaling broke down around 2004 because leakage current and heat density prevented further clock frequency increases. With the power wall and ILP limits, the industry shifted to multicore processors to exploit thread-level parallelism. The tradeoff is that software must be written to take advantage of multiple cores, and Amdahl's Law limits the achievable speedup based on the serial fraction of a program."
