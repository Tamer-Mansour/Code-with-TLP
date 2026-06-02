# Exercise: Extract Opcode Fields from an Instruction Word

In this exercise you will implement a RISC-V instruction decoder that extracts each named field from a 32-bit RISC-V RV32I instruction word.

## Background

Every 32-bit RISC-V instruction encodes multiple fields at fixed bit positions. Because `rs1`, `rd`, and the primary `opcode` are always at the same bit positions regardless of the instruction type, a hardware decoder can read the register file and begin decoding in parallel.

The field layout for all formats:

```
Bits [6:0]   → opcode   (7 bits)
Bits [11:7]  → rd       (5 bits)
Bits [14:12] → funct3   (3 bits)
Bits [19:15] → rs1      (5 bits)
Bits [24:20] → rs2      (5 bits)  — R-type and S/B-type only
Bits [31:25] → funct7   (7 bits)  — R-type only
```

## What You Will Implement

Write a program that:

1. Reads a number `N` of 32-bit instruction words given as unsigned decimal integers (one per line).
2. For each word, extracts and prints the six fields on a single line in the format:

```
opcode=<val> rd=<val> funct3=<val> rs1=<val> rs2=<val> funct7=<val>
```

All values are printed as **decimal integers**.

## Skills Practiced

- Bit masking and shifting in Python.
- Understanding RISC-V R-type and I-type encoding layouts.
- Writing clean, reusable field-extraction logic.

See the exercise prompt for exact input/output specification, constraints, and sample test cases.
