# Exercise Prompt: Extract a Bit Field from a Register Word

## Problem Statement

Given a 32-bit unsigned register value and a series of bit-field queries, extract and print the unsigned integer value of each specified field.

A field is defined by its LSB position (the lowest bit number in the field) and its width in bits. The extraction formula is:

```
field_value = (register >> lsb) & ((1 << width) - 1)
```

## Input Format

```
R
Q
lsb1 width1
lsb2 width2
...
```

- Line 1: integer R — the 32-bit register value (0 ≤ R ≤ 4294967295)
- Line 2: integer Q (1 ≤ Q ≤ 100) — number of queries
- Next Q lines: two integers `lsb` and `width`
  - 0 ≤ lsb ≤ 31
  - 1 ≤ width ≤ 32
  - lsb + width ≤ 32

## Output Format

Q lines, each containing a single non-negative decimal integer — the extracted field value.

## Constraints

- 0 ≤ R ≤ 4294967295
- 1 ≤ Q ≤ 100
- 0 ≤ lsb ≤ 31, 1 ≤ width ≤ 32, lsb + width ≤ 32

## Sample Input

```
305419896
4
0 8
8 8
16 8
24 8
```

## Sample Output

```
120
86
52
18
```

## Explanation

305419896 in hex is 0x12345678.

- Bits 7:0   = 0x78 = 120
- Bits 15:8  = 0x56 = 86
- Bits 23:16 = 0x34 = 52
- Bits 31:24 = 0x12 = 18

## Additional Notes

- Use integer arithmetic only; no floating point needed.
- The register value may require 64-bit handling in some languages — in Python, integers are arbitrary precision so this is not a concern.

## Time and Memory Limits

- Time limit: 3000 ms
- Memory limit: 256 MB
