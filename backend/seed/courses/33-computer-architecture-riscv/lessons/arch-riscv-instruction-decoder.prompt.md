# Prompt: Decode a 32-Bit RISC-V Instruction

## Problem Statement

Write a program that reads one or more 32-bit RISC-V RV32I instruction words (given as 8-character hexadecimal strings, no `0x` prefix) from standard input and decodes each one to standard output.

For each instruction print a single line in the following format depending on the format:

```
R rd=<n> rs1=<n> rs2=<n> funct3=<n> funct7=<n>
I rd=<n> rs1=<n> imm=<signed_decimal> funct3=<n>
S rs1=<n> rs2=<n> imm=<signed_decimal> funct3=<n>
B rs1=<n> rs2=<n> imm=<signed_decimal> funct3=<n>
U rd=<n> imm=<unsigned_decimal>
J rd=<n> imm=<signed_decimal>
UNKNOWN
```

Where `<n>` values are decimal integers with no leading zeros. Register numbers are 0–31. `imm` values:
- I-type: sign-extended 12-bit immediate (range -2048 to 2047)
- S-type: sign-extended 12-bit immediate
- B-type: sign-extended 13-bit immediate (always even)
- U-type: the value stored in upper bits shifted left by 12 (always a multiple of 4096, always non-negative as a 32-bit unsigned value — print as unsigned decimal)
- J-type: sign-extended 21-bit immediate (always even)

Print `UNKNOWN` for any opcode not listed below.

## Opcode Table

| opcode (binary) | Format |
|-----------------|--------|
| 0110011         | R      |
| 0010011         | I      |
| 0000011         | I      |
| 1100111         | I      |
| 1110011         | I      |
| 0100011         | S      |
| 1100011         | B      |
| 0110111         | U      |
| 0010111         | U      |
| 1101111         | J      |

## Field Extraction Rules

**R-type** (inst bits):
- funct7 = inst[31:25]
- rs2    = inst[24:20]
- rs1    = inst[19:15]
- funct3 = inst[14:12]
- rd     = inst[11:7]

**I-type**:
- imm[11:0] = inst[31:20] (sign-extend to 32 bits)
- rs1       = inst[19:15]
- funct3    = inst[14:12]
- rd        = inst[11:7]

**S-type**:
- imm = sign_extend({ inst[31:25], inst[11:7] }, 12)
- rs2    = inst[24:20]
- rs1    = inst[19:15]
- funct3 = inst[14:12]

**B-type**:
- imm = sign_extend({ inst[31], inst[7], inst[30:25], inst[11:8], 0 }, 13)
- rs2    = inst[24:20]
- rs1    = inst[19:15]
- funct3 = inst[14:12]

**U-type**:
- imm = (inst & 0xFFFFF000)  [treat as unsigned 32-bit]
- rd  = inst[11:7]

**J-type**:
- imm = sign_extend({ inst[31], inst[19:12], inst[20], inst[30:21], 0 }, 21)
- rd  = inst[11:7]

## Constraints

- 1 <= number of instructions <= 100
- Each line contains exactly 8 hexadecimal characters (lowercase or uppercase).
- Instruction words are valid 32-bit values.
- You may assume inputs always fall into one of the listed opcode groups or should produce `UNKNOWN`.

## Sample Input

```
00208233
00C12283
00512A23
00208A63
12345037
064000EF
```

## Sample Output

```
R rd=4 rs1=1 rs2=2 funct3=0 funct7=0
I rd=5 rs1=2 imm=12 funct3=2
S rs1=2 rs2=5 imm=20 funct3=2
B rs1=1 rs2=2 imm=20 funct3=0
U rd=0 imm=305418240
J rd=1 imm=100
```

## Notes

- For U-type, `imm` is the full 32-bit word with lower 12 bits zeroed, printed as a plain unsigned decimal integer. Example: `lui x0, 0x12345` → imm = 0x12345000 = 305418240.
- For B-type and J-type the immediate already has bit 0 = 0 from the reconstruction (the implied LSB zero).
- funct3 and funct7 are printed as unsigned decimal (0–7 for funct3, 0–127 for funct7).
