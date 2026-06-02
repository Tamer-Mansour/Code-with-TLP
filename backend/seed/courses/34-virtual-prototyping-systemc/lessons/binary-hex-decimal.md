# Binary, Hex, and Decimal Conversions

Every register, address, and interrupt mask your firmware touches is ultimately a pattern of bits. Fluency in binary and hexadecimal is not optional — it is the first skill a hardware-software engineer reaches for dozens of times per day.

## The Three Bases at a Glance

| Base | Digits | Prefix (C/C++) | Use case |
|------|--------|----------------|----------|
| 2 (binary) | 0–1 | `0b` | Bit-field visualisation |
| 10 (decimal) | 0–9 | none | Human-readable counts |
| 16 (hex) | 0–9, A–F | `0x` | Register maps, addresses |

## Decimal to Binary

Repeatedly divide by 2 and collect remainders from bottom to top.

```
45 ÷ 2 = 22 r 1
22 ÷ 2 = 11 r 0
11 ÷ 2 =  5 r 1
 5 ÷ 2 =  2 r 1
 2 ÷ 2 =  1 r 0
 1 ÷ 2 =  0 r 1
```

Read remainders upward: **45 = 0b10_1101**

## Binary to Decimal

Assign powers of 2 (right to left, starting at 2^0) and sum the positions where a 1 appears.

```
0b1011_0100
  Bit weights: 128 64 32 16  8  4  2  1
  Bit values:    1  0  1  1  0  1  0  0
  Sum: 128 + 32 + 16 + 4 = 180
```

## Hex as a Shorthand for Binary

One hex digit maps exactly to four binary digits (a *nibble*). This is why hex is everywhere in datasheets — it compresses a 32-bit register value into 8 readable characters.

```
Binary   | Hex
---------+----
0000     | 0
0100     | 4
1010     | A
1111     | F
```

Worked example — convert `0xCAFE` to binary:

```
C    A    F    E
1100 1010 1111 1110
```

Result: `0b1100_1010_1111_1110`

## Decimal to Hex

Two common strategies:

**Via binary (fastest mentally):** convert to binary first, then group into nibbles from the right.

```
173 → 0b1010_1101 → 0xAD
```

**Via repeated division by 16:**

```
173 ÷ 16 = 10 r 13  → D
 10 ÷ 16 =  0 r 10  → A
Read upward: 0xAD
```

## C/C++ Literals

```cpp
#include <cstdint>

uint32_t ctrl = 0xDEAD'BEEF;   // hex literal (C++14 digit separator)
uint8_t  mask = 0b0011'1100;   // binary literal (C++14)
uint16_t port = 8080;           // decimal
```

> **Pitfall:** Plain `int` is implementation-defined in width. Always use `<cstdint>` types (`uint32_t`, `int16_t`, etc.) in register models so the bit-widths are guaranteed.

## Quick Sanity Checks

- A hex value `0xNN` where N is a single digit fits in 4 bits; two digits fit in a byte.
- `0xFF` = 255 = all 8 bits set. `0x00FF` isolates the low byte of a 16-bit word.
- Powers of 2 in hex: `0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80` — memorise these; they appear constantly as bit masks.

## Worked Example — Reading a Control Register

A datasheet says register `CR` at address `0x4000'2000` reads back `0x35`. What bits are set?

```
0x35 = 0b0011_0101
         bit 7654 3210
         set:  5 4  2 0
```

Bits 0, 2, 4, and 5 are asserted — you can look up each named field from the datasheet table.

**Interview answer:** "Hex is a compact alias for binary: every hex digit is exactly 4 bits, so I convert by grouping nibbles. I use `0x` prefixed literals with `uint32_t` types to keep widths unambiguous."
