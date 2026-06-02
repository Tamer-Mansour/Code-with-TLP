# Swap Endianness of a 32-bit Word

Byte-swapping a 32-bit integer is one of the first operations you implement when building a bus bridge or a protocol parser that crosses an endianness boundary. In this exercise you will write a Python function that reverses the byte order of a 32-bit unsigned integer and applies it to a list of values.

## What You Will Implement

Given one or more 32-bit unsigned integers in hexadecimal, output each value with its bytes reversed (i.e., converted from big-endian to little-endian or vice versa — the operation is its own inverse).

**Example:** `0xDEADBEEF` becomes `0xEFBEADDE`.

Breaking it down:

| Original byte order | Byte 0 (MSB) | Byte 1 | Byte 2 | Byte 3 (LSB) |
|---|---|---|---|---|
| `0xDEADBEEF` | `DE` | `AD` | `BE` | `EF` |
| After swap | `EF` | `BE` | `AD` | `DE` → `0xEFBEADDE` |

## Key Concepts to Apply

- Isolate each byte using bitwise AND and right-shift.
- Reconstruct the swapped word by shifting each byte to its new position and OR-ing the parts together.
- Alternatively, use Python's `int.to_bytes()` and `int.from_bytes()` for a clean, readable solution.

```python
def bswap32(value: int) -> int:
    b0 = (value >> 24) & 0xFF
    b1 = (value >> 16) & 0xFF
    b2 = (value >>  8) & 0xFF
    b3 = (value >>  0) & 0xFF
    return (b3 << 24) | (b2 << 16) | (b1 << 8) | b0
```

## Your Task

Read test cases from stdin (one hex value per line, without a `0x` prefix), compute the byte-swapped result, and print it in **uppercase hex without a `0x` prefix**, zero-padded to 8 digits.

The complete prompt, input/output spec, sample cases, and constraints are described in the accompanying prompt file.
