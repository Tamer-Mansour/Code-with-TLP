# Exercise: Parse a Hex Byte Stream into Integers

In this exercise you will implement a parser that reads a stream of hexadecimal bytes and reconstructs multi-byte integers from them using a specified byte order.

## What You Will Implement

Your program reads a single line containing space-separated pairs of hex digits (bytes), followed by a second line specifying the byte order (`BE` for big-endian or `LE` for little-endian). The byte stream always contains a multiple of 4 bytes. For each group of 4 bytes, output the corresponding unsigned 32-bit integer in decimal.

## Skills Practiced

- Parsing raw byte streams represented as hex pairs
- Reconstructing integers from bytes using explicit bit shifting
- Handling both big-endian and little-endian byte ordering
- Understanding the difference in how the same bytes produce different integer values

## Byte Assembly Logic

Given bytes `b0 b1 b2 b3` in the stream order:

**Big-endian (network order):**
```
value = (b0 << 24) | (b1 << 16) | (b2 << 8) | b3
```

**Little-endian (x86 order):**
```
value = b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
```

## Input / Output

- **Line 1**: space-separated hex byte pairs (e.g. `12 34 56 78 DE AD BE EF`)
- **Line 2**: byte order string — either `BE` or `LE`
- **Output**: one decimal integer per group of 4 bytes, one per line

## Example

```
Input:
12 34 56 78 DE AD BE EF
BE

Output:
305419896
3735928559
```

```
Input:
78 56 34 12 EF BE AD DE
LE

Output:
305419896
3735928559
```

Both examples produce the same integer values — the bytes are just laid out in opposite order.

## Getting Started

Parse the bytes into a list, then iterate in groups of four. Use the byte order to combine them into a 32-bit value and print each in decimal. No external libraries are needed.
