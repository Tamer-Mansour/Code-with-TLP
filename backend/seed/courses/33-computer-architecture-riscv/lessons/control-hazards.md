# Control Hazards from Branches

A **control hazard** (also called a branch hazard) occurs when the pipeline cannot determine which instruction to fetch next because a branch instruction has not yet resolved its condition and target address. By the time the pipeline knows whether a branch is taken and where it goes, it has already fetched — and perhaps partially executed — the instructions that follow the branch in memory. Those instructions may be wrong.

## The Problem in a Five-Stage Pipeline

In the standard RISC-V five-stage pipeline, branch decisions are resolved in the **EX stage** (cycle 3 for the first branch instruction). By that time, the pipeline has already fetched the next two instructions (IF in cycles 2 and 3). If the branch is taken, both of those fetched instructions come from the wrong address.

```
Cycle:    1    2    3    4    5    6    7
beq x1,x2,L   IF   ID   EX  MEM   WB
add x3,...          IF   ID  [flush] EX  (wrong — must be squashed)
sub x4,...               IF  [flush] (wrong — must be squashed)
L: and x5,...                 IF   ID   EX  MEM  WB  (correct path)
```

If the branch is taken, the two instructions following the branch in memory are wrong. They must be squashed (flushed from the pipeline) and replaced with bubbles.

## Branch Penalty

The **branch penalty** is the number of pipeline cycles wasted when a taken branch is detected. In the five-stage pipeline with branch resolution in EX:

```
Branch penalty = 2 cycles (when branch is taken)
```

If the branch is not taken, the two fetched instructions happen to be the correct ones and no penalty is incurred.

## Mitigation Strategies

### 1. Assume Not Taken

The simplest approach: always fetch instructions after the branch as if it is not taken. If the branch turns out not to be taken, no penalty. If it is taken, flush the incorrectly fetched instructions (2 cycle penalty).

For branches that are not taken most of the time (e.g., loop exit checks), this is efficient.

### 2. Branch Prediction

Modern processors use **branch predictors** — hardware structures that predict the outcome of a branch based on its recent history.

| Predictor | Accuracy | Complexity |
|---|---|---|
| Static "not taken" | ~50–60% | None |
| One-bit predictor | ~85% | Minimal |
| Two-bit saturating counter | ~88–93% | Low |
| Tournament / hybrid | ~95–98% | High |

A mispredicted branch still incurs a penalty (flushing the incorrectly fetched instructions), but accurate prediction makes that penalty rare.

### 3. Delayed Branching

MIPS used this approach: the instruction **immediately after** the branch (the "branch delay slot") is always executed regardless of whether the branch is taken. The compiler fills the delay slot with a useful instruction — often from before the branch.

RISC-V explicitly does not use delayed branches; branches take effect at the branch instruction itself.

### 4. Move Branch Resolution Earlier

If branch resolution can be moved to the **ID stage** instead of EX, the branch penalty drops from 2 cycles to 1 cycle. This requires adding a comparator to the ID stage (for the branch condition) and computing the branch target in ID as well.

### 5. Branch Target Buffer (BTB)

A cache that stores the target address of recently executed branches. On the next encounter, the processor can fetch from the predicted target in the same cycle as the fetch of the branch — zero-cycle overhead when the prediction is correct.

## Worked Example: Loop Overhead

```asm
# Inner loop — branch at bottom
.loop:
    lw   x5, 0(x1)      # load array element
    add  x6, x5, x7     # process
    addi x1, x1, 4      # advance pointer
    addi x2, x2, -1     # decrement counter
    bnez x2, .loop      # branch taken N-1 times, not taken once
```

The `bnez` is taken N-1 times. With a "not taken" prediction and a 2-cycle penalty:

- Total wasted cycles = (N - 1) × 2

For N = 100 iterations, that is 198 wasted cycles out of a loop body of 500 instruction cycles — nearly 40% overhead from branch mispredictions alone.

A two-bit predictor learns quickly that this branch is almost always taken and predicts it correctly after the first iteration, reducing wasted cycles to approximately 2 total.

## Flush vs Squash

Both terms mean the same thing: invalidating instructions in the pipeline by replacing their control signals with NOPs (bubbles). "Flush" is more common when talking about control hazards; "squash" appears frequently in out-of-order processor literature.

## Interview Answer

> "A control hazard occurs because the pipeline fetches instructions after a branch before knowing whether the branch is taken or what its target address is. The penalty is 2 cycles (for a five-stage pipeline with branch resolution in EX) when the branch is taken. Mitigation includes branch prediction, the branch target buffer, moving branch resolution to an earlier stage, and compiler-inserted delay slot instructions."
