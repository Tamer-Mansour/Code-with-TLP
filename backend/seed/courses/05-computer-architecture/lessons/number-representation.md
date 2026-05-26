# Number Representation in Hardware

Computers store everything as binary numbers. This lesson goes deep on how unsigned integers, signed integers, fixed-point, and hexadecimal are encoded and why the hardware choices were made.

## Unsigned Binary

An N-bit unsigned integer encodes values from 0 to 2^N − 1. Each bit position i (counting from 0 at the right) has weight 2^i.

**Worked example: decode 8-bit pattern 10110011**

```
Bit position:  7  6  5  4  3  2  1  0
Bit value:     1  0  1  1  0  0  1  1
Weight:      128 64 32 16  8  4  2  1

Value = 128 + 0 + 32 + 16 + 0 + 0 + 2 + 1 = 179
```

**Encoding 213 in 8 bits:**

```
213 = 128 + 64 + 16 + 4 + 1
    =  1    1    0    1   0   1   0   1
Bit pattern: 11010101
```

Verify: 128+64+16+4+1 = 213 ✓

## Two's Complement (Signed Integers)

The universal hardware encoding for signed integers. In N bits:

- Bit positions 0 through N−2 have positive weights 2^0 through 2^(N-2).
- Bit position N−1 (the MSB) has the **negative** weight **−2^(N−1)**.

**Range:**

```
Minimum (all bits 1):  -2^(N-1)
Maximum (MSB=0, rest 1): 2^(N-1) - 1

For N=8:  -128 to +127
For N=16: -32768 to +32767
For N=32: -2,147,483,648 to +2,147,483,647
```

**Worked example: decode 8-bit pattern 10110011 as signed**

```
Bit position:  7   6  5  4  3  2  1  0
Bit value:     1   0  1  1  0  0  1  1
Weight:      -128 64 32 16  8  4  2  1

Value = -128 + 0 + 32 + 16 + 0 + 0 + 2 + 1 = -77
```

**Worked example: decode 11111111**

```
= -128 + 64 + 32 + 16 + 8 + 4 + 2 + 1 = -128 + 127 = -1
```

### Negating a Two's Complement Number

Algorithm: **flip all bits, then add 1**.

**Example: negate 5 (8-bit)**

```
+5 = 00000101
Step 1 (flip):  11111010
Step 2 (+1):    11111011  = -5

Verification: -128 + 64 + 32 + 16 + 8 + 0 + 2 + 1
            = -128 + 123 = -5 ✓
```

**Example: negate -128 (the minimum)**

```
-128 = 10000000
Step 1: 01111111
Step 2: 10000000  ← back to -128!
```

Negating −2^(N−1) overflows — there is no +128 in 8-bit two's complement. This is the only "asymmetric" case.

**Example: negate -5**

```
-5 = 11111011
Step 1: 00000100
Step 2: 00000101 = 5 ✓
```

### Why Two's Complement?

Two reasons make it the universal choice:

1. **Unique zero**: only one bit pattern for 0 (unlike sign-magnitude, which has +0 = 00000000 and −0 = 10000000, requiring extra hardware to handle).

2. **Same adder for signed and unsigned**: the hardware addition of 00000101 (+5) and 11111011 (−5 in two's complement, or 251 unsigned) gives 100000000, and after dropping the carry-out: 00000000 = 0. The same gate network handles both signed addition and unsigned addition correctly.

```
  5 in 8-bit: 00000101
 -3 in 8-bit: 11111101
              --------
 carry out:  1 00000010 → drop carry → 00000010 = 2 ✓
```

## Sign Extension

To represent a small signed value in more bits, copy the MSB into all new high-order bits.

```
8-bit  +5  = 00000101
16-bit +5  = 0000000000000101  (extend the 0)

8-bit  -5  = 11111011
16-bit -5  = 1111111111111011  (extend the 1)
```

**Worked decode check**: `1111111111111011` as 16-bit signed:
= −32768 + 16384 + 8192 + 4096 + 2048 + 1024 + 512 + 256 + 128 + 64 + 32 + 16 + 8 + 0 + 2 + 1
= −32768 + 32763 = −5 ✓

Sign extension is used by RISC-V's `lw` instruction (load word) and by the RISC-V decoder when expanding a 12-bit immediate to 32 bits.

## Hexadecimal Notation

Four bits map exactly to one hex digit 0–9, A–F. Hex is indispensable for reading bit patterns.

```
Binary to hex mapping:
0000=0  0001=1  0010=2  0011=3
0100=4  0101=5  0110=6  0111=7
1000=8  1001=9  1010=A  1011=B
1100=C  1101=D  1110=E  1111=F
```

**Worked example: encode 0xDEAD in binary**

```
D    E    A    D
1101 1110 1010 1101
→ 1101111010101101 (16 bits)
```

**Worked example: decode 0xBEEF as unsigned 16-bit**

```
B    E    E    F
1011 1110 1110 1111

= 32768 + 8192 + 4096 + 2048 + 1024 + 512 + 256 + 128 + 64 + 32 + 8 + 4 + 2 + 1
Shorter: 0xBEEF = 11×4096 + 14×256 + 14×16 + 15
= 45056 + 3584 + 224 + 15 = 48879
```

## Overflow Detection

### Unsigned Overflow

When the result exceeds 2^N − 1, the carry-out of the MSB position is discarded, wrapping the result mod 2^N.

```
8-bit: 200 + 100 = 300 → 300 mod 256 = 44
Bit: 11001000 + 01100100 = [1] 00101100  (carry=1, result=44)
```

The CPU's **Carry flag (C)** is set when this carry-out occurs.

### Signed Overflow Detection

Signed overflow occurs when:
- Two **positive** numbers sum to a **negative** result, or
- Two **negative** numbers sum to a **positive** result.

Hardware detection: carry into MSB ≠ carry out of MSB.

```
8-bit: +100 + +60 = +160 → overflows!
 01100100
+00111100
----------
 10100000  = -96 in two's complement

Carry into bit 7:  1
Carry out of bit 7: 0
1 ≠ 0 → overflow flag V = 1
```

The CPU's **Overflow flag (V)** is set. Unsigned addition of the same bits gives 160, which is correct unsigned — the hardware is the same circuit; only the flag interpretation differs.

## Fixed-Point Numbers

Fixed-point allocates some bits to the integer part and some to the fractional part, separated by a conceptual **binary point**. The hardware is identical to integer arithmetic; only the programmer's interpretation changes.

**Format notation:** `Q4.4` = 4 integer bits + 4 fraction bits.

```
Bit weights for Q4.4 (8-bit total):
  2^3  2^2  2^1  2^0 . 2^-1  2^-2  2^-3  2^-4
   8    4    2    1  .  0.5   0.25  0.125  0.0625
```

**Example: decode 0101.1100 in Q4.4**

```
= 0 + 4 + 0 + 1 + 0.5 + 0.25 + 0 + 0
= 5.75
```

**Example: encode −3.25 in Q4.4 (signed two's complement)**

```
+3.25 → 0011.0100
Negate (flip + add 1 at bit 0, remembering binary point is just notation):
  0011.0100
  flip: 1100.1011
  +1 at LSB: 1100.1100

Verify: -8 + 4 + 0 + 0 + 0.5 + 0.25 + 0 + 0 = -3.25 ✓
```

Fixed-point is common in digital signal processing (audio codecs, radio), embedded systems (no FPU), and some graphics calculations.

## Key Takeaways

| Encoding | N-bit Range | Unique zero? | Same adder? |
|----------|-------------|-------------|-------------|
| Unsigned | 0 to 2^N−1 | Yes | Yes |
| Two's complement | −2^(N-1) to 2^(N-1)−1 | Yes | Yes |
| Sign-magnitude | −(2^(N-1)−1) to 2^(N-1)−1 | No (+0 and −0) | No |
| One's complement | −(2^(N-1)−1) to 2^(N-1)−1 | No (+0 and −0) | Almost (needs end-around carry) |

Two's complement dominates hardware because it requires no special-case logic for negative numbers, enabling elegant, uniform arithmetic circuits. The next lesson shows what happens when values exceed the representable range: overflow, and the IEEE 754 floating-point standard that handles arbitrarily large and small values.
