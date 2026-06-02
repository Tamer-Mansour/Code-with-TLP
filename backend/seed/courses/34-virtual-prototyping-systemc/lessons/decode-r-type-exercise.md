# Decode an R-Type Instruction

## Background

R-type instructions perform register-to-register operations. Every R-type instruction packs six fields into a 32-bit word:

```
Bits [6:0]   → opcode  (0110011 for integer ALU)
Bits [11:7]  → rd      (destination register)
Bits [14:12] → funct3  (selects sub-operation)
Bits [19:15] → rs1     (source register 1)
Bits [24:20] → rs2     (source register 2)
Bits [31:25] → funct7  (further qualifies operation)
```

The combination of `opcode + funct3 + funct7` uniquely identifies the instruction. For example:

| Instruction | opcode    | funct3 | funct7    |
|-------------|-----------|--------|-----------|
| ADD         | 0110011   | 000    | 0000000   |
| SUB         | 0110011   | 000    | 0100000   |
| AND         | 0110011   | 111    | 0000000   |
| OR          | 0110011   | 110    | 0000000   |
| XOR         | 0110011   | 100    | 0000000   |
| SLL         | 0110011   | 001    | 0000000   |
| SRL         | 0110011   | 101    | 0000000   |
| SRA         | 0110011   | 101    | 0100000   |

## What You Will Implement

You will write a Python program that reads a 32-bit RISC-V instruction (given as a hexadecimal number) and:

1. Extracts all six fields using bitwise operations.
2. Determines whether the instruction is ADD, SUB, AND, OR, XOR, SLL, SRL, or SRA.
3. Prints each field and the decoded mnemonic.

### Input Format

A single line containing one 32-bit hexadecimal value (no `0x` prefix, 8 hex digits).

### Output Format

Exactly six lines:

```
opcode=<7-bit binary>
rd=<decimal>
funct3=<3-bit binary>
rs1=<decimal>
rs2=<decimal>
funct7=<7-bit binary>
mnemonic=<MNEMONIC or UNKNOWN>
```

### Sample Interaction

Input:
```
00208033
```

Output:
```
opcode=0110011
rd=0
funct3=000
rs1=1
rs2=2
funct7=0000000
mnemonic=ADD
```

Explanation: `0x00208033` = 0b 0000000 00010 00001 000 00000 0110011, which is `ADD x0, x1, x2`.

## Your Task

Open the prompt file for the full specification and test cases, then implement the solution in Python using only the standard library.

Key bitwise operations to use:

```python
instr  = int(hex_str, 16)
opcode = instr & 0x7F
rd     = (instr >> 7)  & 0x1F
funct3 = (instr >> 12) & 0x07
rs1    = (instr >> 15) & 0x1F
rs2    = (instr >> 20) & 0x1F
funct7 = (instr >> 25) & 0x7F
```

Focus on correctness over cleverness — a chain of `if/elif` statements keyed on `(funct3, funct7)` is perfectly acceptable.
