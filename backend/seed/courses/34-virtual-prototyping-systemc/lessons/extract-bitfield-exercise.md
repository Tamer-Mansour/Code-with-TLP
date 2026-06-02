# Extract a Bit Field from a Register Word

Datasheets describe registers as collections of named fields, each occupying a contiguous range of bits. In this exercise you will implement a general-purpose bit-field extractor and apply it to a series of queries against a 32-bit register word.

## What You Will Implement

Your program reads a 32-bit register value and a series of extraction queries. For each query you are given the LSB position and the width of a field; you must return the unsigned integer value of that field.

## Core Technique

```python
def extract_field(reg, lsb, width):
    mask = (1 << width) - 1   # e.g. width=4 → mask = 0xF
    return (reg >> lsb) & mask
```

This two-step pattern — shift right to bring the field to bit 0, then AND with the width-derived mask — is the canonical extract operation used in every device driver and hardware model.

## Why This Matters in SystemC/TLM

In a TLM register model, each transaction carries a 32-bit or 64-bit data word. Peripheral models decode fields from that word to update internal state. The extractor pattern you practice here is called hundreds of times per simulation tick.

## Input Format

- Line 1: integer R — the 32-bit register value (unsigned, fits in a 32-bit unsigned integer)
- Line 2: integer Q — number of field queries
- Next Q lines: `lsb width` — both integers, 0 ≤ lsb, width ≥ 1, lsb + width ≤ 32

## Output Format

- Q lines, each containing the extracted field value as a decimal integer.

## Example

Input:
```
305419896
3
0 8
8 8
16 8
```

Output:
```
120
205
171
```

`305419896` = `0x1234_5678`. Bits 7:0 = `0x78` = 120, bits 15:8 = `0x56` = 86... wait — let's use a concrete value.

`0x12345678`:
- bits 7:0  = `0x78` = 120
- bits 15:8 = `0x56` = 86
- bits 23:16 = `0x34` = 52

Use that pattern to verify your implementation against the sample cases provided in the prompt file.
