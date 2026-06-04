# RISC-V Instruction Decoder: Full Field Extraction

Decoding a raw 32-bit RISC-V machine instruction into its component fields is one of the most concrete exercises in understanding the ISA encoding. It grounds abstract format descriptions in real bit manipulation.

## Why the Formats Are Designed This Way

RISC-V instruction formats are carefully structured so that:

1. **The sign bit of every immediate is always at bit 31** of the instruction word — this means hardware only needs one sign-extension input regardless of format.
2. **Register specifiers (rs1, rs2, rd) are always at the same bit positions** across all formats — the register file can begin reading in parallel with decoding.

These constraints drive what appears to be "scrambled" immediate encoding in B-type and J-type instructions. The scrambling is not arbitrary; it minimizes critical path length in the decode stage.

## Format Quick Reference

| Format | Opcode [6:0] | Fields present |
|--------|-------------|----------------|
| R      | 0110011     | rd, rs1, rs2, funct3, funct7 |
| I      | 0010011, 0000011, 1100111 | rd, rs1, funct3, imm[11:0] |
| S      | 0100011     | rs1, rs2, funct3, imm[11:0] (split) |
| B      | 1100011     | rs1, rs2, funct3, imm[12:1] (scattered) |
| U      | 0110111, 0010111 | rd, imm[31:12] |
| J      | 1101111     | rd, imm[20:1] (scattered) |

## Field Extraction by Format

### R-Type (opcode 0110011 — register-register ALU)

```
31       25 24    20 19    15 14   12 11    7 6      0
[  funct7  ][  rs2  ][  rs1  ][ fn3 ][  rd  ][ opcode]
```

```python
funct7 = (instr >> 25) & 0x7F
rs2    = (instr >> 20) & 0x1F
rs1    = (instr >> 15) & 0x1F
funct3 = (instr >> 12) & 0x07
rd     = (instr >> 7)  & 0x1F
```

### I-Type (opcode 0010011, 0000011, 1100111 — ALU-imm, loads, JALR)

```
31          20 19    15 14   12 11    7 6      0
[  imm[11:0]  ][  rs1  ][ fn3 ][  rd  ][ opcode]
```

The immediate is a **sign-extended 12-bit value**:

```python
imm_raw = (instr >> 20) & 0xFFF
# Sign-extend bit 11
imm = imm_raw if (imm_raw < 2048) else (imm_raw - 4096)
```

### S-Type (opcode 0100011 — stores)

The immediate is split to keep rs2 at bits [24:20]:

```
31       25 24    20 19    15 14   12 11    7 6      0
[ imm[11:5] ][  rs2  ][  rs1  ][ fn3 ][ imm[4:0]][ opcode]
```

```python
imm_hi  = (instr >> 25) & 0x7F
imm_lo  = (instr >> 7)  & 0x1F
imm_raw = (imm_hi << 5) | imm_lo
imm = imm_raw if (imm_raw < 2048) else (imm_raw - 4096)
```

### B-Type (opcode 1100011 — conditional branches)

The immediate encodes a **byte offset to a 2-byte-aligned target** (bit 0 is always 0, not stored):

```
31  30      25 24    20 19    15 14   12 11   8  7   6      0
[12][ imm[10:5]][ rs2  ][  rs1  ][ fn3 ][im[4:1]][11][opcode]
```

```python
bit12  = (instr >> 31) & 1
bit11  = (instr >> 7)  & 1
bits10_5 = (instr >> 25) & 0x3F
bits4_1  = (instr >> 8)  & 0xF
imm_raw = (bit12 << 12) | (bit11 << 11) | (bits10_5 << 5) | (bits4_1 << 1)
# 13-bit sign extension
imm = imm_raw if (imm_raw < 4096) else (imm_raw - 8192)
```

### U-Type (opcode 0110111 LUI, 0010111 AUIPC)

Stores a 20-bit immediate in the upper 20 bits; lower 12 bits of the result are zeroed:

```python
imm = (instr >> 12) & 0xFFFFF  # upper 20 bits, sign-extend as 20-bit value
```

### J-Type (opcode 1101111 — JAL)

Encodes a 21-bit byte offset (bit 0 always 0):

```
31  30       21 20  19      12 11    7 6      0
[20][ imm[10:1] ][11][ imm[19:12] ][  rd  ][ opcode]
```

```python
bit20    = (instr >> 31) & 1
bits10_1 = (instr >> 21) & 0x3FF
bit11    = (instr >> 20) & 1
bits19_12= (instr >> 12) & 0xFF
imm_raw = (bit20 << 20) | (bits19_12 << 12) | (bit11 << 11) | (bits10_1 << 1)
# 21-bit sign extension
imm = imm_raw if (imm_raw < 1048576) else (imm_raw - 2097152)
```

## Common Mistakes

- **B-type bit 11 position**: it is at instruction bit 7, *not* bit 11. This is the most common student bug.
- **J-type bit ordering**: bits 19:12 come *before* bit 11 in the instruction word, opposite of what you might expect.
- **Sign extension boundary**: for a 12-bit immediate, the sign bit is bit 11 (value 2048); values ≥ 2048 are negative.

## Further Reading

- The RISC-V Unprivileged Specification (https://docs.riscv.org/reference/isa/_attachments/riscv-unprivileged.pdf) — Chapter 2: RV32I Base Integer Instruction Set, Section 2.3 (Immediate Encoding Variants).
- *Computer Organization and Design RISC-V Edition* by Patterson and Hennessy — Appendix A: The RISC-V Instruction Set.
