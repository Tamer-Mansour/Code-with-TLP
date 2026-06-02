# What Are Pipeline Hazards?

Pipelining is the technique of overlapping the execution of multiple instructions — while one instruction is in the Execute stage, the next is in Decode, and the one after that is in Fetch. This overlap is what gives modern processors their throughput advantage. But it comes with a fundamental tension: instructions that follow one another in the program can interfere with each other when they share the same hardware resources or depend on results that are not yet ready.

A **pipeline hazard** is any condition that prevents the next instruction in the instruction stream from executing in its designated clock cycle. Hazards are not bugs; they are architectural realities that the processor designer must handle explicitly.

## The Three Classes of Hazards

| Class | Root Cause | Example |
|---|---|---|
| **Structural** | Two instructions need the same hardware resource at the same time | Two instructions both need memory access in the same cycle |
| **Data** | An instruction needs a value that a prior instruction has not yet produced | `add x1, x2, x3` followed immediately by `sub x4, x1, x5` |
| **Control** | The pipeline fetches instructions before it knows whether a branch is taken | A `beq` instruction whose target is unknown until Execute |

## Why Hazards Matter

In an ideal five-stage pipeline (IF → ID → EX → MEM → WB), every instruction completes in one cycle of throughput — the CPI (Cycles Per Instruction) is 1.0. Hazards force the pipeline to either **stall** (insert empty cycles called bubbles) or take corrective action. Each stall cycle adds directly to the CPI.

A processor with a CPI of 1.3 instead of 1.0 loses 23% of its theoretical throughput — at three gigahertz that is hundreds of millions of wasted cycles per second.

## How Processors Respond

Three primary mitigation strategies exist:

- **Stalling (interlocks):** The hardware detects the hazard and pauses the affected instruction until the dependency is resolved. Simple but costly in cycles.
- **Forwarding (bypassing):** The result is routed directly from where it is computed to where it is needed, bypassing the register file entirely. Resolves most data hazards with zero stall penalty.
- **Reordering (scheduling):** Either the compiler or the hardware reorders instructions so that independent instructions fill the slots where a dependent instruction would have stalled.

## The Detection Problem

Before any mitigation can occur, the processor (or compiler) must detect the hazard. Hardware detection is done by the **hazard detection unit**, a combinational circuit that compares source register identifiers of instructions in later pipeline stages against destination register identifiers of instructions in earlier stages.

```asm
# Classic RAW (Read After Write) data hazard
add  x1, x2, x3   # writes x1 in WB (cycle 5)
sub  x4, x1, x5   # reads x1 in ID (cycle 3) — result not ready yet!
```

The hazard detection unit sees that the source register of `sub` (`x1`) matches the destination register of `add` (`x1`) and that `add` has not yet completed its write-back.

## Interview Answer

> "A pipeline hazard is a condition that prevents the next instruction from executing on schedule. The three kinds are structural (resource conflict), data (result not yet available), and control (branch target unknown). Mitigation strategies include stalling, forwarding, and compiler/hardware reordering."
