# Prompt: Reconstruct a B-Type Immediate

## Problem Statement

Given one or more 32-bit RISC-V B-type instruction words (as 8-character hexadecimal strings, no `0x` prefix), decode the B-type immediate and the branch fields, and print results to standard output.

For each instruction, print a single line:

```
imm=<signed_decimal> funct3=<n> rs1=<n> rs2=<n>
```

Where:
- `imm` is the reconstructed signed 13-bit PC-relative offset (always even, range -4096 to +4094)
- `funct3` is the 3-bit branch discriminator (0–7, decimal)
- `rs1` and `rs2` are register numbers (0–31, decimal)

## Field Positions

All inputs are guaranteed to have opcode `1100011` (B-type branch). Fields:

| Field      | Instruction bits | Immediate bits |
|------------|-----------------|----------------|
| imm[12]    | [31]            | sign bit       |
| imm[10:5]  | [30:25]         | —              |
| rs2        | [24:20]         | —              |
| rs1        | [19:15]         | —              |
| funct3     | [14:12]         | —              |
| imm[4:1]   | [11:8]          | —              |
| imm[11]    | [7]             | —              |
| opcode     | [6:0]           | —              |

Reconstruction:

```
imm = { imm[12], imm[11], imm[10:5], imm[4:1], 0 }
    = (imm12 << 12) | (imm11 << 11) | (imm10_5 << 5) | (imm4_1 << 1)
```

Sign-extend from bit 12: if bit 12 of the raw value is 1, subtract 2^13.

## Constraints

- 1 <= number of instructions <= 200
- All input instructions have opcode `1100011` (you do not need to validate this).
- Each line is exactly 8 hex characters (case-insensitive).
- Output lines must match exactly (no trailing spaces, fields separated by single spaces).

## Sample Input

```
0020CA63
FE208EE3
00209063
FEC4C4E3
01F45063
00308463
```

## Sample Output

```
imm=20 funct3=4 rs1=1 rs2=2
imm=-4 funct3=0 rs1=1 rs2=2
imm=0 funct3=1 rs1=1 rs2=2
imm=-24 funct3=4 rs1=9 rs2=12
imm=0 funct3=5 rs1=8 rs2=31
imm=8 funct3=0 rs1=1 rs2=3
```

## Derivation Notes

**Case 1: `0020CA63` — `blt x1, x2, +20`**
- bit31=0 → imm[12]=0
- bits[30:25]=000000 → imm[10:5]=0
- bits[24:20]=00010 → rs2=2
- bits[19:15]=00001 → rs1=1
- bits[14:12]=100 → funct3=4 (BLT, signed less-than)
- bits[11:8]=1010 → imm[4:1]=10, contributes 10×2=20 to raw
- bit7=0 → imm[11]=0
- raw = 0|(0<<11)|(0<<5)|(10<<1) = 20; sign bit clear → imm=20 ✓

**Case 2: `FE208EE3` — `beq x1, x2, -4`**
- bit31=1 → imm[12]=1 (negative offset)
- bits[30:25]=110000 → imm[10:5]=48
- bits[24:20]=00010 → rs2=2
- bits[19:15]=00001 → rs1=1
- bits[14:12]=000 → funct3=0 (BEQ)
- bits[11:8]=0111 → imm[4:1]=7, contributes 14
- bit7=0 → imm[11]=0
- raw = (1<<12)|(0<<11)|(48<<5)|(7<<1) = 4096+1536+14 = 5646... 
  actually: (1<<12)=4096, (48<<5)=1536, (7<<1)=14; raw=5646
  bit12 of raw is set (5646 >= 4096), so imm = 5646 - 8192 = -2546...

Let me recalculate: bits[30:25] of 0xFE208EE3:
- 0xFE = 1111 1110, so bit31=1, bit30=1,29=1,28=1,27=1,26=1,25=1
- bits[30:25] = 111111 = 63
- bits[11:8] of 0xFE208EE3: 0x8E=1000 1110 → bit11=1, bit10=0, bit9=0, bit8=0... wait
  0xFE208EE3: byte at positions 11-8 is from 0x8E (bits15-8): 0x8E=1000 1110
  bits[11:8] = bits from 0x8E positions [3:0] = 1110 → imm[4:1]=14? No:
  
  0xFE208EE3 = 1111 1110 0010 0000 1000 1110 1110 0011
  bits[11:8] = 1110 → imm[4:1] = 14, contributes 14<<1=28
  bit7 = 1 → imm[11] = 1
  bits[30:25] = 111111 → imm[10:5] = 63, contributes 63<<5=2016
  imm12 = 1
  
  raw = (1<<12)|(1<<11)|(63<<5)|(14<<1) = 4096+2048+2016+28 = 8188
  bit12 set → imm = 8188 - 8192 = -4 ✓

## Notes

- `imm=0` is valid (a branch that targets its own instruction — a spin-wait if condition never clears).
- Negative offsets jump backwards; this is the normal pattern for loop back-edges.
- The implied LSB zero means `imm` is always even — an odd result indicates a reconstruction bug.
