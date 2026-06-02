# Exercise: Reconstruct a B-Type Immediate

B-type conditional branch instructions scatter the 13-bit PC-relative offset across four non-contiguous groups of bits in the 32-bit instruction word. This exercise drills that reconstruction until it becomes automatic.

## What You Will Implement

Given a 32-bit B-type instruction word (as a hex string), extract and reconstruct the signed 13-bit immediate step by step:

1. Extract **imm[12]** from instruction bit 31.
2. Extract **imm[10:5]** from instruction bits [30:25].
3. Extract **imm[4:1]** from instruction bits [11:8].
4. Extract **imm[11]** from instruction bit 7.
5. Concatenate as `{ imm[12], imm[11], imm[10:5], imm[4:1], 0 }` to form a 13-bit value.
6. Sign-extend from bit 12 to produce the final signed offset.

Your program reads one B-type instruction per line and prints the following for each:

- The reconstructed signed immediate (decimal)
- The funct3 value (decimal)
- The rs1 register number (decimal)
- The rs2 register number (decimal)

## Why This Exercise?

B-type immediate reconstruction is the single most common RISC-V encoding question in computer architecture interviews and exams. The scrambling looks arbitrary until you understand the hardware motivation — after this exercise you will be able to reconstruct it from first principles without looking up a table.

## Skills Practiced

- Multi-field bitwise extraction
- Bit concatenation to form sub-word values
- Sign extension from widths other than 8/16/32
- Working with PC-relative offsets

## Approach

Work out the bit masks before writing code. For each piece:

```python
imm12   = (inst >> 31) & 0x1         # 1 bit
imm10_5 = (inst >> 25) & 0x3F        # 6 bits
imm4_1  = (inst >>  8) & 0xF         # 4 bits
imm11   = (inst >>  7) & 0x1         # 1 bit
```

Combine them and apply sign extension:

```python
raw = (imm12 << 12) | (imm11 << 11) | (imm10_5 << 5) | (imm4_1 << 1)
# sign extend from bit 12
if raw & (1 << 12):
    raw -= (1 << 13)
```

Verify your result against known instructions before submitting.
