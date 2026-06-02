# Exercise: Convert Between Little- and Big-Endian

In this exercise you will implement a program that reads a 32-bit unsigned integer and a target byte order, then outputs the bytes of that integer in the requested endianness.

## What You'll Implement

Your program will:

1. Read a 32-bit unsigned integer (given as a decimal number) and a target byte order (`little` or `big`) from standard input.
2. Output the four bytes of the integer in the requested byte order, as two-digit uppercase hexadecimal values separated by spaces, followed by a newline.

## Concepts Practiced

- Extracting individual bytes from a multi-byte integer using bitwise shifts and masks.
- Understanding how little-endian places the LSB at the lowest position and big-endian places the MSB first.
- Producing a human-readable hex dump of a value's byte representation.

## Byte Extraction Reminder

For a 32-bit value `v`:

| Byte     | Extraction         | Position in little-endian | Position in big-endian |
|----------|--------------------|--------------------------|------------------------|
| Byte 0   | `(v >> 0) & 0xFF`  | offset 0 (lowest address) | offset 3               |
| Byte 1   | `(v >> 8) & 0xFF`  | offset 1                  | offset 2               |
| Byte 2   | `(v >> 16) & 0xFF` | offset 2                  | offset 1               |
| Byte 3   | `(v >> 24) & 0xFF` | offset 3                  | offset 0 (lowest addr) |

Output the bytes in memory order — index 0 first, index 3 last.

## Example

Input:
```
305419896 little
```

`305419896` is `0x12345678` in hex.

Expected output:
```
78 56 34 12
```

Because little-endian stores the LSB (`0x78`) at the lowest address first.

For `big`:
```
305419896 big
```
Output:
```
12 34 56 78
```
