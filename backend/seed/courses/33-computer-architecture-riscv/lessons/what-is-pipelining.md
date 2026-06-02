# What Is Pipelining?

Pipelining is one of the most impactful performance techniques in processor design. Instead of completing one instruction fully before starting the next, a pipelined processor overlaps the execution of multiple instructions — each at a different stage of completion simultaneously.

## The Core Idea

Think of an assembly line in a factory. A car does not wait until the previous car rolls off the line before work begins. Each station works on a different car at the same time. Processors use the same principle.

Without pipelining, if every instruction takes four steps and each step takes one clock cycle, then one instruction completes every four cycles. With pipelining, one instruction completes **every cycle** once the pipeline is full — a four-fold throughput improvement.

## Why Processors Use Pipelining

Modern instructions are complex enough that their execution naturally decomposes into distinct phases:

- **Fetch** — retrieve the instruction from memory
- **Decode** — interpret what the instruction means
- **Execute** — perform the operation in the ALU
- **Memory access** — read or write data memory
- **Write-back** — store the result in a register

These phases use largely independent hardware resources. Pipelining exploits this independence by running them in parallel across consecutive instructions.

## A Simple Illustration

Consider three instructions entering a four-stage pipeline:

```
Cycle:       1    2    3    4    5    6
Inst A:      F    D    E    W
Inst B:           F    D    E    W
Inst C:                F    D    E    W
```

By cycle 4, three instructions are all in-flight at once. Instruction A finishes at cycle 4, B at cycle 5, and C at cycle 6 — one result per cycle after the pipeline fills.

## Pipelining vs Sequential Execution

| Metric | Sequential | Pipelined |
|--------|-----------|-----------|
| Latency (one instruction) | Same | Same |
| Throughput | Low | High |
| Hardware complexity | Low | Higher |
| Clock frequency | Lower | Often higher |

An important point: pipelining does **not** make any single instruction faster. The latency of one instruction stays the same or even increases slightly due to pipeline register overhead. What improves is **throughput** — how many instructions complete per unit time.

## Hazards: The Price of Overlap

Pipelining introduces hazards — situations where the overlap breaks the sequential illusion the programmer expects:

- **Structural hazards** — two instructions need the same hardware at the same time
- **Data hazards** — an instruction needs a result that the previous instruction has not yet produced
- **Control hazards** — a branch changes the program counter before the pipeline knows which instruction to fetch next

These hazards are central topics covered in later lessons. Understanding them is essential for writing efficient code and for hardware design interviews.

## Worked Example: Throughput Calculation

A non-pipelined processor takes 8 ns per instruction. A pipelined version splits the work into 8 stages of 1 ns each (plus negligible register overhead).

- Non-pipelined throughput: 1 instruction / 8 ns = **125 MIPS**
- Pipelined throughput (ideal): 1 instruction / 1 ns = **1000 MIPS**

The pipeline delivers an 8x throughput improvement in the ideal case.

> **Interview answer:** Pipelining overlaps the execution of multiple instructions by dividing instruction processing into independent stages, increasing throughput without reducing per-instruction latency — but it introduces hazards that must be handled by stalling, forwarding, or flushing.
