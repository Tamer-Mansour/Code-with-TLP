# Data Hazards: RAW, WAR, WAW

A **data hazard** arises when an instruction depends on the result of a prior instruction that has not yet completed. Because the pipeline overlaps execution, the dependent instruction may attempt to read a value that is still being computed or has not yet been written back to the register file.

There are three kinds of data hazard, classified by the direction of the dependency.

## RAW — Read After Write (True Dependency)

The most common and most important hazard. Instruction J tries to read a register that instruction I has not yet finished writing.

```asm
add  x1, x2, x3   # I: writes x1
sub  x4, x1, x5   # J: reads x1 — RAW hazard
```

This is called a *true dependency* because it reflects real information flow: J genuinely needs the value that I produces. You cannot eliminate a RAW hazard by reordering; you can only satisfy it sooner via **forwarding** or hide it by placing independent instructions between I and J.

## WAR — Write After Read (Anti-dependency)

Instruction J writes a register that instruction I has not yet finished reading.

```asm
sub  x4, x1, x5   # I: reads x1
add  x1, x2, x3   # J: writes x1 — WAR hazard
```

In a simple in-order pipeline, J is always behind I, so J's write always happens after I's read — **WAR hazards do not occur in classic in-order pipelines**. They matter in out-of-order processors and compilers doing register renaming or code motion.

## WAW — Write After Write (Output Dependency)

Both instruction I and instruction J write to the same register. If J completes before I (possible in out-of-order or variable-latency pipelines), the register ends up with I's value instead of J's.

```asm
add  x1, x2, x3   # I: writes x1 (long latency, e.g., from memory)
sub  x1, x4, x5   # J: also writes x1 — WAW hazard
```

Again, in a strict in-order pipeline with uniform latency this does not manifest, but it surfaces in pipelines with variable-latency functional units (e.g., a multicycle floating-point unit).

## Comparing the Three

| Hazard | Also Known As | In-Order Pipeline Risk | Out-of-Order Risk |
|---|---|---|---|
| RAW | True dependency | High | High |
| WAR | Anti-dependency | Low (rare) | High |
| WAW | Output dependency | Low (rare) | High |

## How Many Stalls Does a RAW Cause?

In a classic five-stage pipeline (IF, ID, EX, MEM, WB):

- The result of an ALU instruction is available at the **end of EX** (cycle 3 for the first instruction).
- The consumer reads registers in **ID** (cycle 2 for the instruction immediately after).
- Without forwarding: the consumer arrives at ID in cycle 2 but needs data not available until end of cycle 3. This requires **2 stall cycles**.
- With forwarding from EX/MEM pipeline register: **0 stall cycles** for ALU-to-ALU.
- With forwarding from MEM/WB pipeline register: **0 stall cycles** for ALU-to-ALU with one instruction gap.
- A load followed immediately by a use: **1 stall cycle** even with forwarding (the load-use hazard).

## Worked Example

```asm
lw   x1, 0(x2)    # cycle 1-5: result available end of MEM (cycle 4)
add  x3, x1, x4   # cycle 2-6: needs x1 in EX (cycle 4) — 1 stall needed
sub  x5, x3, x6   # can use forwarding from EX/MEM, no stall
```

Inserting an independent instruction between `lw` and `add` eliminates the stall:

```asm
lw   x1, 0(x2)
addi x7, x8, 1    # independent — fills the hazard slot
add  x3, x1, x4   # now x1 is ready, no stall
```

## Common Pitfall

Students sometimes say "we can avoid RAW by reordering." You cannot reorder a true RAW without changing program semantics — J must always use I's output. What you *can* do is fill the gap with independent instructions so the pipeline doesn't stall waiting.

## Interview Answer

> "There are three data hazard types: RAW (true dependency — the consumer reads before the producer finishes writing), WAR (anti-dependency — write happens before a prior read completes), and WAW (output dependency — two writes to the same destination arrive out of order). RAW is the only one that causes stalls in a classic in-order pipeline; WAR and WAW become critical in out-of-order designs."
