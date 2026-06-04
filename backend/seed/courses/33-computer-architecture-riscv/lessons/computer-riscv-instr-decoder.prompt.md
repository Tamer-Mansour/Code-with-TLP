# RISC-V Instruction Decoder

## Problem Description

Given one or more 32-bit RISC-V machine instructions, each as an 8-character hexadecimal string (no `0x` prefix), decode each instruction and print its type, opcode bits, and all relevant fields.

Use the standard RISC-V base ISA opcode map:

| opcode bits [6:0] | Type |
|-------------------|------|
| 0110011           | R    |
| 0010011           | I    |
| 0000011           | I    |
| 1100111           | I    |
| 0100011           | S    |
| 1100011           | B    |
| 0110111           | U    |
| 0010111           | U    |
| 1101111           | J    |

If the opcode does not match any entry above, print `UNKNOWN`.

## Output Format Per Instruction

Print one line per instruction in exactly the following formats:

**R-type:**
```
Type=R opcode=<7-bit-binary> rd=<decimal> rs1=<decimal> rs2=<decimal> funct3=<decimal> funct7=<7-bit-binary>
```

**I-type:**
```
Type=I opcode=<7-bit-binary> rd=<decimal> rs1=<decimal> funct3=<decimal> imm=<signed-decimal>
```

**S-type:**
```
Type=S opcode=<7-bit-binary> rs1=<decimal> rs2=<decimal> funct3=<decimal> imm=<signed-decimal>
```

**B-type:**
```
Type=B opcode=<7-bit-binary> rs1=<decimal> rs2=<decimal> funct3=<decimal> imm=<signed-decimal>
```

**U-type:**
```
Type=U opcode=<7-bit-binary> rd=<decimal> imm=<signed-decimal>
```

**J-type:**
```
Type=J opcode=<7-bit-binary> rd=<decimal> imm=<signed-decimal>
```

**Unknown:**
```
UNKNOWN
```

Notes on field values:
- `opcode` is printed as a 7-character binary string (e.g., `0110011`).
- `funct7` is printed as a 7-character binary string.
- `rd`, `rs1`, `rs2`, `funct3` are unsigned decimal integers.
- `imm` for I, S, B, J types is **sign-extended** and printed as a **signed decimal** (may be negative).
- `imm` for U-type is the **sign-extended 20-bit immediate** field (bits [31:12] of the instruction word >> 12), printed as a signed decimal.

## Field Extraction Rules

**R-type:**
- funct7 = bits[31:25]
- rs2    = bits[24:20]
- rs1    = bits[19:15]
- funct3 = bits[14:12]
- rd     = bits[11:7]

**I-type:**
- imm[11:0] = bits[31:20], sign-extended to 32 bits
- rs1 = bits[19:15], funct3 = bits[14:12], rd = bits[11:7]

**S-type:**
- imm = sign_extend({bits[31:25], bits[11:7]}, 12)
- rs2 = bits[24:20], rs1 = bits[19:15], funct3 = bits[14:12]

**B-type:**
- imm = sign_extend({bit[31], bit[7], bits[30:25], bits[11:8], 0}, 13)
- rs2 = bits[24:20], rs1 = bits[19:15], funct3 = bits[14:12]

**U-type:**
- imm = sign_extend(bits[31:12], 20)   (the 20-bit field value, NOT shifted)
- rd = bits[11:7]

**J-type:**
- imm = sign_extend({bit[31], bits[19:12], bit[20], bits[30:21], 0}, 21)
- rd = bits[11:7]

## Sample Input

```
00A58533
00050513
FE112E23
FE208CE3
000052B7
FF5FF06F
```

## Sample Output

```
Type=R opcode=0110011 rd=10 rs1=11 rs2=10 funct3=0 funct7=0000000
Type=I opcode=0010011 rd=10 rs1=10 funct3=0 imm=0
Type=S opcode=0100011 rs1=2 rs2=1 funct3=2 imm=-4
Type=B opcode=1100011 rs1=1 rs2=2 funct3=0 imm=-8
Type=U opcode=0110111 rd=5 imm=5
Type=J opcode=1101111 rd=0 imm=-12
```

## Explanation of Sample

**00A58533** = `0000 0000 1010 0101 1000 0101 0011 0011`
- opcode = 0110011 (R-type)
- rd=10, rs1=11, rs2=10, funct3=0, funct7=0000000

**000052B7** = LUI x5, 5 → U-type, rd=5, imm = bits[31:12] = 5 (0x00005), printed as 5.

**FF5FF06F** = JAL x0, -12 → J-type, rd=0, imm = -12.

## Constraints

- 1 ≤ number of instructions ≤ 200.
- Each input line is exactly 8 uppercase or lowercase hexadecimal characters.
- Input instructions are valid 32-bit values.
- Use only the Python standard library.
- Time limit: 3000 ms
- Memory limit: 256 MB
