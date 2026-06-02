# Two's Complement: How Negative Numbers Work

Two's complement is the universal encoding for signed integers in modern processors. Its elegance is that **a single adder circuit handles both addition and subtraction for signed and unsigned numbers** — no special logic needed for negative operands.

## The Core Idea

For an n-bit two's complement number, the weight of each bit is the same as unsigned *except* for the MSB, which has weight **−2ⁿ⁻¹** instead of +2ⁿ⁻¹.

```
8-bit example of -37:

Bit position: 7    6    5    4    3    2    1    0
Weight:      -128  64   32   16    8    4    2    1
Bit value:     1    1    0    1    1    0    1    1

Value = -128 + 64 + 0 + 16 + 8 + 0 + 2 + 1
      = -128 + 91
      = -37
```

The bit pattern `1101 1011` represents -37 in signed and 219 in unsigned. Same bits, different interpretation.

## Encoding a Negative Number

**Method 1 — definition formula:**  
Two's complement of X = 2ⁿ − X

For -37 in 8 bits: 256 − 37 = 219 = `1101 1011`. ✓

**Method 2 — flip-and-add-one (the fast mental trick):**
1. Write the positive value in binary.
2. Flip all bits (one's complement).
3. Add 1.

```
+37  =  0010 0101
Flip =  1101 1010   (one's complement)
Add 1=  1101 1011   (two's complement of -37)
```

Both methods always give the same result. The flip-and-add trick is faster by hand.

## Decoding a Negative Number

Given `1101 1011`, determine the signed value:

- MSB is 1 → negative.
- Apply flip-and-add-one to find the magnitude:
  ```
  1101 1011
  0010 0100   (flip)
  0010 0101   (add 1) = 37
  ```
- Result: -37.

Alternatively, use the weighted formula directly: -128 + 64 + 16 + 8 + 2 + 1 = -37.

## Why This Encoding Is Brilliant

Addition works identically for signed and unsigned values. To compute -37 + 10:

```
  1101 1011   (-37)
+ 0000 1010   (+10)
-----------
  1110 0101   (-27)  ← correct!
```

The carry out of bit 7 is discarded. The result -27 is correct. The CPU needs only one adder.

## Special Cases

- **Most negative number:** `1000 0000` = -128. There is no corresponding positive +128 in 8 bits. Trying to negate it wraps back to -128.
- **Zero:** `0000 0000` = 0. Exactly one representation (unlike sign-magnitude which has +0 and -0).
- **Negation of INT_MIN is undefined** in C/C++ because +128 doesn't fit in 8 bits.

```c
int8_t x = -128;
int8_t y = -x;   // Undefined behavior! -(-128) = +128, overflows int8_t
```

## Range Summary

| Bits | Min (signed) | Max (signed) | Max (unsigned) |
|------|-------------|--------------|----------------|
| 8    | -128        | 127          | 255            |
| 16   | -32768      | 32767        | 65535          |
| 32   | -2147483648 | 2147483647   | 4294967295     |
| 64   | -2⁶³        | 2⁶³ − 1      | 2⁶⁴ − 1       |

## RISC-V Immediates

RISC-V I-type instructions carry a **12-bit two's complement immediate**, giving a range of −2048 to +2047. When the hardware sign-extends it to 32 or 64 bits before using it, the flip-and-add logic happens automatically.

```asm
addi t0, t0, -1    # immediate = 0xFFF (12-bit two's complement -1)
                   # sign-extended to 0xFFFFFFFF before adding
```

> **Interview answer:** Two's complement encodes negative numbers by assigning the MSB a weight of −2ⁿ⁻¹. To negate a value, flip all bits then add 1. The key advantage is that the same adder circuit works for both signed and unsigned arithmetic with no extra hardware.
