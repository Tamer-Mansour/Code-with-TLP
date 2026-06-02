# Sign Extension of Immediates

Every RISC-V instruction that carries an immediate value uses **sign extension** to widen that value to 32 bits (or 64 bits on RV64) before it is used in arithmetic. Understanding sign extension precisely — and knowing the common bugs it causes — is essential for writing a correct ISA simulator.

## What Is Sign Extension?

When a number is stored in fewer bits than the target width, sign extension replicates the most-significant bit (the sign bit) into all higher positions.

**Positive example (12-bit → 32-bit):**

```
12-bit value:  0 000 0000 0101  = +5
32-bit result: 0000 0000 0000 0000 0000 0000 0000 0101 = +5
```

**Negative example (12-bit → 32-bit):**

```
12-bit value:  1 111 1111 1011  = -5 (two's complement)
32-bit result: 1111 1111 1111 1111 1111 1111 1111 1011 = -5
```

The sign bit (bit 11 of the 12-bit number) is copied into bits [31:12].

## How RISC-V Uses Sign Extension

Every RISC-V immediate is **always** sign-extended before being used in an operation. This applies to:

- **I-type:** 12-bit immediate → 32-bit signed value.
- **S-type:** 12-bit immediate (split) → 32-bit signed value. Used as a byte offset in stores.
- **B-type:** 13-bit immediate (bit 0 = 0) → 32-bit signed PC-relative offset.
- **J-type:** 21-bit immediate (bit 0 = 0) → 32-bit signed PC-relative offset.
- **U-type:** 20-bit upper immediate — **no** sign extension; bits [31:12] of the result are the immediate; bits [11:0] are zeroed.

## Implementing Sign Extension in C

### Method 1: Arithmetic Right Shift (C, careful with undefined behavior)

```c
// Works when int is 32-bit and right-shift is arithmetic (common on x86/ARM)
int32_t sign_ext_12(uint32_t instr) {
    int32_t signed_instr = (int32_t)instr;
    return signed_instr >> 20;  // arithmetic right-shift propagates sign bit
}
```

This works because casting to `int32_t` and shifting right arithmetically fills the upper bits with the sign bit. However, arithmetic right-shift on signed integers is implementation-defined in C before C23 — in practice it works on all major compilers for x86/ARM/RISC-V targets.

### Method 2: Explicit Bit Manipulation (portable, preferred)

```c
int32_t sign_ext_12(uint32_t raw_imm12) {
    // raw_imm12 is already masked to 12 bits
    if (raw_imm12 & 0x800) {          // bit 11 is set → negative
        return (int32_t)(raw_imm12 | 0xFFFFF000u);  // fill upper 20 bits with 1s
    }
    return (int32_t)raw_imm12;        // positive, upper bits already 0
}
```

### Method 3: Python

Python integers have arbitrary precision, so "sign extension" means recognising when a value's sign bit is set and subtracting the unsigned range:

```python
def sign_ext(value, bits):
    """Sign-extend `value` from `bits`-wide to full Python int."""
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

# Examples
print(sign_ext(0x7FF, 12))   # +2047
print(sign_ext(0x800, 12))   # -2048
print(sign_ext(0xFFF, 12))   # -1
```

## Common Pitfalls

**Pitfall 1: Zero-extending instead of sign-extending.**
If your simulator uses `uint32_t` everywhere and masks the immediate with `0xFFF`, the value is always non-negative. `ADDI x1, x0, -1` would compute `0xFFF = 4095` instead of `−1`.

**Pitfall 2: Sign-extending U-type immediates.**
`LUI` and `AUIPC` use U-type encoding. The immediate already occupies bits [31:12] of the instruction word; it is the upper 20 bits of the result. Do not sign-extend it — zero out bits [11:0] and use the result directly.

**Pitfall 3: Forgetting the shift-by-1 in B and J types.**
The 13-bit B-type immediate has bit[0] = 0 (implicit). When you reassemble it you must shift `imm[4:1]` left by 1. Forgetting this gives a byte offset half the correct value.

## Quick Reference Table

| Format | Imm width | Sign bit | Extension needed |
|--------|-----------|----------|-----------------|
| I      | 12 bit    | bit 11   | Yes |
| S      | 12 bit    | bit 11   | Yes |
| B      | 13 bit    | bit 12   | Yes |
| U      | 20 bit    | —        | No (upper bits) |
| J      | 21 bit    | bit 20   | Yes |

> **Interview answer:** "RISC-V always sign-extends immediates before use, replicating the top bit of the immediate into all higher bits. The only exception is U-type, where the 20-bit immediate is placed in bits [31:12] and bits [11:0] are zeroed."
