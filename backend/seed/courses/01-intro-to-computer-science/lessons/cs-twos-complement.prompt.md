# Two's Complement

Write a program that interprets an 8-bit binary string as both an unsigned integer and as a signed integer using two's complement.

Read one 8-bit binary string per line (exactly 8 characters, each `0` or `1`) until EOF.

For each string, output two values on the same line, separated by a space:
1. The **unsigned** decimal value (treating the binary as a non-negative integer, range 0–255).
2. The **signed** decimal value using 8-bit two's complement (range -128 to 127).

## Unsigned value

Sum the place values (128, 64, 32, 16, 8, 4, 2, 1) where the bit is `1`.

## Signed (two's complement) value

If the leftmost (most significant) bit is `0`, the signed value equals the unsigned value.

If the leftmost bit is `1`, the signed value is: unsigned value - 256.

## Example

**Input:**
```
00000001
01111111
10000000
11111111
10000001
```

**Output:**
```
1 1
127 127
128 -128
255 -1
129 -127
```
