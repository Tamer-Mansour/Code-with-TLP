# Exercise: RISC-V R-Type Instruction Decoder

This exercise bridges the gap between ISA theory and real machine code. You will decode RISC-V R-type instructions from 32-bit hex values by extracting bit fields according to the RISC-V specification.

## Why Fixed-Width Instructions Matter

RISC-V uses fixed 32-bit instructions (in the base ISA), which makes decoding simple and fast. Unlike x86 where instructions range from 1 to 15 bytes and require complex variable-length decoding, RISC-V hardware can begin decoding any instruction immediately by reading exactly 4 bytes.

## Bit Field Extraction

R-type instructions pack six fields into 32 bits:

```
31      25 24   20 19   15 14  12 11    7 6      0
|funct7(7)| rs2(5) | rs1(5) |funct3(3)| rd(5) |opcode(7)|
```

Key operations in RISC-V R-type (opcode=51):

| funct7 | funct3 | Operation |
|--------|--------|-----------|
| 0      | 000    | ADD       |
| 32     | 000    | SUB       |
| 0      | 110    | OR        |
| 0      | 111    | AND       |
| 0      | 100    | XOR       |
| 0      | 001    | SLL       |
| 0      | 101    | SRL       |

## Challenge

Parse each hex instruction and extract all six fields in decimal. Use bit shifting and masking — no string slicing.

## Further Reading

- **x86-64 Assembly Language Programming with Ubuntu** by Ed Jorgensen (https://open.umn.edu/opentextbooks/textbooks/x86-64-assembly-language-programming-with-ubuntu) — contrasts RISC fixed-format encoding with the variable-length x86 approach.
- **MIT 6.823 Computer System Architecture** (https://ocw.mit.edu/courses/6-823-computer-system-architecture-fall-2005/) — covers ISA design tradeoffs including instruction encoding.
