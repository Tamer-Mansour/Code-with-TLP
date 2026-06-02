# Reconstruct a B-Type Branch Immediate

## Background

Branch instructions use B-type encoding. The 13-bit signed PC-relative offset has its bits **scrambled** across the instruction word to keep rs1 and rs2 in their standard positions (shared with S-type decode). Bit 0 of the offset is implicit (always 0, because branch targets must be 2-byte aligned).

The encoding layout:

```
Bit 31       → imm[12]  (sign bit)
Bits [30:25] → imm[10:5]
Bits [24:20] → rs2
Bits [19:15] → rs1
Bits [14:12] → funct3
Bits [11:8]  → imm[4:1]
Bit  7       → imm[11]
Bits [6:0]   → opcode (1100011)
```

Notice that imm[11] lives at bit 7 and imm[12] lives at bit 31 — they are swapped relative to what you might expect. This swap exists so that the sign bit is always at position 31 and the partial imm[4:1] field can share hardware with the S-type imm[4:0] field.

## Reconstruction Algorithm

```python
def decode_b_imm(instr):
    imm12  = (instr >> 31) & 0x1   # bit 31 → imm[12]
    imm11  = (instr >> 7)  & 0x1   # bit 7  → imm[11]
    imm105 = (instr >> 25) & 0x3F  # bits [30:25] → imm[10:5]
    imm41  = (instr >> 8)  & 0xF   # bits [11:8]  → imm[4:1]

    # Reassemble: bit 0 is always 0
    imm = (imm12 << 12) | (imm11 << 11) | (imm105 << 5) | (imm41 << 1)

    # Sign-extend from bit 12
    if imm & 0x1000:
        imm -= 0x2000
    return imm
```

## Branch Mnemonics

The opcode is always `1100011` (decimal 99). `funct3` selects the condition:

| funct3 | Mnemonic | Condition |
|--------|----------|-----------|
| 000    | BEQ      | rs1 == rs2 |
| 001    | BNE      | rs1 != rs2 |
| 100    | BLT      | rs1 < rs2 (signed) |
| 101    | BGE      | rs1 >= rs2 (signed) |
| 110    | BLTU     | rs1 < rs2 (unsigned) |
| 111    | BGEU     | rs1 >= rs2 (unsigned) |

## What You Will Implement

Write a Python program that reads a 32-bit RISC-V B-type instruction (hex) and prints all fields including the reconstructed signed immediate.

### Input Format

A single line: 8 hexadecimal characters (no `0x` prefix).

### Output Format

Exactly 6 lines:

```
opcode=<7-bit binary>
funct3=<3-bit binary>
rs1=<decimal>
rs2=<decimal>
imm=<signed decimal>
mnemonic=<MNEMONIC or UNKNOWN>
```

### Sample Interaction

Input:
```
00209463
```

Output:
```
opcode=1100011
funct3=001
rs1=1
rs2=2
imm=8
mnemonic=BNE
```

Explanation: `BNE x1, x2, 8` — if x1 != x2, jump PC+8.

## Common Pitfalls

- **Forgetting imm[11] and imm[12] swap.** Always re-read the bit positions from the spec before coding.
- **Missing the shift-by-1.** The immediate represents a byte offset but bit[0] is implicit. The assembled bits are for positions [12:1], not [11:0].
- **Off-by-one in sign extension.** The immediate is 13 bits wide (positions 12..0). The sign bit is at position 12, so the sign-extension threshold is `0x1000` (bit 12 set = value >= 4096 as unsigned).
