# Prompt: Decode an R-Type RISC-V Instruction

## Problem Statement

Given a 32-bit RISC-V instruction encoded as an 8-character hexadecimal string, decode it as an R-type instruction and print all fields plus the mnemonic.

You may assume the input is always a valid R-type instruction (opcode = 0110011 binary = 0x33) belonging to the set: ADD, SUB, AND, OR, XOR, SLL, SRL, SRA.

## Input Format

A single line containing exactly 8 hexadecimal characters (uppercase or lowercase, no `0x` prefix) representing a 32-bit little-endian RISC-V instruction word.

## Output Format

Print exactly 7 lines in the following order:

```
opcode=<7-bit binary string>
rd=<decimal integer>
funct3=<3-bit binary string>
rs1=<decimal integer>
rs2=<decimal integer>
funct7=<7-bit binary string>
mnemonic=<MNEMONIC>
```

- Binary strings must have exactly the stated width (zero-padded on the left).
- Decimal integers have no leading zeros.
- MNEMONIC is one of: ADD, SUB, AND, OR, XOR, SLL, SRL, SRA, UNKNOWN.

## Field Extraction Rules

```
opcode  = instr[6:0]   (bits 6 down to 0)
rd      = instr[11:7]
funct3  = instr[14:12]
rs1     = instr[19:15]
rs2     = instr[24:20]
funct7  = instr[31:25]
```

## Mnemonic Lookup Table

| funct7    | funct3 | Mnemonic |
|-----------|--------|----------|
| 0000000   | 000    | ADD      |
| 0100000   | 000    | SUB      |
| 0000000   | 111    | AND      |
| 0000000   | 110    | OR       |
| 0000000   | 100    | XOR      |
| 0000000   | 001    | SLL      |
| 0000000   | 101    | SRL      |
| 0100000   | 101    | SRA      |

Any other combination → UNKNOWN.

## Constraints

- Input is exactly one line, 8 hex characters.
- No external libraries; use only Python standard library.
- Output comparison is case-sensitive and exact.

## Sample Input 1

```
00208033
```

## Sample Output 1

```
opcode=0110011
rd=0
funct3=000
rs1=1
rs2=2
funct7=0000000
mnemonic=ADD
```

## Sample Input 2

```
40B50533
```

## Sample Output 2

```
opcode=0110011
rd=10
funct3=000
rs1=10
rs2=11
funct7=0100000
mnemonic=SUB
```

Explanation: `0x40B50533` = funct7=0100000, rs2=01011 (11), rs1=01010 (10), funct3=000, rd=01010 (10), opcode=0110011 → SUB x10, x10, x11.
