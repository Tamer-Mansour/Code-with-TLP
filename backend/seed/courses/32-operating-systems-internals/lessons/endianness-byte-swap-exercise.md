# Exercise: Convert a 32-bit Integer Between Big- and Little-Endian

In this exercise you will implement a byte-swap function that converts a 32-bit unsigned integer between big-endian and little-endian representations — the same transformation that `htonl`/`ntohl` perform under the hood.

## What You Will Implement

Given a 32-bit unsigned integer and a target endian format, output the correctly reordered value as an 8-digit uppercase hex string.

## Skills Practiced

- Isolating individual bytes using bitwise AND masks and shifts
- Reassembling bytes into a new integer in the desired byte order
- Understanding how byte position maps to significance

## Approach

To swap a 32-bit integer `x`:

```python
byte0 = (x >> 24) & 0xFF   # most significant byte
byte1 = (x >> 16) & 0xFF
byte2 = (x >>  8) & 0xFF
byte3 =  x        & 0xFF   # least significant byte

# little-endian: byte3 at lowest address (index 0 in memory)
# represented as integer: byte3 is least significant → it stays at position 0
swapped = (byte3 << 24) | (byte2 << 16) | (byte1 << 8) | byte0
```

This is exactly the operation network stacks perform on every packet header.

## Your Task

Read from standard input and write the converted value to standard output. See the problem specification in the prompt file for the full input/output format and sample cases.
