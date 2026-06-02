# Prompt: Decode an I-Type RISC-V Instruction and Its Immediate

## Problem Statement

Given a 32-bit RISC-V instruction encoded as an 8-character hex string, decode it as an I-type instruction. Extract all fields, sign-extend the 12-bit immediate, and identify the mnemonic.

## Input Format

A single line: exactly 8 hexadecimal characters (upper or lowercase, no `0x` prefix).

The instruction is guaranteed to be one of the following opcodes (binary): 0010011 (immediate ALU), 0000011 (load), or 1100111 (JALR).

## Output Format

Print exactly 6 lines:

```
opcode=<7-bit binary>
rd=<decimal>
funct3=<3-bit binary>
rs1=<decimal>
imm=<signed decimal>
mnemonic=<MNEMONIC or UNKNOWN>
```

- Binary strings: zero-padded to exact stated width.
- `imm` is the sign-extended 12-bit immediate as a signed decimal integer (may be negative).
- No leading zeros on decimal fields; negative numbers use a leading minus sign.

## Mnemonic Lookup Table

| opcode (bin) | funct3 | Mnemonic |
|-------------|--------|----------|
| 0010011     | 000    | ADDI     |
| 0010011     | 010    | SLTI     |
| 0010011     | 100    | XORI     |
| 0010011     | 110    | ORI      |
| 0010011     | 111    | ANDI     |
| 0000011     | 000    | LB       |
| 0000011     | 001    | LH       |
| 0000011     | 010    | LW       |
| 0000011     | 100    | LBU      |
| 0000011     | 101    | LHU      |
| 1100111     | 000    | JALR     |

Any other combination → UNKNOWN.

## Sign Extension Rule

The immediate occupies bits [31:20] as a 12-bit two's-complement value.

```python
imm12 = (instr >> 20) & 0xFFF
if imm12 & 0x800:
    imm12 -= 0x1000
```

## Constraints

- Input is exactly one line, 8 hex characters.
- Pure Python standard library only.
- Output is case-sensitive and exact.

## Sample Input 1

```
00A08513
```

## Sample Output 1

```
opcode=0010011
rd=10
funct3=000
rs1=1
imm=10
mnemonic=ADDI
```

## Sample Input 2

```
FFF00513
```

## Sample Output 2

```
opcode=0010011
rd=10
funct3=000
rs1=0
imm=-1
mnemonic=ADDI
```

Explanation: imm bits [31:20] = 0xFFF = 4095; sign bit set → 4095 - 4096 = -1.

## Sample Input 3

```
0040A303
```

## Sample Output 3

```
opcode=0000011
rd=6
funct3=010
rs1=1
imm=4
mnemonic=LW
```

Explanation: `LW x6, 4(x1)` — load word from address rs1+4 into rd.
