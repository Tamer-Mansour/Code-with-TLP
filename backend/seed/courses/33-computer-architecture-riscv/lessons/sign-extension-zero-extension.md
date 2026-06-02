# Sign Extension vs Zero Extension

When a processor loads a narrow value (say, 8 bits) into a wider register (say, 64 bits), it must fill the upper bits with something. The choice of what to fill with determines whether the value's numeric meaning is preserved — and getting it wrong silently corrupts computations.

## The Problem

A 64-bit RISC-V register holds 64 bits. If you load a single byte from memory, you have only 8 meaningful bits. The remaining 56 bits must be set to some value before arithmetic can proceed correctly.

## Zero Extension

Fill all upper bits with **0**. This is correct for **unsigned** values because prepending zeros to a binary number does not change its magnitude.

```
uint8_t value = 0xAB = 1010 1011 = 171 (decimal)

Zero-extended to 32 bits:
0000 0000  0000 0000  0000 0000  1010 1011  = 171 ✓
```

RISC-V uses zero extension for `LBU` (load byte unsigned), `LHU` (load halfword unsigned), and `LWU` (load word unsigned for RV64).

## Sign Extension

Replicate the **most-significant bit** (the sign bit) into all upper positions. This preserves the two's complement value for **signed** types.

```
int8_t value = 0xAB = 1010 1011 = -85 (signed 8-bit)

Sign-extended to 32 bits:
1111 1111  1111 1111  1111 1111  1010 1011  = -85 ✓

If zero-extended instead:
0000 0000  0000 0000  0000 0000  1010 1011  = 171 ✗ (wrong — sign lost)
```

RISC-V uses sign extension for `LB` (load byte signed), `LH`, and `LW` (on RV64).

## Worked Example — RISC-V Load

```asm
# Memory at address 0x1000 contains byte 0xFF

LBU t0, 0(a0)   # t0 = 0x00000000000000FF = 255 (zero-extended)
LB  t1, 0(a0)   # t1 = 0xFFFFFFFFFFFFFFFF = -1  (sign-extended)
```

Both instructions read the same byte. The difference is entirely in how the upper 56 bits are filled.

## When to Use Each

| Scenario                        | Extension type |
|---------------------------------|----------------|
| Unsigned byte/halfword/word     | Zero           |
| Signed byte/halfword/word       | Sign           |
| Immediate fields in instructions| Sign (always in RISC-V) |
| Shift amounts                   | Zero           |
| Array index from `unsigned`     | Zero           |

## Immediates Are Always Sign-Extended in RISC-V

A 12-bit immediate in an I-type instruction is **always sign-extended** to the full XLEN (32 or 64) before use, regardless of whether the instruction is logically signed or unsigned. This is why negative immediates work in instructions like `ADDI`:

```asm
addi t0, t0, -4   # -4 as 12-bit: 0xFFC
                  # sign-extended to 0xFFFFFFFFFFFFFFFC
                  # result: t0 = t0 - 4
```

## Common Pitfall — C Type Conversion

```c
uint8_t byte_val = 0xFF;          // 255
int32_t wrong    = byte_val;      // 255 — zero-extended, OK for unsigned

int8_t  signed_byte = (int8_t)0xFF; // -1
int32_t correct     = signed_byte;  // -1 — sign-extended, correct
int32_t mistake     = (uint8_t)0xFF; // 255 — unsigned cast forces zero-extend
```

The compiler chooses zero vs sign extension based on the **source type**, not the destination type. If the source is `uint8_t`, it zero-extends; if `int8_t`, it sign-extends.

## Hardware Implementation

Sign extension in hardware is free — it is just routing wires:

```
8-bit value input:  [b7][b6][b5][b4][b3][b2][b1][b0]
32-bit output:
  bits 31-8 → all connected to b7 (the sign bit)
  bits  7-0 → connected to b7..b0
```

No computation required. Zero extension is even simpler: the upper wires are tied to logic 0.

> **Interview answer:** Sign extension replicates the MSB to fill upper bits, preserving a two's complement signed value when widening; zero extension fills upper bits with zeros, preserving an unsigned value. RISC-V uses separate load instructions (LB/LBU, LH/LHU) to distinguish the two cases.
