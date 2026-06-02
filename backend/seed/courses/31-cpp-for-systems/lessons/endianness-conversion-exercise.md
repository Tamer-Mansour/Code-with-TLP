# Exercise: Convert Integers Between Endianness

In this exercise you will implement a program that reads a series of unsigned 32-bit integers stored in one byte order and outputs them converted to the opposite byte order.

## What You Will Implement

Your program reads lines from standard input. Each line contains a single unsigned 32-bit integer represented as a hexadecimal string (e.g. `12345678`). For each value, output the byte-swapped result as an 8-digit uppercase hex string.

## Skills Practiced

- Parsing hexadecimal strings into integer values
- Performing manual byte swap using bitwise shifts and masks
- Formatting output as zero-padded hexadecimal
- Understanding the relationship between byte order and byte-level integer layout

## Byte Swap Logic

For a 32-bit value `0xAABBCCDD`:
- Byte at position 0 (MSB) = `0xAA`
- Byte at position 1      = `0xBB`
- Byte at position 2      = `0xCC`
- Byte at position 3 (LSB)= `0xDD`

After swapping: `0xDDCCBBAA`

The formula in code:

```cpp
uint32_t swap32(uint32_t x) {
    return ((x & 0xFF000000u) >> 24) |
           ((x & 0x00FF0000u) >>  8) |
           ((x & 0x0000FF00u) <<  8) |
           ((x & 0x000000FFu) << 24);
}
```

## Input / Output

- **Input**: one hex string per line (no `0x` prefix, exactly 8 hex digits, uppercase or lowercase)
- **Output**: one swapped hex string per line, exactly 8 uppercase hex digits, zero-padded

## Example

```
Input:
12345678
DEADBEEF
00000001

Output:
78563412
EFBEADDE
01000000
```

## Getting Started

Open the code editor and implement the solution in the starter file. Parse each line, swap the bytes, and print the result. No external libraries are needed.
