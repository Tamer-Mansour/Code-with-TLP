# Instruction Encoding Basics (RISC-V Overview)

RISC-V is the go-to architecture for VP and OS interview problems because its encoding is clean, open, and freely documented. Understanding how 32 bits become an operation is the foundation of any instruction-set simulator.

## Why RISC-V?

- Fixed 32-bit instruction width (base ISA) — no length-decoding prefix logic.
- A small number of format types means a compact decode table.
- Open specification — you can download the full manual for free.
- Used in chips from SiFive, Espressif, Western Digital, and many academic CPUs.

## Instruction Formats

Every RISC-V base instruction is 32 bits. Six formats cover the entire base ISA:

| Format | Fields | Typical use |
|---|---|---|
| R | opcode, rd, funct3, rs1, rs2, funct7 | ALU register-to-register |
| I | opcode, rd, funct3, rs1, imm[11:0] | Loads, ADDI, JALR |
| S | opcode, funct3, rs1, rs2, imm[11:0] | Stores |
| B | opcode, funct3, rs1, rs2, imm[12:1] | Branches |
| U | opcode, rd, imm[31:12] | LUI, AUIPC |
| J | opcode, rd, imm[20:1] | JAL |

The `opcode` field is always bits [6:0]. Bits [4:2] identify the major group; bits [1:0] are always `11` for 32-bit instructions (allowing future compressed extensions at `00`, `01`, `10`).

## R-Type Bit Layout

```
 31       25 24  20 19  15 14  12 11   7 6     0
 [ funct7 ] [ rs2 ] [ rs1 ] [fn3] [ rd  ] [opcode]
    7 bits    5 bits  5 bits 3 bits  5 bits  7 bits
```

Extracting fields in C++:

```cpp
uint32_t opcode = instr & 0x7F;           // bits [6:0]
uint32_t rd     = (instr >>  7) & 0x1F;  // bits [11:7]
uint32_t funct3 = (instr >> 12) & 0x07;  // bits [14:12]
uint32_t rs1    = (instr >> 15) & 0x1F;  // bits [19:15]
uint32_t rs2    = (instr >> 20) & 0x1F;  // bits [24:20]
uint32_t funct7 = (instr >> 25) & 0x7F;  // bits [31:25]
```

These six lines decode every R-type instruction completely. `ADD` is opcode=0x33, funct3=0, funct7=0x00. `SUB` is the same opcode and funct3 but funct7=0x20.

## I-Type Immediate Sign Extension

The 12-bit immediate in I-type instructions is **sign-extended** to 32 bits:

```cpp
int32_t imm_i(uint32_t instr) {
    int32_t raw = static_cast<int32_t>(instr) >> 20;  // arithmetic shift
    return raw;   // sign bit is already in position after arithmetic right shift
}
```

Forgetting sign extension is the single most common ISS bug. A load of `-4(sp)` will jump to address `0xFFFFFFFC` instead of the correct stack slot if you treat the immediate as unsigned.

## B-Type Branch Immediates — A Gotcha

Branch immediates are **not** contiguous in the encoding. The spec scrambles bits to reuse hardware from other formats:

```
imm[12]  = bit 31
imm[11]  = bit 7
imm[10:5]= bits 30:25
imm[4:1] = bits 11:8
imm[0]   = always 0 (branches are 2-byte aligned)
```

```cpp
int32_t imm_b(uint32_t instr) {
    uint32_t bit12  = (instr >> 31) & 1;
    uint32_t bit11  = (instr >>  7) & 1;
    uint32_t bits10_5 = (instr >> 25) & 0x3F;
    uint32_t bits4_1  = (instr >>  8) & 0xF;
    uint32_t raw = (bit12 << 12) | (bit11 << 11) | (bits10_5 << 5) | (bits4_1 << 1);
    // sign-extend from bit 12
    return static_cast<int32_t>(raw << 19) >> 19;
}
```

## Common Opcodes to Memorize

| Opcode (hex) | Format | Instructions |
|---|---|---|
| 0x33 | R | ADD, SUB, AND, OR, XOR, SLL, SRL, SRA |
| 0x13 | I | ADDI, ANDI, ORI, XORI, SLLI, SRLI, SRAI |
| 0x03 | I | LB, LH, LW, LBU, LHU |
| 0x23 | S | SB, SH, SW |
| 0x63 | B | BEQ, BNE, BLT, BGE, BLTU, BGEU |
| 0x37 | U | LUI |
| 0x17 | U | AUIPC |
| 0x6F | J | JAL |
| 0x67 | I | JALR |

## Interview Answer

> **Interview answer:** "RISC-V uses six fixed-width 32-bit formats. The opcode is always in bits [6:0]; additional fields (funct3, funct7, rd, rs1, rs2) are extracted with shifts and masks. Immediates require careful sign extension — using arithmetic right shifts in C++ — and branch immediates have a scrambled layout that must be reassembled before use."
