# Speculative Execution and Misprediction Recovery

Branch prediction is useful only if the processor acts on it immediately — fetching, decoding, and even executing instructions *before* knowing whether the prediction is correct. This is **speculative execution**: doing work that might need to be undone.

Making speculation safe requires careful hardware support for rollback.

## What "Speculation" Means

Without speculation, the pipeline stalls at every branch until the outcome is known. With speculation, the pipeline keeps running — instructions from the predicted path are fetched, decoded, issued, and may even begin execution. These instructions are called **speculative instructions**.

Speculative instructions are not allowed to:
- **Commit** their results to architectural state (registers, memory).
- **Raise exceptions** that change visible behavior.

They live in temporary hardware buffers until the branch resolves.

## Reorder Buffer (ROB)

The key hardware mechanism is the **Reorder Buffer** — a circular queue that holds every in-flight instruction in program order, regardless of the order in which instructions are actually executed.

```
ROB (head → tail, in program order):
  [ADD r1, r2, r3 | done | result=42]
  [BEQ r1, r4     | done | TAKEN    ]  ← branch resolved here
  [LW  r5, 0(r6)  | done | SPEC     ]  ← speculatively fetched
  [ADDI r7, r5, 1 | exec | SPEC     ]
  [SD  r7, 4(r8)  | fetc | SPEC     ]
```

Instructions complete out of order but **commit in order** from the head of the ROB. An instruction only writes to the architectural register file or memory when it reaches the head of the ROB and all preceding instructions have committed.

## Misprediction Recovery Steps

When the branch resolves and the prediction was **wrong**:

1. **Tag the branch** in the ROB with the correct target PC.
2. **Squash** all instructions that entered the ROB *after* the mispredicted branch — flush them from the ROB, the issue queue, and any execution units.
3. **Restore** the register rename table to the state it was in just before the branch (a checkpoint is often kept per-branch).
4. **Redirect** the fetch unit to the correct PC.
5. **Update** the branch predictor with the actual outcome.

```
Before recovery:      After recovery:
ROB: [...BEQ SPEC SPEC SPEC]   ROB: [...BEQ]
                               Fetch → correct target
```

The recovery penalty is the number of pipeline stages between fetch and the branch-resolve stage — typically 12–20 cycles on a modern out-of-order processor.

## Checkpointing Strategies

| Strategy | How it works | Cost |
|----------|-------------|------|
| **ROB squash** | Walk ROB backward, free entries after branch | Simple, O(N) squash |
| **Register checkpointing** | Save the full rename map at each branch; restore in O(1) | Extra storage per branch |
| **History buffer** | Store old values; undo changes on rollback | Complex but fast |

Most modern processors use a combination: a ROB for ordering, plus a saved rename-map snapshot for O(1) rename restoration.

## Example: Branch Misprediction Timeline

```
Cycle  Stage     Instruction
  1    Fetch     BEQ r1, r2          (predict NOT TAKEN)
  2    Decode    BEQ r1, r2
  3    Issue     BEQ r1, r2 / Fetch  ADD r3, r4, r5   ← speculative
  4    Execute   BEQ → MISPREDICTED  / Decode ADD
  5    Recovery  Squash ADD and all subsequent instructions
  6    Redirect  Fetch from correct target
```

Cycles 3–4 contained work that was thrown away — a 2-cycle penalty in this simplified pipeline.

## Precise Exceptions and Speculation

A critical requirement is that **exceptions are precise**: when an exception occurs, all instructions before the excepting instruction have committed, and no instructions after it have committed. This is guaranteed by the ROB's in-order commit discipline.

Without this property, a speculative `load` that faults before the branch resolves could incorrectly raise a fault for a path that was never supposed to execute.

## Performance Impact

Misprediction cost on modern processors:

| Processor | Pipeline depth | Misprediction penalty |
|-----------|---------------|----------------------|
| RISC-V simple (5-stage) | 5 | 2 cycles |
| Intel Pentium 4 (Netburst) | 31 | ~20 cycles |
| Intel Core (Skylake)       | 14–19 | ~15 cycles |
| ARM Cortex-A76             | ~13 | ~11 cycles |

With a 3% misprediction rate and a 15-cycle penalty, each branch adds `0.03 × 15 = 0.45` cycles on average. This motivates every percentage point of predictor accuracy improvement.

> **Interview answer:** Speculative execution runs instructions past an unresolved branch using a Reorder Buffer that enforces in-order commit. On a misprediction the ROB squashes all instructions after the branch, restores register state from a checkpoint, and redirects fetch — paying a penalty equal to the pipeline stages between fetch and branch resolution.
