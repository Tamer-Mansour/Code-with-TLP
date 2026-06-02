# Forwarding and Bypassing

**Forwarding** (also called **bypassing**) is the most important optimization for data hazards. Instead of waiting for a value to be written to the register file and then read back, the processor routes the result directly from the pipeline register where it resides to the input of the functional unit that needs it. The value bypasses the normal read path entirely.

Forwarding eliminates the stall penalty for most RAW hazards at the cost of extra multiplexers and control logic in the datapath.

## Where Values Live in the Pipeline

After an ALU instruction completes its Execute stage, the result sits in the **EX/MEM pipeline register** — it has not yet been written to the register file. One cycle later it moves to the **MEM/WB pipeline register**. Only after the WB stage does it reach the register file.

Without forwarding, the consumer must wait until WB. With forwarding, the consumer can receive the value from either pipeline register as soon as it is produced.

## Forwarding Paths

```
                    EX/MEM          MEM/WB
                  ┌────────┐      ┌────────┐
   IF → ID → EX → │ result │→ MEM→│ result │→ WB
                  └────┬───┘      └────┬───┘
                       │  forward       │  forward
                       └──────┐ ┌───────┘
                              ▼ ▼
                        ALU input MUX (EX stage)
```

There are two forwarding paths used most often:

| Path Name | From | To | Resolves |
|---|---|---|---|
| EX-to-EX | EX/MEM register | ALU input of next instruction | One-cycle gap |
| MEM-to-EX | MEM/WB register | ALU input of instruction two cycles later | Two-cycle gap |

## Forwarding Control Logic

The hazard detection unit generates forwarding control signals by comparing register identifiers:

```
// EX-to-EX forward for source A
if (EX_MEM.RegWrite
    && EX_MEM.RD != 0
    && EX_MEM.RD == ID_EX.RS1)
    ForwardA = EX_to_EX

// MEM-to-EX forward for source A
if (MEM_WB.RegWrite
    && MEM_WB.RD != 0
    && MEM_WB.RD == ID_EX.RS1)
    ForwardA = MEM_to_EX
```

The `RD != 0` check is essential: `x0` in RISC-V is hardwired to zero and can never be a meaningful destination.

## Worked Example

```asm
add  x1, x2, x3   # produces x1 at end of EX (cycle 3)
sub  x4, x1, x5   # needs x1 at start of EX (cycle 4) — EX-to-EX forward
and  x6, x1, x7   # needs x1 at start of EX (cycle 5) — MEM-to-EX forward
or   x8, x1, x9   # needs x1 at start of EX (cycle 6) — register file (no forward needed)
```

All three consumers get the correct value of `x1` with **zero stall cycles** because forwarding supplies it directly from the appropriate pipeline register.

## What Forwarding Cannot Fix

Forwarding solves ALU-to-ALU RAW hazards completely. But it cannot help when the producing instruction is a **load** and the consumer immediately follows:

```asm
lw   x1, 0(x2)    # result of load is available only at END of MEM (cycle 4)
add  x3, x1, x4   # needs x1 at START of EX (cycle 4) — impossible!
```

The load result is not available until the end of the MEM stage, but the consumer needs it at the beginning of its EX stage — the same cycle. Even forwarding cannot travel back in time. This specific case — the **load-use hazard** — always requires exactly one stall cycle.

## Double Data Hazards

When a destination register appears multiple times in the pipeline:

```asm
add  x1, x2, x3   # instruction I
add  x1, x4, x5   # instruction J (overwrites x1)
add  x6, x1, x7   # instruction K (needs x1 from J, not I)
```

Forwarding logic must give priority to the **most recent** producer. The EX/MEM forward takes precedence over the MEM/WB forward when both would apply, because EX/MEM holds the newer value.

## Performance Impact

Without forwarding, every RAW hazard costs 2 stall cycles. Studies of typical workloads show that roughly 25–30% of instructions have a RAW dependency with their immediate predecessor. Forwarding turns that from a 50–60% CPI overhead into zero overhead for ALU chains.

## Interview Answer

> "Forwarding routes a result directly from a pipeline register (EX/MEM or MEM/WB) to the ALU input of the consuming instruction, bypassing the register file. It eliminates the stall penalty for ALU-to-ALU RAW hazards entirely, but it cannot help with a load immediately followed by a use — that still requires one stall cycle."
