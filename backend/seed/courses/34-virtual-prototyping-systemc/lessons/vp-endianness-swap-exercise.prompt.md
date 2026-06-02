# Prompt: Swap Endianness of a 32-bit Word

## Problem Statement

Given N 32-bit unsigned integers (provided as 8-digit uppercase or lowercase hexadecimal strings, one per line), output each value with its four bytes reversed, formatted as an 8-digit uppercase hexadecimal string (no `0x` prefix).

Byte reversal: for value `0xAABBCCDD`, the result is `0xDDCCBBAA`.

## Input Format

```
N
hex_value_1
hex_value_2
...
hex_value_N
```

- First line: integer N (1 ≤ N ≤ 100)
- Next N lines: each an 8-character hex string (digits 0-9, A-F or a-f), no `0x` prefix, no spaces.

## Output Format

N lines, each an **8-digit uppercase hex string** (zero-padded) representing the byte-swapped value. No `0x` prefix.

## Constraints

- 1 ≤ N ≤ 100
- Each input value is a valid 32-bit unsigned hexadecimal number.
- No leading/trailing whitespace on output lines.
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input

```
3
DEADBEEF
00000001
12345678
```

## Sample Output

```
EFBEADDE
01000000
78563412
```

## Explanation

- `DEADBEEF` → bytes `DE AD BE EF` → reversed `EF BE AD DE` → `EFBEADDE`
- `00000001` → bytes `00 00 00 01` → reversed `01 00 00 00` → `01000000`
- `12345678` → bytes `12 34 56 78` → reversed `78 56 34 12` → `78563412`
