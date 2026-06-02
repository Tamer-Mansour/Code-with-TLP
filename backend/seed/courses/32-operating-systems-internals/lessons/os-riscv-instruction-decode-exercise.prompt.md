# Prompt: Decode a 32-bit RISC-V Instruction

## Problem Description

You are implementing the decode stage of a RISC-V RV32I Instruction Set Simulator.

Given one or more 32-bit instruction words (in hexadecimal), decode each instruction and print the fields: opcode, rd, rs1, rs2, funct3, funct7, and the sign-extended immediate.

## Instruction Format Rules

Determine the format using the 7-bit opcode (bits [6:0]):

| Opcode (hex) | Format | Instruction type |
|---|---|---|
| 0x33 | R | ADD, SUB, AND, OR, XOR, SLT, SLTU, SLL, SRL, SRA |
| 0x03 | I | LB, LH, LW, LBU, LHU |
| 0x13 | I | ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI |
| 0x67 | I | JALR |
| 0x73 | I | ECALL/EBREAK |
| 0x23 | S | SB, SH, SW |
| 0x63 | B | BEQ, BNE, BLT, BGE, BLTU, BGEU |
| 0x37 | U | LUI |
| 0x17 | U | AUIPC |
| 0x6F | J | JAL |

**Field extraction (bit ranges are inclusive, 0-indexed from LSB):**

- opcode  = bits[6:0]
- rd      = bits[11:7]
- funct3  = bits[14:12]
- rs1     = bits[19:15]
- rs2     = bits[24:20]
- funct7  = bits[31:25]

**Immediate construction and sign extension:**

- I-type: imm = bits[31:20], sign-extend from bit 11 (12-bit immediate)
- S-type: imm = {bits[31:25], bits[11:7]}, sign-extend from bit 11
- B-type: imm = {bit[31], bit[7], bits[30:25], bits[11:8], 0}, sign-extend from bit 12
- U-type: imm = {bits[31:12], 12'b0} (already 32-bit, treat as signed)
- J-type: imm = {bit[31], bits[19:12], bit[20], bits[30:21], 0}, sign-extend from bit 20
- R-type: imm = 0, funct7 is used instead

Fields not applicable to a format are printed as 0.

## Input Format

- One or more lines, each containing exactly one 32-bit instruction word as an 8-character lowercase hexadecimal string (no "0x" prefix).

## Output Format

For each instruction, print exactly one line:

```
opcode=0x<HH> format=<X> rd=<D> rs1=<D> rs2=<D> funct3=0x<H> funct7=0x<HH> imm=<D>
```

Where:
- `<HH>` is the opcode as a 2-digit lowercase hex (e.g. `0x33`)
- `<X>` is one of: `R`, `I`, `S`, `B`, `U`, `J`, or `UNKNOWN`
- `<D>` is a decimal integer (signed for imm, unsigned for register numbers)
- `funct3` is 1 hex digit (0x0 to 0x7)
- `funct7` is 2 hex digits (0x00 to 0x7f)

## Constraints

- Each input line is a valid 8-hex-digit string.
- At most 100 instructions per input.
- Immediates are printed as signed decimal integers.
- Unknown opcodes: print format=UNKNOWN and all numeric fields as 0.

## Sample Input

```
00a00513
00000033
fe010113
```

## Sample Output

```
opcode=0x13 format=I rd=10 rs1=0 rs2=0 funct3=0x0 funct7=0x00 imm=10
opcode=0x33 format=R rd=0 rs1=0 rs2=0 funct3=0x0 funct7=0x00 imm=0
opcode=0x13 format=I rd=2 rs1=2 rs2=0 funct3=0x0 funct7=0x00 imm=-16
```

### Explanation

- `00a00513` = `ADDI x10, x0, 10` → I-type, opcode=0x13, rd=10, rs1=0, imm=10
- `00000033` = `ADD x0, x0, x0` → R-type, opcode=0x33, rd=0, rs1=0, rs2=0, imm=0
- `fe010113` = `ADDI x2, x2, -16` → I-type, opcode=0x13, rd=2, rs1=2, imm=-16 (sign extended)
