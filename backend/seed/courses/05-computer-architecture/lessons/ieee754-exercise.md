# Exercise: Float to IEEE 754 Bits

In this exercise you will implement the IEEE 754 single-precision encoding of a floating-point number from scratch using only Python's standard library.

## Background

IEEE 754 single precision uses 32 bits:

```
Bit 31:     Sign (0 = positive, 1 = negative)
Bits 30–23: Exponent (8 bits, biased by 127)
Bits 22–0:  Fraction / Mantissa (23 bits, after the implicit leading 1.)
```

The value represented is:
```
(-1)^sign × 1.fraction × 2^(stored_exponent - 127)
```

Special case: `0.0` has all bits zero; the implicit leading 1 is suppressed.

## Algorithm (for normal values)

1. Extract the sign bit: `sign = 1` if `v < 0`, else `0`.
2. Work with `|v|`.
3. Find the largest power of 2 ≤ |v| → this is the biased exponent base.
4. Compute `fraction = |v| / 2^exp − 1` (the part after the implicit 1.).
5. Encode fraction as 23 bits (multiply by 2^23, truncate to integer).
6. Pack: `sign<<31 | (exp+127)<<23 | fraction_bits`.

Python's `struct.pack('>f', value)` does this in one call.

## Task

Read one floating-point number from stdin and print its 32-bit IEEE 754 single-precision representation as a binary string.

## Examples

```
Input:  6.5
Output: 01000000110100000000000000000000
```

```
Input:  -1.0
Output: 10111111100000000000000000000000
```
