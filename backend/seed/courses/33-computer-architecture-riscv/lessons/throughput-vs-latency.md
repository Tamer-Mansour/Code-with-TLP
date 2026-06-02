# Throughput vs Latency in Pipelines

Two of the most misunderstood metrics in computer architecture are throughput and latency. Pipelining improves one while leaving the other unchanged — and knowing which is which determines whether a pipeline actually helps your workload.

## Definitions

**Latency** is the time required to complete one instruction from start to finish. In a five-stage pipeline with a 1 ns clock, the latency of a single instruction is 5 ns — it must pass through all five stages regardless of what other instructions are doing.

**Throughput** is the rate at which instructions are completed — how many instructions finish per unit of time. In a fully pipelined processor, one instruction can complete every clock cycle, giving a throughput of 1 instruction per cycle (IPC = 1 for ideal pipelines).

## Why Pipelining Helps Throughput, Not Latency

A non-pipelined processor might complete one instruction every 5 ns. A five-stage pipelined version running at 1 ns per stage completes the same instruction in 5 ns — **identical latency**. In fact, pipeline register overhead slightly increases per-instruction latency.

What changes is that while instruction A is in stage 4, instruction B is in stage 3, instruction C is in stage 2, and instruction D is in stage 1. All four make progress simultaneously. Once the pipeline fills, instructions complete every 1 ns, not every 5 ns.

| Metric | Non-pipelined | 5-stage Pipeline |
|--------|--------------|-----------------|
| Latency (1 instruction) | 5 ns | 5 ns (or slightly more) |
| Throughput (steady state) | 0.2 billion inst/s | 1 billion inst/s |
| CPI (ideal) | 5 | 1 |

## Throughput vs Latency Trade-offs in Practice

Deeper pipelines (more stages) raise the clock frequency by making each stage shorter. But they also increase latency per instruction:

- A 20-stage pipeline running at 4 GHz completes instructions with 20 × 0.25 ns = 5 ns latency
- A 5-stage pipeline running at 1 GHz completes instructions with 5 × 1 ns = 5 ns latency

Same latency, but the deeper pipeline has four times the throughput — if no hazards occur. Hazards (branches, data dependencies) cause pipeline flushes and stalls that are more expensive in deeper pipelines.

This is exactly why Intel's Pentium 4 (Prescott, 31 stages) achieved high clock speeds but poor performance-per-clock — branch mispredictions flushed dozens of pipeline stages.

## CPI and IPC

Two related metrics appear everywhere in architecture discussions:

- **CPI (Cycles Per Instruction)**: ideal = 1, increases with stalls
- **IPC (Instructions Per Cycle)**: ideal = 1, decreases with stalls; IPC = 1/CPI

A stall inserts a "bubble" (a no-op) into the pipeline, wasting one cycle. If 1 in every 5 instructions causes a one-cycle stall:

```
CPI = 1 + (1/5 × 1) = 1.2
IPC = 1 / 1.2 ≈ 0.83
```

## When Does Latency Matter?

For long-running loops with millions of iterations, throughput dominates. But consider:

- **Cache misses** — a single instruction that misses L2 cache stalls the pipeline for 50–200 cycles. Here latency matters enormously.
- **Branch prediction misses** — flushing a deep pipeline has a high latency cost.
- **Interactive applications** — the latency of responding to a user event may matter more than raw throughput.

## Worked Example

A processor has a 4-stage pipeline with a 2 ns clock. A program has 1000 instructions with 50 one-cycle stalls.

```python
# Cycles = N + (k - 1) + stalls
# N = 1000 instructions
# k = 4 stages (pipeline fill cost)
# stalls = 50

cycles = 1000 + (4 - 1) + 50  # = 1053
time   = 1053 * 2e-9            # = 2106 ns ≈ 2.1 µs

# Throughput
ipc    = 1000 / 1053            # ≈ 0.95 IPC
```

> **Interview answer:** Pipelining improves throughput — instructions completed per cycle — but does not reduce per-instruction latency; in fact, pipeline registers add small overhead. The trade-off is that deeper pipelines enable higher clock speeds and throughput but make misprediction and stall penalties more expensive.
