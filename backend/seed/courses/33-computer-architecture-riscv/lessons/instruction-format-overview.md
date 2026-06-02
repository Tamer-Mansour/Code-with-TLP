# Overview of RISC-V Instruction Formats

Every RISC-V base integer instruction is exactly 32 bits wide. That fixed width is a deliberate design choice: decoders stay simple, pipelines stay uniform, and compilers can reason about instruction boundaries without ambiguity. Within those 32 bits, the ISA defines six canonical formats — R, I, S, B, U, and J — each tailored to a specific class of operation.

## Why Six Formats?

Different operations need different operands:

- **Arithmetic** between two registers needs two source registers and one destination register.
- **Loads and immediate arithmetic** need one source register, one destination register, and a constant.
- **Stores** need two source registers and a constant offset, but no destination register.
- **Branches** need two source registers and a PC-relative offset.
- **Upper-immediate** instructions need only a destination register and a 20-bit constant.
- **Jump-and-link** needs a destination register and a 20-bit PC-relative offset.

Rather than inventing per-instruction encodings, RISC-V groups these into six formats and keeps the bit positions of common fields identical across formats wherever possible.

## The Six Formats at a Glance

| Format | Typical uses | Immediate bits |
|--------|-------------|----------------|
| R | `add`, `sub`, `and`, `or`, `sll` | none |
| I | `addi`, `lw`, `jalr`, `ecall` | 12 |
| S | `sw`, `sh`, `sb` | 12 |
| B | `beq`, `bne`, `blt`, `bge` | 13 (12 encoded) |
| U | `lui`, `auipc` | 20 |
| J | `jal` | 21 (20 encoded) |

## Constant Fields Across All Formats

Regardless of format, bits [6:0] are always the **opcode**, and bits [11:7] are always **rd** (the destination register) — or repurposed as part of an immediate in formats that have no destination. Similarly, bits [19:15] and [24:20] are always **rs1** and **rs2** when those registers are present.

This regularity means the decode stage can latch register addresses and the opcode in parallel, before it even knows the full format. The format is disambiguated later by the opcode (and sometimes funct3).

```
Bit positions:  31       25 24    20 19    15 14   12 11      7 6       0
                +---------+--------+--------+-------+---------+---------+
R-type:         |  funct7 |  rs2   |  rs1   | funct3|   rd    | opcode  |
I-type:         |   imm[11:0]      |  rs1   | funct3|   rd    | opcode  |
S-type:         |imm[11:5]|  rs2   |  rs1   | funct3|imm[4:0] | opcode  |
B-type:         |imm[12|10:5]| rs2 |  rs1   | funct3|imm[4:1|11]|opcode|
U-type:         |         imm[31:12]         |       |   rd    | opcode  |
J-type:         |    imm[20|10:1|11|19:12]   |       |   rd    | opcode  |
                +---------+--------+--------+-------+---------+---------+
```

## Key Design Principles

**Sign extension is always from bit 31.** The MSB of every immediate is placed at bit 31 of the instruction word. This lets the sign-extension hardware read a single bit without format-dependent multiplexing.

**Immediates are intentionally scrambled.** The bit positions of immediate sub-fields look chaotic at first. They are arranged so that the bits that are also present in register specifiers stay in those positions — reducing the number of multiplexers in hardware. This is the most common "gotcha" in interview questions about RISC-V encoding.

**No instruction sets all 32 bits of a destination register to a constant in one cycle** (for RV32I). The split between U-type (upper 20 bits) and I-type (lower 12 bits) via `lui + addi` is intentional; it keeps the instruction word width fixed.

## Interview Answer

> "RISC-V uses six 32-bit instruction formats — R, I, S, B, U, J — that share fixed field positions for the opcode and register specifiers. The sign bit of every immediate is always at instruction bit 31, and immediates are scrambled to minimize decoder hardware complexity."
