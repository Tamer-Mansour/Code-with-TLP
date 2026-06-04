# Pipeline Hazard Classifier: Forwarding vs Stalls

Understanding exactly which instructions require stalls versus which can be resolved by forwarding is the difference between writing assembly that runs fast and assembly that silently burns pipeline cycles. This lesson builds precise intuition through the lens of the classic 5-stage RISC-V pipeline.

## The 5-Stage Pipeline Recap

```
IF → ID → EX → MEM → WB
```

Each instruction spends one cycle in each stage. The register file is read in **ID** and written in **WB**. A result produced by an ALU instruction is available at the end of **EX**; a load result is available at the end of **MEM**.

## RAW Hazards and the Distance Rule

A RAW (Read After Write) hazard occurs when instruction J reads a register that instruction I writes, and I has not yet finished writing when J needs to read.

The **distance** between instructions matters:

| Distance | Producer completes | Consumer reads | ALU producer result available? | Load producer result available? |
|----------|--------------------|----------------|-------------------------------|----------------------------------|
| 1 (back-to-back) | EX of cycle N+1 | ID of cycle N+1 | No — needs forwarding from EX/MEM | No — not even in MEM yet → STALL |
| 2 (one between) | MEM of cycle N+2 | ID of cycle N+2 | Forward from MEM/WB | Forward from MEM/WB |
| 3+ | WB completed | ID | No hazard | No hazard |

## Forwarding Paths

Forwarding (bypassing) routes the result from a pipeline register directly to the EX stage input, skipping the register file write and re-read:

```
EX/MEM → EX input  (for instruction immediately after an ALU op)
MEM/WB → EX input  (for instruction two after an ALU op, or immediately after a load)
```

These two forwarding paths resolve almost all RAW hazards at zero cost in stall cycles.

## The Load-Use Hazard: One Unavoidable Stall

The one case forwarding cannot solve is a **load followed immediately by a dependent instruction**:

```asm
lw  x1, 0(x2)      # load: result not available until end of MEM
add x3, x1, x4     # needs x1 at start of EX — one cycle too early!
```

Timeline:

```
Cycle:   1    2    3    4    5    6
lw:     IF   ID   EX   MEM  WB
add:         IF   ID   --   EX   MEM  WB
                       ↑ stall bubble inserted
```

The hardware pipeline controller detects this (via the Hazard Detection Unit) and inserts a bubble: it freezes IF and ID, cancels EX for that cycle, and replays the load result forward from MEM/WB into the add's EX stage one cycle later.

## Practical Impact on Code

The compiler (or assembly programmer) can often eliminate load-use stalls by **reordering** instructions:

```asm
# Before: 1 stall
lw   x1, 0(x2)
add  x3, x1, x4   # stall here
sub  x5, x6, x7   # independent

# After: 0 stalls (independent instruction fills slot)
lw   x1, 0(x2)
sub  x5, x6, x7   # independent, moved up
add  x3, x1, x4   # x1 now ready
```

This is called **load scheduling** and modern compilers do it automatically with `-O2` or higher.

## Structural Hazards

While data hazards dominate RISC-V discussions, structural hazards also exist. The classic one is a unified (shared) memory: if the same memory port services both instruction fetch (IF stage) and data access (MEM stage), the two stages conflict when both need memory simultaneously. RISC-V implementations solve this by separating instruction and data caches (Harvard-style L1), eliminating this structural hazard entirely.

## Control Hazards

Branch instructions create a control hazard because the processor does not know the next PC until the branch is resolved in EX. RISC-V cores typically handle this with one of:

- **Predict-not-taken**: always fetch PC+4; flush if branch is taken (1 bubble on a taken branch).
- **Static prediction with delay slot**: no delay slot in RISC-V base ISA (unlike MIPS).
- **Dynamic branch prediction**: BTB + 2-bit saturating counter; misprediction costs 2–15 cycles depending on pipeline depth.

## Key Takeaways

- RAW at distance 1 from an ALU instruction → **forwarding, no stall**.
- RAW at distance 1 from a load instruction → **1 stall required** (load-use hazard).
- RAW at distance 2 → **forwarding from MEM/WB, no stall** (both ALU and load).
- Distance 3+ → **no hazard**.
- `x0` never causes a hazard (hardwired to zero, writes are discarded).

## Further Reading

- *Computer Organization and Design RISC-V Edition* by Patterson and Hennessy — Section 4.8: Control Hazards and Section 4.7: Data Hazards Forwarding and Stalling.
- *Digital Design and Computer Architecture: RISC-V Edition* by Harris and Harris — Chapter 7: Microarchitecture, covering the pipelined RISC-V datapath with forwarding and hazard detection units (free slides at https://pages.hmc.edu/harris/ddca/ddcarv.html).
- MIT 6.004 Computation Structures — Problem sets on pipeline hazards (https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/).
