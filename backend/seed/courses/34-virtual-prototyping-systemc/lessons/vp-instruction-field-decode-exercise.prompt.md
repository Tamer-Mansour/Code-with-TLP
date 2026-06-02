# Exercise Prompt: Decode Opcode and Operand Fields from an Instruction Word

## Problem Statement

You are implementing the decode stage of a RISC-V RV32I CPU model. Given one or more 32-bit instruction words (each on its own line, encoded as an 8-character lowercase hexadecimal string without the `0x` prefix), decode and print each instruction's fields.

## Input Format

- One or more lines, each containing exactly one 8-character lowercase hexadecimal number (32-bit instruction word).
- No extra whitespace. No blank lines between instructions.

## Output Format

For each instruction word, print the following lines **in this exact order**, separated by a blank line after each instruction block:

```
INSTR: <hex>
FORMAT: <R|I|S|B|U|J>
OPCODE: <7-bit binary string>
RD: <decimal>
RS1: <decimal>
RS2: <decimal or N/A>
FUNCT3: <3-bit binary string or N/A>
FUNCT7: <7-bit binary string or N/A>
IMM: <decimal signed or N/A>
```

Field rules by format:

**R-type** (opcode 0x33):
- RD = bits [11:7], RS1 = bits [19:15], RS2 = bits [24:20]
- FUNCT3 = bits [14:12] (3-bit binary), FUNCT7 = bits [31:25] (7-bit binary)
- IMM = N/A

**I-type** (opcode 0x13, 0x03, 0x67):
- RD = bits [11:7], RS1 = bits [19:15], RS2 = N/A
- FUNCT3 = bits [14:12], FUNCT7 = N/A
- IMM = sign-extended bits [31:20] (12-bit signed, printed as decimal)

**S-type** (opcode 0x23):
- RD = N/A, RS1 = bits [19:15], RS2 = bits [24:20]
- FUNCT3 = bits [14:12], FUNCT7 = N/A
- IMM = sign-extended {bits[31:25], bits[11:7]} (12-bit signed, printed as decimal)

**B-type** (opcode 0x63):
- RD = N/A, RS1 = bits [19:15], RS2 = bits [24:20]
- FUNCT3 = bits [14:12], FUNCT7 = N/A
- IMM = sign-extended {instr[31], instr[7], instr[30:25], instr[11:8], 0} (13-bit, LSB always 0, printed as decimal)

**U-type** (opcode 0x37, 0x17):
- RD = bits [11:7], RS1 = N/A, RS2 = N/A
- FUNCT3 = N/A, FUNCT7 = N/A
- IMM = bits [31:12] zero-extended left-shifted by 12 (i.e., instr & 0xFFFFF000, printed as decimal unsigned)

**J-type** (opcode 0x6F):
- RD = bits [11:7], RS1 = N/A, RS2 = N/A
- FUNCT3 = N/A, FUNCT7 = N/A
- IMM = sign-extended {instr[31], instr[19:12], instr[20], instr[30:21], 0} (21-bit, LSB always 0, printed as decimal)

Print `N/A` (exactly) for fields not applicable to the format.

Print the OPCODE as a 7-character binary string (e.g., `0110011`).
Print FUNCT3 as a 3-character binary string (e.g., `000`).
Print FUNCT7 as a 7-character binary string (e.g., `0000000`).

After each instruction block print one blank line (including after the last instruction).

## Constraints

- 1 <= number of instructions <= 20
- All hex strings are valid 8-character lowercase hex.
- All opcodes will be one of: 0x33, 0x13, 0x03, 0x23, 0x63, 0x37, 0x17, 0x6F, 0x67.

## Sample Input

```
00430293
00628233
fe010113
```

## Sample Output

```
INSTR: 00430293
FORMAT: I
OPCODE: 0010011
RD: 5
RS1: 6
RS2: N/A
FUNCT3: 000
FUNCT7: N/A
IMM: 4

INSTR: 00628233
FORMAT: R
OPCODE: 0110011
RD: 4
RS1: 5
RS2: 6
FUNCT3: 000
FUNCT7: 0000000
IMM: N/A

INSTR: fe010113
FORMAT: I
OPCODE: 0010011
RD: 2
RS1: 2
RS2: N/A
FUNCT3: 000
FUNCT7: N/A
IMM: -32

```

## Explanation of Sample

- `00430293` is `addi x5, x6, 4` — I-type, rd=5, rs1=6, imm=4.
- `00628233` is `add x4, x5, x6` — R-type, rd=4, rs1=5, rs2=6.
- `fe010113` is `addi x2, x2, -32` — I-type, rd=2, rs1=2, imm=-32 (stack pointer adjustment).
