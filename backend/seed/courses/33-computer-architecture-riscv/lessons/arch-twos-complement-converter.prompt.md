# Prompt: Two's Complement Encode/Decode

## Problem Statement

Write a program that encodes and decodes two's complement integers. Each line of input is one operation.

## Input Format

Each line contains one of:
```
ENCODE <width> <decimal>
DECODE <width> <binary>
```

- `width` is an integer in {4, 8, 16, 32} representing the number of bits.
- For `ENCODE`: `decimal` is a signed integer in the range [−2^(width−1), 2^(width−1)−1].
- For `DECODE`: `binary` is a string of exactly `width` characters, each '0' or '1'.

Input ends at EOF. There are 1 to 20 operations per test case.

## Output Format

For each operation, print one line:
- `ENCODE` → the zero-padded binary string of length `width` representing the two's complement encoding.
- `DECODE` → the signed decimal integer represented by the binary string in two's complement.

## Constraints

- width in {4, 8, 16, 32}
- Encoded decimals are always in the valid range for the given width.
- Binary strings are always exactly `width` characters of '0'/'1'.
- No extra whitespace in output.

## Sample Input

```
ENCODE 8 -37
ENCODE 8 127
ENCODE 4 -1
DECODE 8 11011011
DECODE 4 1000
DECODE 8 00000000
ENCODE 8 -128
DECODE 8 10000000
```

## Sample Output

```
11011011
01111111
1111
-37
-8
0
10000000
-128
```

## Explanation

- `-37` in 8-bit two's complement: +37 = 00100101, flip → 11011010, add 1 → 11011011.
- `127` in 8-bit: 01111111 (positive, no transformation needed).
- `-1` in 4-bit: +1 = 0001, flip → 1110, add 1 → 1111.
- `11011011` decoded: MSB is 1, so negative. Flip → 00100100, add 1 → 00100101 = 37, so value is -37.
- `1000` in 4-bit: MSB weight = -8, rest = 0. Value = -8.
- `00000000` = 0.
- `-128` is the most negative 8-bit value = 10000000.

## Notes

- For `DECODE`, use the weighted MSB formula: value = -2^(width-1) * MSB + sum of remaining weighted bits.
- For `ENCODE` of negative numbers: compute 2^width + decimal (or use flip-and-add-1).
- Zero must encode to all zeros and decode to 0.
