# Exercise Prompt: Endianness Converter

## Description

Given a 32-bit unsigned integer and a requested byte order, output the four bytes of that integer in the specified endianness as uppercase two-digit hexadecimal values separated by single spaces.

## Input Format

A single line containing:
- A non-negative integer `N` where `0 <= N <= 4294967295` (fits in uint32)
- A string, either `little` or `big`, separated from `N` by a single space

## Output Format

A single line of four two-digit uppercase hexadecimal byte values, separated by single spaces.

The bytes are printed in memory order:
- For `little` endian: LSB (least significant byte) first, MSB last.
- For `big` endian: MSB (most significant byte) first, LSB last.

No trailing spaces. End the line with a newline.

## Constraints

- `0 <= N <= 4294967295`
- Byte order is exactly `little` or `big` (lowercase)
- Output hex digits must be uppercase (A-F)

## Sample Input 1

```
305419896 little
```

## Sample Output 1

```
78 56 34 12
```

**Explanation:** `305419896 = 0x12345678`. Little-endian stores `0x78` at offset 0, `0x56` at offset 1, `0x34` at offset 2, `0x12` at offset 3.

## Sample Input 2

```
305419896 big
```

## Sample Output 2

```
12 34 56 78
```

**Explanation:** Big-endian stores the MSB `0x12` at offset 0, then `0x34`, `0x56`, `0x78`.

## Sample Input 3

```
0 little
```

## Sample Output 3

```
00 00 00 00
```

## Sample Input 4

```
4294967295 big
```

## Sample Output 4

```
FF FF FF FF
```

**Explanation:** `4294967295 = 0xFFFFFFFF`. All bytes are `0xFF` regardless of byte order.

## Starter Code (Python)

```python
import sys

def solve():
    line = input().split()
    n = int(line[0])
    order = line[1]
    # TODO: extract 4 bytes and print in requested order

solve()
```

## Hints

- Extract each byte with `(n >> (8 * i)) & 0xFF` for `i` in 0..3. `i=0` gives the LSB, `i=3` gives the MSB.
- For little-endian print bytes from `i=0` to `i=3`.
- For big-endian print bytes from `i=3` to `i=0`.
- Use `f"{byte:02X}"` to format as two-digit uppercase hex.
