# Stalls, Bubbles, and Pipeline Interlocks

When a hazard cannot be resolved by forwarding alone, the pipeline must be **stalled**: the affected instruction and all instructions behind it are held in place for one or more clock cycles while the pipeline waits for the necessary data or resource to become available. The empty slot that appears in the pipeline as a result is called a **bubble**.

## What Is a Stall?

A stall freezes the program counter and all pipeline stages up to and including the blocked instruction. The stages that have already passed the blocked instruction continue to advance normally — they carry real work. The stages behind it sit idle, holding the same instructions they held in the previous cycle.

Concretely, in a five-stage pipeline stalling the ID stage means:

- **PC** is not incremented (the same instruction will be fetched again next cycle).
- **IF/ID register** is not updated (the fetched instruction is re-held).
- **ID/EX register** is loaded with a **NOP** (no-operation) — the bubble.
- **EX, MEM, WB** stages continue normally.

## What Is a Bubble?

A bubble is a NOP injected into the pipeline. It has no effect on registers, memory, or the program counter. As it flows through the pipeline it simply occupies hardware slots without doing useful work. Each bubble corresponds to one wasted cycle of throughput.

In RISC-V the canonical NOP is `addi x0, x0, 0` — it writes to `x0`, which is hardwired to zero, so the write has no effect. The pipeline control can also inject a bubble by zeroing the control signals in the ID/EX pipeline register rather than inserting an actual NOP instruction.

```
Cycle:     1    2    3    4    5    6    7
lw  x1     IF   ID   EX  MEM   WB
add x3     —    IF   ID  [stall] EX  MEM  WB
           —    —    —   bubble  —   —    —
sub x5     —    —    IF   ID    EX  MEM   WB
```

The bubble appears in cycle 4 where `add` would have been in EX — it occupies the EX, MEM, and WB stages in cycles 4, 5, and 6 doing nothing.

## Pipeline Interlocks

A **pipeline interlock** is the hardware mechanism that detects a hazard and generates the stall. It is implemented as a combinational circuit — the hazard detection unit — that:

1. Reads the source register identifiers of the instruction currently in ID.
2. Reads the destination register identifiers and instruction types of instructions currently in EX and MEM.
3. Checks whether a load-use hazard exists.
4. If so, asserts stall control signals for PC and IF/ID, and clears the control signals in ID/EX to insert a bubble.

```
Hazard Condition (load-use):
  if (ID_EX.MemRead
      && (ID_EX.RD == IF_ID.RS1 || ID_EX.RD == IF_ID.RS2))
      → stall for 1 cycle
```

## Stall Penalty and CPI

Each stall adds 1 to the CPI. The total CPI is:

```
CPI = ideal_CPI + (stall_rate × stall_cycles)
    = 1.0 + (stalls_per_instruction × 1)
```

For a typical integer workload with forwarding enabled, the load-use hazard occurs roughly 10–15% of the time, giving a CPI of approximately 1.10–1.15.

## Multiple Stall Cycles

Some hazards require more than one stall. A multicycle floating-point divide may have a latency of 20+ cycles. If forwarding is implemented, the stall count equals:

```
stalls = producer_latency - (pipeline_stages_between + forwarding_benefit)
```

For a 20-cycle divide followed immediately by a use, and forwarding from the result register, the stall count is approximately 19 cycles.

## Common Pitfall: Confusing Stall vs Bubble

- A **stall** is an action applied to the pipeline (hold these stages).
- A **bubble** is the result of a stall (a NOP that flows through the pipeline).

You stall an instruction; you insert a bubble. In timing diagrams you annotate stages, not the stall signal itself. When the problem says "how many stall cycles?", count the bubbles that appear in the diagram for the affected instruction.

## Interview Answer

> "A stall freezes the pipeline by holding the PC and all stages behind the hazard in place. A bubble is the NOP inserted into the stage that would have been used by the stalled instruction. A pipeline interlock is the hardware circuit that detects the hazard and generates the stall and bubble signals automatically."
