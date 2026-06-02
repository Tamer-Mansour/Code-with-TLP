# Why Branches Are Expensive

Modern CPUs do not execute one instruction and wait for it to finish before fetching the next. Instead, the pipeline overlaps many instructions simultaneously — fetch, decode, execute, memory access, and write-back all happen at the same time across different instructions. This overlap is what gives pipelined processors their speed.

Branches shatter that overlap.

## The Pipeline Hazard

A conditional branch — `beq`, `bne`, `blt` in RISC-V, or any `jz`/`jne` in x86 — cannot be resolved until the ALU evaluates the condition, which happens in the **Execute** stage. By that time, the pipeline has already fetched 2–3 more instructions that might be from the wrong path.

When the processor discovers it fetched the wrong instructions, it must:

1. **Flush** the incorrectly fetched instructions (turn them into `nop` bubbles).
2. **Redirect** the program counter to the correct target.
3. **Re-fetch** from the correct address.

Every flushed instruction is wasted work. In a classic 5-stage pipeline, a branch taken late costs **2 cycles** of wasted fetch bandwidth — one bubble per stage between fetch and the stage that resolves the branch.

## Branch Penalty Formula

```
Branch Penalty (cycles) = (Stage that resolves branch) - (Fetch stage)
```

For a 5-stage RISC-V pipeline where the branch resolves in Execute (stage 3):

```
Penalty = 3 - 1 = 2 cycles wasted per mispredicted branch
```

Deeper pipelines (modern out-of-order cores have 14–20 stages) push this penalty to **15–20 cycles**.

## How Often Do Branches Occur?

In typical C programs:

| Code pattern        | Branch frequency |
|---------------------|-----------------|
| Integer benchmarks  | ~15-25% of all instructions |
| Loop-heavy code     | Can exceed 30% |
| Linked-list traversal | Near 50% |

With a 20% branch rate and a 2-cycle penalty on every branch, an ideal CPI of 1.0 becomes:

```
Effective CPI = 1.0 + (0.20 × 2) = 1.4
```

That is a 40% slowdown even in a shallow pipeline. In a deep modern pipeline with a 15-cycle penalty, the degradation is catastrophic without prediction.

## The Three Naive Options

Processors historically used one of three approaches before sophisticated prediction existed:

- **Stall (freeze the pipeline):** Safe but slow. Insert bubbles until the branch resolves.
- **Predict not-taken:** Always fetch sequentially. Flush and redirect if the branch is actually taken.
- **Predict taken:** Always jump to the target. Flush if the branch is actually not-taken.

Both static predictions are wrong roughly 30–40% of the time for arbitrary code. That remaining misprediction rate is what motivates the entire field of branch prediction.

## Worked Example: Loop Overhead

Consider this C loop:

```c
int sum = 0;
for (int i = 0; i < 1000; i++) {
    sum += array[i];
}
```

The `beq` (or `bne`) at the bottom of the loop body executes **1001 times** — 1000 times it is taken (loop back), once it falls through. A "predict not-taken" strategy is wrong 1000 out of 1001 times — paying the full penalty almost every iteration.

A "predict taken" strategy is correct 1000 out of 1001 times — near perfect for this pattern, which is why early compilers placed the loop body such that the backward branch was the common case.

## Key Takeaway

> **Interview answer:** A branch forces the CPU to guess which instructions come next. A wrong guess causes a pipeline flush — the deeper the pipeline, the more cycles are wasted. This penalty, multiplied by branch frequency, makes branch misprediction one of the dominant performance bottlenecks in modern processors.
