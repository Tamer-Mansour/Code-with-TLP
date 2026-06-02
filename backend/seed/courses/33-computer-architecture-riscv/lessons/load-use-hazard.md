# The Load-Use Hazard

The **load-use hazard** is a special and unavoidable case of a RAW data hazard. It occurs when a `lw` (load word) instruction is immediately followed by an instruction that uses the loaded value. Even with full forwarding hardware in place, exactly one stall cycle is required — there is no way around it in a standard five-stage in-order pipeline.

## Why Forwarding Alone Is Insufficient

In the five-stage pipeline, a load instruction produces its result at the **end of the MEM stage** (stage 4). The consuming instruction needs that value at the **start of its EX stage** (also stage 4 — one cycle later for the immediately following instruction). Since EX comes before MEM in the pipeline order, the consumer arrives at EX at the same moment the load is completing MEM. The result cannot travel backwards in time.

```
Cycle:     1    2    3    4    5    6    7
lw  x1     IF   ID   EX  MEM   WB
add x3     —    IF   ID  [??]  EX  MEM   WB
                         ↑
                    add needs x1 here (start of EX = cycle 5)
                    lw  produces x1 here (end of MEM = end of cycle 4) ✓
```

Wait — looking at this carefully: if `add` stalls one cycle, it enters EX in cycle 6, while `lw` finishes MEM at end of cycle 5. Forwarding from MEM/WB to EX input then works perfectly. Without the stall, `add` would be in EX in cycle 4 — the same cycle `lw` is in MEM — and the value is not yet available at the start of that cycle.

The interlock inserts **one bubble** and then forwarding handles the transfer.

## Timing Diagram With One Stall

```
Cycle:      1    2    3    4    5    6    7    8
lw   x1,0(x2)  IF   ID   EX  MEM   WB
               [stall inserted by interlock]
add  x3,x1,x4  —    IF   ID  NOP   EX  MEM   WB
                              ↑
                           bubble
```

After the stall, `lw` is in MEM/WB at the start of cycle 6, and `add` is at the start of EX in cycle 6. The MEM-to-EX forwarding path delivers `x1` in time.

## Hardware Detection

The load-use hazard detection condition is:

```
if (ID_EX.MemRead == 1
    && (ID_EX.RD == IF_ID.RS1 || ID_EX.RD == IF_ID.RS2))
    → stall
```

Note that `ID_EX.MemRead` specifically checks for a load, not just any instruction. An ALU instruction writing the same register does not trigger this condition because its result is available a full cycle earlier (end of EX, not end of MEM).

## The One-Cycle Unavoidable Penalty

This is one of the important constants in computer architecture to memorize:

| Hazard | With Forwarding |
|---|---|
| ALU → ALU (back-to-back) | 0 stall cycles |
| ALU → ALU (one instruction gap) | 0 stall cycles |
| Load → Use (back-to-back) | **1 stall cycle** |
| Load → Use (one instruction gap) | 0 stall cycles |

One independent instruction between the load and its use is enough to eliminate the stall:

```asm
lw   x1, 0(x2)
addi x6, x7, 4    # independent instruction — fills the load-use slot
add  x3, x1, x4   # no stall: x1 is now in MEM/WB at the right cycle
```

## Compiler Role

The compiler can often eliminate the load-use stall penalty by **load scheduling**: reordering instructions to place an independent operation in the slot between a load and its first consumer. This is done during the instruction scheduling phase of compilation and requires the compiler to prove that the inserted instruction does not modify `x1`, `x2`, or otherwise affect correctness.

```c
// C source
int a = mem[i];
int b = c + d;        // independent
int result = a + b;
```

```asm
lw   x1, 0(x2)        # load a
add  x3, x4, x5       # compute b (independent, fills slot)
add  x6, x1, x3       # compute result — no stall
```

## Common Pitfall

Students sometimes think that a `lw` followed by a `sw` using the loaded value has no load-use hazard because `sw` does not use a register in EX. In RISC-V, `sw x1, 0(x2)` reads `x1` in the EX stage (to compute the store data), so the hazard still applies.

## Interview Answer

> "The load-use hazard occurs when a load is immediately followed by an instruction that uses the loaded register. One stall cycle is always required because the load's result is not available until the end of MEM — one cycle too late for the consumer's EX stage even with forwarding. Placing one independent instruction between the load and its use eliminates the stall."
