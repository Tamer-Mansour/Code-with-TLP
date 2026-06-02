# The Decode Stage in Detail

The **Decode** stage is where the raw bit pattern fetched from memory is transformed into a set of control signals that tell every other part of the processor what to do. It is the processor's interpreter — the bridge between "a 32-bit number" and "add the contents of register 1 and register 2, then store in register 5."

## What the Decode Stage Does

The Instruction Register (IR) holds a 32-bit value. The decode stage must answer these questions simultaneously:

1. **What type of instruction is this?** (ALU op, branch, load, store, immediate arithmetic, system call)
2. **Which registers are the sources?** (rs1, rs2)
3. **Which register is the destination?** (rd)
4. **What immediate value is embedded, and how should it be sign-extended?**
5. **What control signals should be sent to the ALU, memory, and write-back?**

These answers are derived entirely from **combinational logic** — no clock edge is needed; the signals propagate as soon as the IR is stable.

## RISC-V Instruction Formats

RISC-V uses six fixed encoding formats. Knowing which format applies tells the decoder exactly where to find every field:

| Format | Used For | Bit Fields |
|---|---|---|
| R-type | Register-register ops | opcode[6:0], rd[11:7], funct3[14:12], rs1[19:15], rs2[24:20], funct7[31:25] |
| I-type | Immediate ops, loads | opcode, rd, funct3, rs1, imm[11:0] |
| S-type | Stores | opcode, imm[4:0], funct3, rs1, rs2, imm[11:5] |
| B-type | Branches | opcode, imm (scattered), funct3, rs1, rs2 |
| U-type | Upper-immediate | opcode, rd, imm[31:12] |
| J-type | Jump (JAL) | opcode, rd, imm (scattered) |

The opcode field `[6:0]` always tells the decoder which format to apply, so there is no ambiguity.

## Immediate Reconstruction and Sign Extension

Immediates in RISC-V are split across non-contiguous bit fields to keep the most-significant bit (the sign bit) always at position 31 — a deliberate design choice that simplifies hardware by avoiding a mux on the sign-extension input.

```
B-type immediate reconstruction (12-bit signed → 13-bit, shifted left 1):
  imm[12]   ← inst[31]
  imm[10:5] ← inst[30:25]
  imm[4:1]  ← inst[11:8]
  imm[11]   ← inst[7]
  imm[0]    = 0  (branch targets are always even)
```

Sign-extension then replicates bit 12 into bits [31:13] to produce a full 32-bit signed offset.

## Register File Read

While the control logic is decoding the opcode, the register file is simultaneously read. The register indices (rs1, rs2) are available at fixed bit positions (`[19:15]` and `[24:20]`) regardless of instruction type, so the read can begin before the decoder even confirms the format. This parallel read is a key RISC design advantage.

```
        ┌──────────────┐
IR ────►│   Decoder    │────► Control Signals (ALU op, MemRead, MemWrite, RegWrite …)
        │              │────► Immediate (sign-extended)
        └──────────────┘
              │
              ▼ rs1, rs2 indices
        ┌──────────────┐
        │ Register File│────► A (rs1 value), B (rs2 value)
        └──────────────┘
```

## Control Signals Generated

The decoder drives a set of one-bit (and few-bit) control signals consumed by later stages:

| Signal | Width | Meaning |
|---|---|---|
| `ALUSrc` | 1 | 0 = B operand is register; 1 = B is immediate |
| `ALUOp` | 2–4 | Coarse instruction class (add/sub/logical/compare) |
| `MemRead` | 1 | This instruction reads data memory |
| `MemWrite` | 1 | This instruction writes data memory |
| `RegWrite` | 1 | This instruction writes a register |
| `MemToReg` | 1 | Result comes from memory (load) vs. ALU |
| `Branch` | 1 | This instruction is a conditional branch |

## Data Hazards and the Decode Stage

In a pipelined processor, the decode stage can encounter a **data hazard**: it tries to read a register that is still being written by an instruction earlier in the pipeline. Two solutions exist:

- **Forwarding (bypassing):** Route the result directly from a later stage back to the decode or execute stage input, skipping the register file entirely.
- **Stalling (pipeline interlock):** Insert a bubble (NOP) into the pipeline and wait for the write-back to complete.

Load-use hazards — where a `LOAD` is immediately followed by an instruction that needs the loaded value — cannot be resolved by forwarding alone and always require one stall cycle.

## Common Pitfalls

- **Confusing funct3 and funct7.** Both refine the opcode, but `funct7` is only present in R-type instructions. Treating I-type bits [31:25] as funct7 produces garbage.
- **Forgetting that sign extension is mandatory.** Immediates are always sign-extended to XLEN bits before use. Using zero-extension produces wrong results for negative values.
- **Assuming register reads happen after decode completes.** The register file read starts in parallel with decoding — the indices are always at fixed positions.

> **Interview answer:** The decode stage reads the instruction format from the opcode field, extracts register indices and immediates, sign-extends immediates to the full register width, reads the register file in parallel, and generates the control signals that steer every subsequent pipeline stage for that instruction.
