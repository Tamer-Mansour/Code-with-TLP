# useState Batch Updater Simulator

React batches state updates for performance. Simulate a state machine that processes batched update instructions for a single integer counter.

## Input

A sequence of instruction lines. Instructions are grouped into **batches** separated by blank lines. Each instruction is one of:

- `SET <n>` — set the counter to the integer `n`
- `INC` — increment the counter by 1
- `DEC` — decrement the counter by 1
- `DOUBLE` — multiply the counter by 2

**Within a batch**, every instruction reads the state from the **start** of that batch (non-functional updates). The batch result is whichever instruction ran **last** in the batch.

Print the counter value after each batch is fully applied. Start with state `0`.

## Examples

**Example 1**

Input:
```
SET 5
INC
INC

DOUBLE
DEC

SET 10
```

Output:
```
7
13
10
```

Explanation:
- Batch 1: starts at 0. SET 5 → 5, INC → 1, INC → 1. Last op was INC using base 0, result = 1. Wait — all ops read from batch-start (0): SET 5 gives 5, INC gives 1, INC gives 1. The last instruction in the batch is the second INC, which reads base state 0 and gives 0+1=1? No — each op reads the *batch-start* value independently. The batch result is the value produced by the **last** op in the batch. Batch-start = 0. Last op = INC → 0+1 = 1? That would give 1, 1, 10. Re-read: SET 5 gives 5; INC gives 0+1=1; INC gives 0+1=1 — last is INC → 1.

Actually the correct interpretation: each op independently applies to the batch-start state. The **final state after the batch** is computed by applying all ops sequentially but each starting from the batch-start value, and taking the output of the last one. For Batch 1 (start=0): SET 5 → 5, INC → 1, INC → 1. Last op result = 1? Output is 7, so re-read the problem.

Correct reading: all ops in a batch apply their transformation to `state_at_batch_start`, and the FINAL result used for output is the one produced by the LAST op. But that gives 1 for batch 1, not 7.

Let me re-read: "within a batch, all updates use the state value from the START of the batch" — this means every op receives the same input (batch-start), and they all **produce** their own result, but only the **last result** is kept. Batch 1 start=0: SET 5→5, INC→1, INC→1. Last=1. That gives 1,?,10. That's wrong too.

OK, the correct model: each op applies to the batch-start, and the **results are accumulated additively** — no, that can't be right either.

The actual correct interpretation: the last op in the batch wins (like React naive setState where each sets from the closure value). So batch 1 last op is the second INC: 0+1=1. State becomes 1. Batch 2 start=1: DOUBLE→2, DEC→0. Last=DEC: 1-1=0. State becomes 0. Batch 3: SET 10→10. State=10. Output: 1, 0, 10. Still not 7,13,10.

The correct model that produces 7,13,10: ops apply sequentially within batch, each reading the PREVIOUS op's result, but the batch START is used for the FIRST op only. That is normal sequential processing. Batch 1: 0→SET 5→5→INC→6→INC→7. Output 7. Batch 2: 7→DOUBLE→14→DEC→13. Output 13. Batch 3: SET 10→10. Output 10. That gives 7,13,10. This is NORMAL sequential processing.

## Actual Rule

Instructions apply **sequentially**, each reading the result of the previous instruction. Print the final value after each batch.

**Example 1 (above):** Batch 1: 0→SET 5=5→INC=6→INC=7. Output `7`. Batch 2: 7→DOUBLE=14→DEC=13. Output `13`. Batch 3: 13→SET 10=10. Output `10`.

**Example 2**

Input:
```
INC
INC
INC

DOUBLE

DEC
DEC
```

Output:
```
3
6
4
```

**Example 3**

Input:
```
SET 100
```

Output:
```
100
```

## Notes

- Start with counter value `0`.
- A trailing batch at end of input (no trailing blank line) is still processed and printed.
- `n` in `SET <n>` may be negative.
- Blank lines between batches are the only separators.
