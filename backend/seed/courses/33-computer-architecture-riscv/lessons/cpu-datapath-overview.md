# The CPU Datapath: A Guided Tour

The **datapath** is the collection of functional units, registers, and interconnections through which data flows as instructions execute. Think of it as the "plumbing" of the CPU — the control unit opens and closes valves, but actual data travels through the datapath.

## Major Datapath Components

| Component | Function |
|---|---|
| Register File | Array of fast registers; read two operands, write one result per cycle |
| ALU | Performs add, sub, AND, OR, shift, compare, etc. |
| Multiplexers (Muxes) | Route the correct data source to the next stage |
| Adder (PC+4) | Dedicated adder that increments the Program Counter |
| Immediate Generator | Sign-extends immediate fields from the instruction bits |
| Data Memory Port | Interface to L1 data cache / RAM for load/store |
| Instruction Memory Port | Interface to L1 instruction cache for fetches |

## A Single-Cycle RISC-V Datapath Walkthrough

Consider the instruction `add x3, x1, x2` — add registers x1 and x2, write the result to x3.

```
Instruction Memory
       |
       | [32-bit instruction word]
       v
   Decode Logic
   /     |     \
 RS1    RS2    RD (destination tag)
  |      |
Register File
  |      |
  v      v
[x1]   [x2]
  \    /
   ALU  <--- control signals say "ADD"
    |
    v
  Result
    |
    v
Register File (write port -> x3)
```

## Handling Load Instructions

`lw x5, 8(x2)` — load the 32-bit word at address (x2 + 8) into x5.

The datapath must do two things the ALU-only path does not:

1. Compute the effective address: ALU adds x2 + sign_extend(8).
2. Read data memory at that address and route it (not the ALU output) back to the register file.

A **mux** just before the register write port selects between:
- ALU result (for R-type / I-type ALU ops)
- Data memory output (for load instructions)

The control unit drives the mux select line.

## Handling Branch Instructions

`beq x1, x2, label` — if x1 == x2, jump to label.

Two things happen in parallel:

```
ALU: subtract x1 - x2  →  zero flag
PC Adder: PC + sign_extend(offset) << 1  →  branch target address
```

A second mux selects between `PC+4` (sequential) and the branch target. The control unit enables this mux only when the branch is taken (zero flag is set for `beq`).

## Data Hazards and Forwarding

In a **pipelined** datapath (covered in later modules), an instruction may need a result that a previous instruction has not yet written back:

```asm
add x1, x2, x3   # produces x1 in EX stage
sub x4, x1, x5   # needs x1 immediately in next EX stage
```

**Forwarding (bypassing)** solves this by routing the ALU output directly back to the ALU input without waiting for the register file write. Datapath designers add dedicated forwarding paths — extra wires — to enable this.

## Key Design Principle: Shared vs Dedicated Hardware

- **Shared** — one ALU handles both address calculation (loads/stores) and arithmetic (R/I-type). Simpler, smaller.
- **Dedicated** — separate adders for PC increment and branch target avoid slowing down the critical path. Common in real CPUs.

## Common Pitfalls

- **Forgetting sign extension.** RISC-V immediate fields are sign-extended before entering the ALU. Treating them as zero-extended causes wrong addresses/values.
- **Missing the write-enable.** The register file's write port must be gated — instructions like `beq` should not accidentally overwrite any register.
- **Confusing data memory and instruction memory.** Harvard-style caches treat them as separate; confusing them leads to incorrect pipeline analysis.

## Interview Answer

> "The datapath is the set of hardware units — ALU, register file, muxes, and memory interfaces — through which data flows. The control unit tells the datapath *what* to do by asserting control signals; the datapath actually carries and transforms the data."
