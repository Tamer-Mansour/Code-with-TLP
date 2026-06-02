# Decode an I-Type Instruction and Its Immediate

## Background

I-type instructions carry a 12-bit signed immediate value that is sign-extended to XLEN (32 bits for RV32I) before use. They cover loads, immediate arithmetic, and the `JALR` jump instruction.

The field layout is:

```
Bits [6:0]   → opcode
Bits [11:7]  → rd       (destination register)
Bits [14:12] → funct3   (selects sub-operation)
Bits [19:15] → rs1      (source register)
Bits [31:20] → imm[11:0] (12-bit signed immediate, contiguous)
```

Because the immediate is a single contiguous field at the top of the word, extraction is a single arithmetic right-shift:

```python
# Python handles sign extension via arithmetic right shift on signed integers
raw = int(hex_str, 16)
# Treat as signed 32-bit first
if raw >= 0x80000000:
    raw -= 0x100000000
imm = raw >> 20   # arithmetic right shift preserves sign bit
```

## Common I-Type Opcodes and funct3

| Instruction | opcode   | funct3 | Notes |
|-------------|----------|--------|-------|
| ADDI        | 0010011  | 000    | rd = rs1 + imm |
| SLTI        | 0010011  | 010    | rd = (rs1 < imm) signed |
| XORI        | 0010011  | 100    | rd = rs1 ^ imm |
| ORI         | 0010011  | 110    | rd = rs1 \| imm |
| ANDI        | 0010011  | 111    | rd = rs1 & imm |
| LW          | 0000011  | 010    | Load word |
| LH          | 0000011  | 001    | Load halfword signed |
| LB          | 0000011  | 000    | Load byte signed |
| LHU         | 0000011  | 101    | Load halfword unsigned |
| LBU         | 0000011  | 100    | Load byte unsigned |
| JALR        | 1100111  | 000    | Jump and link register |

## What You Will Implement

Write a Python program that reads a 32-bit RISC-V instruction (hex) and:

1. Extracts all I-type fields.
2. Sign-extends the 12-bit immediate to a Python integer (may be negative).
3. Decodes the mnemonic from the opcode + funct3 table above.
4. Prints each field.

### Input Format

A single line: 8 hexadecimal characters (no `0x` prefix).

### Output Format

Exactly 6 lines:

```
opcode=<7-bit binary>
rd=<decimal>
funct3=<3-bit binary>
rs1=<decimal>
imm=<signed decimal>
mnemonic=<MNEMONIC or UNKNOWN>
```

### Sample Interaction

Input:
```
00A08513
```

Output:
```
opcode=0010011
rd=10
funct3=000
rs1=1
imm=10
mnemonic=ADDI
```

Explanation: `0x00A08513` → imm=0x00A=10, rs1=1 (x1), funct3=000, rd=10 (a0), opcode=0010011 → `ADDI a0, ra, 10`.

## Key Insight: Sign Extension

A 12-bit immediate with bit [11] = 1 represents a negative number. When you shift right by 20 on a 32-bit signed integer, Python's arbitrary-precision integers handle this automatically if you first convert to a signed 32-bit value.

```python
def sign_ext_12(val_32bit):
    """Extract and sign-extend the 12-bit I-type immediate."""
    imm12 = (val_32bit >> 20) & 0xFFF
    if imm12 & 0x800:          # bit 11 set → negative
        imm12 -= 0x1000
    return imm12
```

Practise with `0xFFF00513` (ADDI x10, x0, -1) — the immediate should be −1.
