# Decode Opcode and Operand Fields from an Instruction Word

In this exercise you will write a RISC-V RV32I instruction decoder. Given a 32-bit instruction word encoded in hexadecimal, your program must identify the instruction format, extract all relevant fields, and print them in a structured format.

## What You Will Implement

A Python program that:

1. Reads one or more 32-bit hex instruction words from standard input (one per line).
2. For each instruction, determines the instruction format (R, I, S, B, U, J) by examining bits `[6:0]` (the opcode field).
3. Extracts and prints every relevant field: opcode bits, instruction format, `rd`, `rs1`, `rs2`, `funct3`, `funct7`, and the sign-extended immediate (where applicable).
4. Outputs a fixed multi-line block per instruction as described in the prompt file.

## Skills Reinforced

- Bitwise masking and shifting to extract sub-fields from a 32-bit word.
- Sign extension from a sub-word integer to a full 32-bit signed value.
- Recognizing RISC-V instruction formats from the opcode field alone.
- Understanding the distinction between R-type (register-register) and I-type (register-immediate) encodings.

## What to Submit

A single Python file that reads from `stdin` and writes decoded field information to `stdout` exactly as specified. No third-party libraries are permitted — use only the Python standard library.

## Quick Reference: RISC-V RV32I Opcode Map

| Opcode (hex) | Format | Instruction family |
|---|---|---|
| 0x33 | R | Integer register-register (ADD, SUB, AND, …) |
| 0x13 | I | Integer register-immediate (ADDI, SLTI, …) |
| 0x03 | I | Loads (LW, LH, LB, …) |
| 0x23 | S | Stores (SW, SH, SB) |
| 0x63 | B | Conditional branches (BEQ, BNE, BLT, …) |
| 0x37 | U | LUI |
| 0x17 | U | AUIPC |
| 0x6F | J | JAL |
| 0x67 | I | JALR |

Good luck — precise bit manipulation is the heart of every hardware decoder!
