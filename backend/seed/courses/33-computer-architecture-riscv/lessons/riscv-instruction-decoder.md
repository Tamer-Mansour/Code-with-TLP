# Exercise: Decode a 32-Bit RISC-V Instruction

In this exercise you will implement a RISC-V RV32I instruction decoder. Given a 32-bit hexadecimal instruction word, your program must identify the instruction format, extract all fields, reconstruct any immediate, and print a human-readable summary.

## What You Will Implement

Your decoder must handle the following instruction types by examining the opcode field (bits [6:0]) and, where needed, funct3 and funct7:

- **R-type** (opcode `0110011`): extract funct7, rs2, rs1, funct3, rd
- **I-type** (opcodes `0010011`, `0000011`, `1100111`, `1110011`): extract imm[11:0], rs1, funct3, rd; sign-extend the immediate
- **S-type** (opcode `0100011`): reassemble imm from bits [31:25] and [11:7]; sign-extend
- **B-type** (opcode `1100011`): reassemble imm from bits [31], [30:25], [11:8], [7]; sign-extend
- **U-type** (opcodes `0110111`, `0010111`): extract imm[31:12], shift left by 12
- **J-type** (opcode `1101111`): reassemble imm from bits [31], [19:12], [20], [30:21]; sign-extend

## Input / Output

- Input: one hexadecimal instruction word per line (8 hex digits, no `0x` prefix).
- Output: one decoded line per instruction in the format described in the prompt file.

## Skills Practiced

- Bitwise extraction with masks and shifts
- Sign extension from arbitrary bit widths
- Understanding how the six RISC-V formats differ in field positions
- Thinking like a hardware decoder pipeline

Work through the encoding tables in the reading lessons before writing code. Start by isolating the opcode, then branch on format, then extract each field in order from MSB to LSB.
