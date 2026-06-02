# Opcode, funct3, and funct7 Fields

Three fields act as the "instruction selector" in RISC-V: opcode, funct3, and funct7. Together they uniquely identify every instruction in the base ISA. Understanding their structure is essential for reading encoding tables, writing decoders, and explaining RISC-V to an interviewer.

## The Opcode Field (bits [6:0])

The 7-bit opcode selects the **instruction format and major group**. With 7 bits you could encode 128 values, but RISC-V reserves codes so that bits [1:0] are always `11` for 32-bit instructions. This lets compressed (16-bit) instructions use codes ending in `00`, `01`, or `10` — making the compressed extension backward-compatible.

Key opcode values for RV32I:

| Opcode (binary) | Hex | Group |
|-----------------|-----|-------|
| 0110011 | 0x33 | R-type: integer register-register |
| 0010011 | 0x13 | I-type: integer immediate |
| 0000011 | 0x03 | I-type: loads |
| 0100011 | 0x23 | S-type: stores |
| 1100011 | 0x63 | B-type: branches |
| 0110111 | 0x37 | U-type: LUI |
| 0010111 | 0x17 | U-type: AUIPC |
| 1101111 | 0x6F | J-type: JAL |
| 1100111 | 0x67 | I-type: JALR |
| 1110011 | 0x73 | I-type: SYSTEM (ECALL, CSR) |

Notice that opcode alone tells you the format. A decoder pipeline stage can latch the format bits and start routing operands before funct3 is even examined.

## The funct3 Field (bits [14:12])

funct3 is a 3-bit field that selects among the instructions within an opcode group (up to 8 distinct operations). Its meaning is opcode-dependent.

**For integer immediate (opcode 0x13):**

| funct3 | Instruction |
|--------|-------------|
| 000    | ADDI |
| 001    | SLLI |
| 010    | SLTI |
| 011    | SLTIU |
| 100    | XORI |
| 101    | SRLI / SRAI |
| 110    | ORI |
| 111    | ANDI |

**For loads (opcode 0x03):**

| funct3 | Instruction | Transfer |
|--------|-------------|----------|
| 000    | LB  | signed byte |
| 001    | LH  | signed halfword |
| 010    | LW  | word |
| 100    | LBU | unsigned byte |
| 101    | LHU | unsigned halfword |

**For branches (opcode 0x63):**

| funct3 | Instruction |
|--------|-------------|
| 000    | BEQ |
| 001    | BNE |
| 100    | BLT |
| 101    | BGE |
| 110    | BLTU |
| 111    | BGEU |

## The funct7 Field (bits [31:25])

funct7 is a 7-bit field present only in R-type instructions (and the shift immediate variants of I-type). It provides additional discrimination within the same (opcode, funct3) pair.

In practice, RISC-V uses only a few funct7 values:

| funct7    | Notes |
|-----------|-------|
| 0000000   | Default — most instructions |
| 0100000   | Alternate — SUB (vs ADD), SRA (vs SRL) |
| 0000001   | M-extension — MUL, DIV, REM |

The critical bit is **bit 30** (second from the top): it is 0 for the "default" operation and 1 for the "alternate" arithmetic operation. Silicon implementations commonly decode only this single bit rather than all seven.

```asm
add  x1, x2, x3   # funct7 = 0000000, funct3 = 000
sub  x1, x2, x3   # funct7 = 0100000, funct3 = 000  <- bit 30 set
srl  x1, x2, x3   # funct7 = 0000000, funct3 = 101
sra  x1, x2, x3   # funct7 = 0100000, funct3 = 101  <- bit 30 set
```

## Decoding Example

Given instruction `0x00A28233`:

```
Binary: 0000 0000 1010 0010 1000 0010 0011 0011
                                              ↑ opcode bits [6:0] = 011 0011 = 0x33 → R-type
```

Break it down:

| Field  | Bits    | Value   | Meaning |
|--------|---------|---------|---------|
| funct7 | [31:25] | 0000000 | default |
| rs2    | [24:20] | 01010   | x10 |
| rs1    | [19:15] | 00101   | x5 |
| funct3 | [14:12] | 000     | ADD/SUB |
| rd     | [11:7]  | 00100   | x4 |
| opcode | [6:0]   | 0110011 | R-type |

Result: `add x4, x5, x10`

## Common Pitfall

Candidates confuse the opcode for stores (`0100011`) with the opcode for R-type (`0110011`) — they differ by one bit. Always check all seven opcode bits before concluding the format.

## Interview Answer

> "Opcode (7 bits) identifies the format and instruction group; funct3 (3 bits) selects among operations in that group; funct7 (7 bits, R-type only) provides a final discriminator — notably bit 30 switches ADD to SUB and SRL to SRA. Together they uniquely identify every RV32I instruction."
