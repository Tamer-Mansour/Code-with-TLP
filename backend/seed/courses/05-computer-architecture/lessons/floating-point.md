# Floating-Point and Overflow

Fixed-width integers cannot represent very large numbers, very small fractions, or irrational values. IEEE 754 floating-point is the hardware and language standard that handles these cases. This lesson covers the complete bit-level encoding, worked examples, special values, rounding, and common pitfalls.

## Integer Overflow in Detail

Before floating-point: what happens when integers escape their range?

### Unsigned Overflow — Modular Wrap

```
8-bit: 255 + 1:
  11111111
+ 00000001
----------
 100000000  → drop carry → 00000000 = 0

More generally: result = (a + b) mod 2^N
```

The CPU's **Carry (C) flag** is set. C and Python integers wrap around on the hardware but Python's `int` is arbitrary-precision so no overflow occurs in Python.

### Signed Overflow — Same Bits, Different Interpretation

```
8-bit: +127 + +1:
  01111111
+ 00000001
----------
  10000000 = -128 in two's complement ← wrong sign!

Carry into bit 7 = 1 (from the 7th-bit column)
Carry out of bit 7 = 0
Carry_in ≠ Carry_out → Overflow flag V = 1
```

Detection rule: **V = Carry_in_MSB XOR Carry_out_MSB**.

In C, signed integer overflow is **undefined behavior** — the compiler is free to assume it never happens, which can eliminate bounds checks. In Java and Python, it does not occur at the language level.

## IEEE 754 Floating-Point Standard

IEEE 754 (1985, revised 2008) encodes real numbers in **base-2 scientific notation**:

```
Value = (−1)^sign  ×  1.fraction  ×  2^(exponent − bias)
```

The "1." before the fraction is **implicit** (the hidden bit) — it is not stored.

### Single Precision (float32) — 32 bits

```
 31  30         23  22                        0
 ┌──┬───────────────┬──────────────────────────┐
 │ S│  Exponent(8)  │    Fraction/Mantissa(23) │
 └──┴───────────────┴──────────────────────────┘
```

- **Sign** (bit 31): 0 = positive, 1 = negative.
- **Exponent** (bits 30–23): biased by **127**. Stored exponent E → actual exponent E − 127.
  - Stored 0: special (zero/denormals). Stored 255: special (infinity/NaN).
  - Normal range: stored 1–254, actual −126 to +127.
- **Fraction** (bits 22–0): the 23 bits after the implicit leading 1.

### Double Precision (float64) — 64 bits

- Sign: 1 bit. Exponent: 11 bits, bias 1023, range −1022 to +1023. Fraction: 52 bits.
- ~15–17 significant decimal digits vs ~7 for single.

## Complete Worked Example: Encoding 6.5

**Step 1: Convert to binary.**

```
6.5 = 6 + 0.5
    = 110 + 0.1 (binary)
    = 110.1 (binary)
```

**Step 2: Normalize (move binary point to get 1.xxx × 2^exp).**

```
110.1 = 1.101 × 2^2
```

**Step 3: Encode fields.**

```
Sign  = 0  (positive)
Exponent = 2 + 127 = 129 = 10000001 (binary)
Fraction = 101 followed by 20 zeros:
           10100000000000000000000
```

**Step 4: Assemble the 32-bit pattern.**

```
S  Exponent   Fraction
0  10000001  10100000000000000000000
```

Hex: `0 1000 0000 1 1010 0000 0000 0000 0000 000`
     = `0100 0000 1101 0000 0000 0000 0000 0000`
     = `0x40D00000`

## Complete Worked Example: Encoding −0.375

**Step 1: 0.375 in binary.**

```
0.375 × 2 = 0.75 → 0
0.75  × 2 = 1.5  → 1
0.5   × 2 = 1.0  → 1
0.375 = 0.011 (binary)
```

**Step 2: Normalize.**

```
0.011 = 1.1 × 2^(-2)
```

**Step 3: Encode.**

```
Sign     = 1  (negative)
Exponent = -2 + 127 = 125 = 01111101
Fraction = 1 followed by 22 zeros = 10000000000000000000000
```

**Step 4: Assembled pattern.**

```
1 01111101 10000000000000000000000
= 1011 1110 1100 0000 0000 0000 0000 0000
= 0xBEC00000
```

## Worked Example: Decoding a Bit Pattern

Decode `0 10000100 10011000000000000000000`:

```
Sign     = 0 → positive
Exponent = 10000100 = 132, actual = 132 − 127 = 5
Fraction = 10011000000000000000000
Mantissa = 1.10011 (append implicit 1.)
         = 1 + 0.5 + 0 + 0 + 0.0625 + 0.03125
         = 1.59375

Value = 1.59375 × 2^5 = 1.59375 × 32 = 51.0
```

Check: 32 + 16 + 2 + 1 = 51. ✓

## Special Values

The exponent fields all-zeros and all-ones are reserved:

| Stored Exp | Fraction | Value | Notes |
|------------|----------|-------|-------|
| 0 (00000000) | 0 | ±0 | Positive and negative zero |
| 0 (00000000) | ≠0 | Denormal | Gradual underflow, no implicit 1 |
| 255 (11111111) | 0 | ±∞ | Result of overflow or div by zero |
| 255 (11111111) | ≠0 | NaN | Invalid operation (√−1, 0/0, etc.) |

### Denormal Numbers (Subnormals)

When the exponent stored is 0, the implicit leading bit is **0** instead of 1. This allows IEEE 754 to represent values smaller than the minimum normalized number:

```
Minimum normalized (single):  ±1.0 × 2^(-126) ≈ 1.18 × 10^-38
Minimum denormal:              ±0.000...001 × 2^(-126) ≈ 1.40 × 10^-45  (one fraction bit set)
```

Denormals enable **gradual underflow** instead of sudden snap-to-zero, but many CPUs handle them in microcode and are **50–100× slower** for denormal operands.

### NaN Arithmetic

```python
import math
print(math.nan == math.nan)   # False!  NaN is not equal to itself
print(math.nan + 1)           # nan
print(math.nan > 0)           # False
```

This behavior is intentional: NaN propagates through calculations to signal that a result is meaningless.

## Rounding Modes

IEEE 754 mandates four rounding modes:

| Mode | Description |
|------|-------------|
| Round to nearest, ties to even (default) | The last representable value; on a tie, choose the one with an even LSB |
| Round toward +∞ | Always round up |
| Round toward −∞ | Always round down |
| Round toward zero (truncate) | Chop off extra bits |

**Why "ties to even"?** It prevents systematic bias accumulation when doing many rounded operations (e.g., financial summations).

## Precision and Range Summary

| Format | Total bits | Sign | Exponent | Fraction | Approx decimal digits | Max value |
|--------|-----------|------|----------|----------|-----------------------|-----------|
| Half (float16) | 16 | 1 | 5 (bias 15) | 10 | ~3 | 65504 |
| Single (float32) | 32 | 1 | 8 (bias 127) | 23 | ~7 | ~3.4×10^38 |
| Double (float64) | 64 | 1 | 11 (bias 1023) | 52 | ~15–16 | ~1.8×10^308 |

float16 is now widely used in AI training (mixed-precision) because it is 2× smaller than float32, allowing 2× more data per SIMD register.

## The Representation Gap: Why 0.1 Cannot Be Exact

In base 2, any fraction whose denominator has a prime factor other than 2 is a repeating fraction:

```
0.1 (decimal) in base 2:
0.1 × 2 = 0.2 → 0
0.2 × 2 = 0.4 → 0
0.4 × 2 = 0.8 → 0
0.8 × 2 = 1.6 → 1
0.6 × 2 = 1.2 → 1
0.2 × 2 = 0.4 → 0   ← cycle repeats!

0.1 (decimal) = 0.0001100110011... (binary, repeating)
```

The nearest float32 is `0.10000000149011612...`. Printing `0.1 + 0.2 == 0.3` in Python gives `False`.

## Non-Associativity

Floating-point addition is **not** mathematically associative:

```python
>>> (1e20 + (-1e20)) + 1.0
1.0
>>> 1e20 + ((-1e20) + 1.0)
0.0   # catastrophic cancellation: 1.0 is lost in the noise of 1e20
```

This is why numeric libraries (NumPy, BLAS) use pairwise summation or compensated summation (Kahan algorithm) for accuracy.

## Performance Implications

| Operation | Typical latency (modern CPU) |
|-----------|------------------------------|
| Integer ADD | 1 cycle |
| FP ADD (double) | 4–5 cycles |
| FP MUL (double) | 4–5 cycles |
| FP DIV (double) | 10–15 cycles |
| Denormal FP ADD | 50–150 cycles (microcode) |

FP operations have dedicated **floating-point units (FPUs)** with multi-cycle latencies but can be pipelined. SIMD extensions (SSE, AVX, AVX-512) operate on 4, 8, or 16 floats simultaneously, giving 16× throughput for vectorizable code.
