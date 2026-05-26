# Exercise: Two's Complement Interpreter

Practice your understanding of how signed integers are stored in binary by building an 8-bit two's complement interpreter.

## What you need to do

Read 8-bit binary strings from standard input, one per line, until EOF.

For each string, print **two values on the same line, separated by a space**:
1. The **unsigned** decimal value (0–255)
2. The **signed two's complement** decimal value (-128 to 127)

## Two's complement rule (8-bit)

- If the leftmost bit is `0`: signed value = unsigned value
- If the leftmost bit is `1`: signed value = unsigned value − 256

## Example

**Input:**
```
00000001
01111111
10000000
11111111
```

**Output:**
```
1 1
127 127
128 -128
255 -1
```

## Hints

- `int(s, 2)` converts a binary string to an unsigned integer in Python.
- The MSB (most significant bit) is `s[0]`.
