# Dynamic Branch Prediction Basics

Dynamic branch prediction observes actual branch behavior at runtime and uses that history to make future predictions. Instead of committing to a fixed rule, the hardware learns from what the program has done and adapts its predictions accordingly.

This is the foundation of every modern high-performance processor's branch unit.

## Core Idea: Branch History Table

The fundamental data structure is the **Branch History Table (BHT)**, sometimes called the **Pattern History Table (PHT)**. It is a small, fast SRAM array indexed by bits from the branch's PC. Each entry holds a **prediction bit** (or a small counter) that the hardware reads at fetch time and updates when the branch resolves.

```
   Fetch stage                 Execute stage
   ----------                  -------------
PC → [index bits] → BHT       branch outcome (T/NT)
                     ↓                ↓
                 prediction ──── update entry
```

## The Predict-Then-Verify Loop

1. **Fetch:** Read the BHT entry for the current PC. Predict taken or not-taken.
2. **Speculate:** Continue fetching along the predicted path.
3. **Execute:** Resolve the actual branch outcome.
4. **Correct or flush:**
   - If prediction was correct: no penalty, retire speculatively fetched instructions.
   - If prediction was wrong: flush the pipeline, redirect the PC, update the BHT.

## Indexing the BHT

The simplest indexing scheme uses the **low-order bits of the branch PC**:

```
BHT index = PC[k:2]   (k bits, ignoring the 2 byte-offset bits)
```

A BHT with 2^k entries uses k PC bits to select an entry. This means **two different branches** can map to the same entry — called **aliasing**. Aliasing causes one branch's history to corrupt another's prediction.

Larger tables reduce aliasing but cost more area and power. A typical modern predictor uses 4 KB–64 KB of state.

## Why Dynamic Prediction Outperforms Static

| Property              | Static  | Dynamic |
|-----------------------|---------|---------|
| Uses runtime history  | No      | Yes     |
| Adapts to input data  | No      | Yes     |
| Hardware cost         | None    | Moderate|
| Accuracy (typical)    | 65-75%  | 93-99%  |

A dynamic predictor can recognize that a branch is taken 99% of the time for *this particular input*, even if the compiler had no idea. For pointer-chasing loops, recursive calls, and data-driven conditionals, dynamic prediction is decisive.

## Important Terminology

| Term | Meaning |
|------|---------|
| **Prediction** | The guess made at fetch time |
| **Resolution** | When the actual outcome is known (Execute stage) |
| **Misprediction** | Prediction != actual outcome |
| **Branch penalty** | Cycles flushed on a misprediction |
| **MPKI** | Mispredictions per thousand instructions (lower = better) |

Industry processors today target **< 5 MPKI** on integer workloads. High-performance CPUs like AMD Zen 4 and Apple M-series achieve **< 3 MPKI** on SPEC CPU2017.

## Worked Example: Simple 1-Bit BHT

Assume a 4-entry BHT, all initialized to "not-taken". A branch at PC=0x100 maps to entry 0 (PC bits [3:2] = 00). The branch executes six times with outcomes T, T, T, NT, T, T.

```
Cycle  Outcome  Prediction  Correct?  New entry
-----  -------  ----------  --------  ---------
  1      T         NT          No     → T
  2      T          T          Yes    → T
  3      T          T          Yes    → T
  4     NT          T          No     → NT
  5      T         NT          No     → T
  6      T          T          Yes    → T
```

3 mispredictions out of 6 — the 1-bit predictor thrashes on transitions. The 2-bit saturating counter (next lesson) fixes this specific problem.

## Common Pitfall

A BHT that is too small causes **destructive aliasing**: a branch that is always taken gets its entry overwritten by a different, always-not-taken branch, and both suddenly appear to mispredicted. Always size the BHT to be at least 2^12 entries (4 K entries) in serious designs.

> **Interview answer:** Dynamic branch prediction uses a hardware table indexed by the branch PC to store runtime history and make predictions at fetch time. It adapts to actual program behavior, achieving 93-99% accuracy — far better than static schemes — at the cost of a small SRAM structure and a pipeline flush on misprediction.
