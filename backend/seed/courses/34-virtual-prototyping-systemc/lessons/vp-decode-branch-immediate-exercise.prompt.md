# Prompt: Reconstruct a B-Type Branch Immediate

## Problem Statement

Given a 32-bit RISC-V B-type branch instruction as an 8-character hex string, extract all fields, reconstruct the 13-bit signed PC-relative immediate, and identify the branch mnemonic.

## Input Format

A single line: exactly 8 hexadecimal characters (upper or lowercase, no `0x` prefix).

The instruction is guaranteed to have opcode = 1100011 (binary) — it is a branch instruction.

## Output Format

Print exactly 6 lines:

```
opcode=<7-bit binary>
funct3=<3-bit binary>
rs1=<decimal>
rs2=<decimal>
imm=<signed decimal>
mnemonic=<MNEMONIC or UNKNOWN>
```

- Binary strings: zero-padded to stated width.
- `imm` is a signed decimal integer; may be negative. No leading zeros. Negative values have a leading minus sign.
- `imm` is always even (bit 0 is implicit zero).

## Field Extraction

```
opcode     = instr[6:0]
funct3     = instr[14:12]
rs1        = instr[19:15]
rs2        = instr[24:20]
imm[12]    = instr[31]
imm[10:5]  = instr[30:25]
imm[4:1]   = instr[11:8]
imm[11]    = instr[7]
imm[0]     = 0  (implicit)
```

Reassemble and sign-extend from bit 12:

```python
imm12  = (instr >> 31) & 0x1
imm11  = (instr >> 7)  & 0x1
imm105 = (instr >> 25) & 0x3F
imm41  = (instr >> 8)  & 0xF
imm = (imm12 << 12) | (imm11 << 11) | (imm105 << 5) | (imm41 << 1)
if imm & 0x1000:
    imm -= 0x2000
```

## Mnemonic Table

| funct3 (bin) | Mnemonic |
|-------------|----------|
| 000         | BEQ      |
| 001         | BNE      |
| 100         | BLT      |
| 101         | BGE      |
| 110         | BLTU     |
| 111         | BGEU     |
| other       | UNKNOWN  |

## Constraints

- Input is exactly one line, 8 hex characters.
- Pure Python standard library only.
- Output is case-sensitive and exact.

## Sample Input 1

```
00209463
```

## Sample Output 1

```
opcode=1100011
funct3=001
rs1=1
rs2=2
imm=8
mnemonic=BNE
```

## Sample Input 2

```
FE0098E3
```

## Sample Output 2

```
opcode=1100011
funct3=001
rs1=1
rs2=0
imm=-16
mnemonic=BNE
```

## Sample Input 3

```
00000063
```

## Sample Output 3

```
opcode=1100011
funct3=000
rs1=0
rs2=0
imm=0
mnemonic=BEQ
```

## Sample Input 4

```
0062C463
```

## Sample Output 4

```
opcode=1100011
funct3=100
rs1=5
rs2=6
imm=8
mnemonic=BLT
```

## Sample Input 5

```
FE10CCE3
```

## Sample Output 5

```
opcode=1100011
funct3=100
rs1=1
rs2=1
imm=-8
mnemonic=BLT
```
