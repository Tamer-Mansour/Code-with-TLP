# Pipeline Hazards

A **hazard** is any condition that prevents the next instruction from executing in the next cycle, raising the effective CPI above the ideal value of 1. There are three classes: structural, data, and control hazards.

## 1. Structural Hazards

Two instructions simultaneously need the **same hardware resource** and it cannot handle both at once.

### Classic Example: Unified Memory

A CPU with one combined instruction + data memory: during cycle 5, instruction I1 does a `LW` (accesses memory in MEM stage) while instruction I5 attempts a fetch (needs memory in IF stage). Both demand the same physical RAM.

```
Cycle:    1    2    3    4    5    6
I1(LW): IF   ID   EX  [MEM] WB
I5:     ...                 [IF]  ← CONFLICT with I1 MEM
```

**Solution**: Separate instruction cache (I$) and data cache (D$). This eliminates the most common structural hazard entirely. Modern CPUs always have split L1 I$ and D$.

Other structural hazards:
- **FP multiply unit**: if there is only one FP multiplier and two FP multiply instructions are in flight, one must stall.
- **Write port contention**: two instructions complete WB in the same cycle but the register file has only one write port.

### Structural Hazard Stall

```
Cycle:  1    2    3    4    5    6    7
I1:    IF   ID   EX  MEM   WB
I2:         IF   ID   EX   --  MEM   WB   ← bubble (stall 1 cycle)
I3:              IF   ID   --  EX   MEM   WB
```

A stall inserts a **bubble** (NOP) into the pipeline — all upstream stages pause for one cycle.

## 2. Data Hazards

An instruction needs the result of a previous instruction that has not yet written back.

### RAW (Read After Write) — Most Common

```asm
add  x1, x2, x3   # writes x1 in WB (cycle 5)
sub  x4, x1, x5   # reads x1 in ID (cycle 3) — stale value!
```

Timing diagram showing the problem without forwarding:

```
Cycle:   1    2    3    4    5    6    7    8    9
add:    IF   ID   EX  MEM   WB
sub:         IF   ID*  --   --   EX  MEM   WB
                  ↑
                  reads x1 here (cycle 3), but add writes x1 in cycle 5
                  → without stalling, reads old/wrong value
```

Without intervention, `sub` would read the pre-addition value of x1.

### Solution A: Stalling (Inserting Bubbles)

The **hazard detection unit** stalls the pipeline until the result is available:

```
Cycle:   1    2    3    4    5    6    7    8    9
add:    IF   ID   EX  MEM   WB
sub:         IF   ID   --   --   EX  MEM   WB      (2-cycle stall)
             holds here     ↑ x1 now valid (written end of cycle 5,
                              EX reads at start of cycle 6)
```

This wastes 2 cycles. The CPI penalty for a 2-deep RAW with no forwarding is +2 per hazard.

### Solution B: Forwarding (Bypassing)

Route the result directly from the pipeline register where it was computed to the ALU input where it is needed, without waiting for writeback.

**EX-to-EX forward (1-cycle gap)**:

```asm
add  x1, x2, x3   # result in EX/MEM register after cycle 3
sub  x4, x1, x5   # needs x1 at start of cycle 4 (its EX stage)
```

```
Cycle:   1    2    3    4    5    6
add:    IF   ID   EX  MEM   WB
sub:         IF   ID   EX  MEM   WB
                  ↑    ↑
                  │    sub's EX needs x1
                  └──── EX/MEM register holds add's result → forward!
```

The forwarding MUX at the ALU input selects `EX/MEM.result` instead of `ID/EX.data1`.

**MEM-to-EX forward (2-cycle gap)**:

```asm
add  x1, x2, x3   # result in MEM/WB register after cycle 4
nop                # (one cycle gap)
sub  x4, x1, x5   # needs x1 at start of cycle 5 (its EX stage)
```

The forwarding MUX selects `MEM/WB.result`.

**Forwarding logic in hardware**:

```
ForwardA = 10  if (EX/MEM.RegWrite AND EX/MEM.rd = ID/EX.rs1)
         = 01  if (MEM/WB.RegWrite AND MEM/WB.rd = ID/EX.rs1)
         = 00  otherwise (use register file value)

(Similar for ForwardB / rs2)
```

Forwarding eliminates the CPI penalty for most RAW hazards with zero stall cycles.

### Load-Use Hazard (Cannot Forward Away)

```asm
lw   x1, 0(x2)    # memory value not available until end of MEM (cycle 4)
add  x3, x1, x4   # needs x1 at start of EX (cycle 4) — one cycle too early
```

```
Cycle:   1    2    3    4    5    6    7
lw:     IF   ID   EX  MEM   WB
add:         IF   ID   --   EX  MEM   WB
                       ↑
                 1-cycle stall inserted (bubble)
                 then MEM/WB → EX forwarding completes the path
```

After the stall, `MEM-to-EX` forwarding covers the rest. Total cost: **1 stall cycle per load-use hazard**.

The **hazard detection unit** identifies load-use hazards:

```
if (ID/EX.MemRead AND
    (ID/EX.rd == IF/ID.rs1 OR ID/EX.rd == IF/ID.rs2)):
    stall pipeline (insert bubble, hold PC and IF/ID register)
```

A good compiler (or the programmer using `__builtin_expect`) can reorder instructions to fill the stall slot with an unrelated instruction. MIPS historically exposed this as the **load delay slot** — the programmer is required to fill it.

### WAR and WAW Hazards

- **WAR (Write After Read)**: instruction J writes a register that instruction I (earlier) still needs to read. In simple in-order 5-stage pipelines, I always reads before J writes, so no hazard.
- **WAW (Write After Write)**: two instructions write the same register; the later write could complete before the earlier one (in out-of-order machines). The earlier write's result would be wrong.

These hazards are handled by **register renaming** in out-of-order processors.

## 3. Control Hazards (Branch Hazards)

When a branch instruction is fetched, the CPU does not yet know whether the branch is taken (and what the target is). It continues fetching sequentially, but those fetched instructions may be wrong.

### The Problem

```asm
beq  x1, x2, target    # branch resolved in EX stage (cycle 3)
     [next instruction] # fetched in cycle 2 — may be wrong
     [next+1]           # fetched in cycle 3 — may be wrong
```

```
Cycle:   1    2    3    4    5
beq:    IF   ID   EX  MEM   WB
I+1:         IF   ID  [FLUSH if branch taken]
I+2:              IF  [FLUSH if branch taken]
```

**Branch penalty**: 2 cycles (flush 2 instructions from IF and ID) when resolved in EX.

### Solution 1: Always Stall (Simple but Slow)

Insert 2 bubbles after every branch. For a 20% branch frequency with 2-cycle penalty: +0.4 CPI overhead.

### Solution 2: Static Prediction — Predict Not Taken

Continue fetching sequentially. If the branch is NOT taken (the common case for if-statements), no penalty. If taken: flush the 2 wrongly-fetched instructions and redirect to the target.

```
Not taken (correct prediction):  0 stall cycles
Taken   (misprediction):         2 stall cycles
```

For loops: the branch-back is taken on every iteration except the last. Predict-not-taken performs poorly (misses on every iteration).

### Solution 3: Delayed Branching (MIPS)

The instruction immediately after the branch — the **branch delay slot** — **always executes**, regardless of branch outcome. The compiler fills this slot with a useful instruction that must execute in either case.

```asm
beq x1, x0, done    # branch
addi x2, x2, 1      # delay slot: always executes (was about to execute anyway)
...
done:
```

If no useful instruction can fill the slot, a NOP is inserted. MIPS required this from the programmer. Modern ISAs (RISC-V, ARM) do not use delay slots.

### Solution 4: Dynamic Branch Prediction

A **Branch Prediction Buffer (BPB)** / **Branch Target Buffer (BTB)** uses execution history to predict the outcome of branches.

#### 1-bit Predictor

Store one bit per branch entry: 0 = predict not-taken, 1 = predict taken. Update on each execution.

- Problem: for a loop taken 9 times then not-taken once, mispredicts **twice** per loop (once entering, once exiting).

#### 2-bit Saturating Counter

Four states:

```
00 — Strongly Not Taken
01 — Weakly Not Taken
10 — Weakly Taken
11 — Strongly Taken

Taken outcome → increment (saturate at 11)
Not-taken    → decrement (saturate at 00)
Predict taken if state ≥ 10
```

For a loop taken 9 times then not-taken once: starts at 11, stays at 11 for all 9 taken iterations (no misprediction), drops to 10 at the exit (not-taken, mispredict), then 01 on the first iteration of the next invocation (misprediction), then back to 10 and 11. Only **2 mispredictions per 10 iterations** instead of 2 per 2.

#### Tournament (Hybrid) Predictors

Modern CPUs combine multiple predictors: local history (tracking each branch's own pattern), global history (correlating with the last N branches), and a meta-predictor that selects the better prediction. AMD K8, Intel Core, and Apple M1 use variants of this.

Neural branch predictors (perceptron-based) now dominate high-performance designs, achieving >99.5% accuracy on typical workloads.

#### Branch Target Buffer (BTB)

Even knowing a branch is taken, the CPU needs the **target address** to fetch from. The BTB caches (PC → target) pairs so the correct fetch address is available in the same cycle the branch is predicted taken.

## Performance Impact Summary

```
Effective CPI = 1  (ideal)
             + load_use_stalls          (typically 0.03–0.10 per instruction)
             + branch_misprediction     (typically 0.01–0.05 per instruction)
             + structural_stalls        (near 0 on modern CPUs)

Worked example:
  Load/store: 25% of instructions, 8% load-use hazards, 1 stall each
  Branches: 15% of instructions, 5% mispredicted, 15-cycle penalty (deep pipeline)

  Load-use stall CPI: 0.25 × 0.08 × 1 = 0.020
  Branch misprediction CPI: 0.15 × 0.05 × 15 = 0.113

  Effective CPI ≈ 1 + 0.020 + 0.113 = 1.133
  IPC ≈ 0.88
```

This shows why branch prediction accuracy matters so much on deep pipelines: a 15-cycle penalty with even a 5% miss rate adds more CPI overhead than all load-use hazards combined.
