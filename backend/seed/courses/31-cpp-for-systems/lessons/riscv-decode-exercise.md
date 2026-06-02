# Exercise: Decode RISC-V R-Type Instructions

In this exercise you will implement a decoder for **RISC-V R-type** instructions and print the disassembly. This is the core skill tested in every virtual-prototype and compiler-backend interview: given a 32-bit word, extract the fields and identify the operation.

## What You Will Implement

Given a sequence of 32-bit instruction words (in hexadecimal), your program must:

1. Extract `opcode`, `rd`, `funct3`, `rs1`, `rs2`, and `funct7` using bitwise shifts and masks.
2. Identify the mnemonic (`ADD`, `SUB`, `AND`, `OR`, `XOR`, `SLL`, `SRL`, `SRA`, `SLT`, `SLTU`).
3. Print one line of disassembly per instruction in the format `MNEMONIC x<rd>, x<rs1>, x<rs2>`.
4. Print `UNKNOWN` if the encoding does not match a known R-type operation.

## Background

All R-type instructions share `opcode = 0x33`. The mnemonic is determined by the `funct3` field (bits [14:12]) and, for `ADD`/`SUB` and `SRL`/`SRA`, the `funct7` field (bits [31:25]).

```
Bit layout:
 31      25 24  20 19  15 14  12 11   7 6      0
 [funct7 ] [ rs2 ] [ rs1 ] [fn3] [ rd  ] [opcode]
```

## Input / Output

- **Input:** one 32-bit hex value per line (no `0x` prefix).
- **Output:** one disassembly line per input line.

## Example

Input:
```
00B50533
40B50533
```

Output:
```
ADD x10, x10, x11
SUB x10, x10, x11
```

## Starter Hint

```python
def decode(word):
    opcode = word & 0x7F
    rd     = (word >>  7) & 0x1F
    funct3 = (word >> 12) & 0x07
    rs1    = (word >> 15) & 0x1F
    rs2    = (word >> 20) & 0x1F
    funct7 = (word >> 25) & 0x7F
    # your logic here ...
```

Open the coding environment and implement the full decoder. Refer to the **Instruction Encoding Basics** lesson for the funct3/funct7 table.
