# Exercise: Decode a 32-bit RISC-V Instruction

In this exercise you will implement a RISC-V instruction decoder — the first step every ISS performs. Given a 32-bit integer encoding of a RISC-V RV32I instruction, your program will extract the opcode, destination register (rd), source registers (rs1, rs2), function codes (funct3, funct7), and the immediate value (for I-, S-, B-, U-, and J-type formats).

## Background

RISC-V uses fixed 32-bit instruction words with a consistent 7-bit opcode field in bits [6:0]. The remaining bits are partitioned differently depending on the instruction format.

| Format | Fields |
|---|---|
| R-type | funct7, rs2, rs1, funct3, rd, opcode |
| I-type | imm[11:0], rs1, funct3, rd, opcode |
| S-type | imm[11:5], rs2, rs1, funct3, imm[4:0], opcode |
| B-type | imm[12,10:5], rs2, rs1, funct3, imm[4:1,11], opcode |
| U-type | imm[31:12], rd, opcode |
| J-type | imm[20,10:1,11,19:12], rd, opcode |

You will determine the format from the opcode, extract all fields, and sign-extend immediates where required.

## What You Will Implement

Your program reads one hex-encoded 32-bit instruction word per line from stdin and prints the decoded fields for each instruction. The decoder must:

1. Extract the 7-bit opcode (bits 6–0).
2. Determine the instruction format from the opcode.
3. Extract rd, rs1, rs2, funct3, funct7 as applicable (print 0 when the field does not exist in the format).
4. Compute the sign-extended immediate (print 0 for R-type).
5. Print one line of output per instruction.

This mirrors what the fetch-decode stage of a real ISS does on every instruction boundary.
