# Exercise: Hex to Binary and Back

In this exercise you will implement a conversion tool that translates between hexadecimal and binary representations. Fluency in this conversion is a non-negotiable skill for reading CPU register dumps, disassembler output, and network packet traces.

## What You Will Implement

Your program reads conversion requests from standard input. Each line contains:

- `HEX_TO_BIN <hex_string>` — convert a hexadecimal string to its full binary representation (4 bits per hex digit, no spaces, no `0x` prefix).
- `BIN_TO_HEX <binary_string>` — convert a binary string (length is always a multiple of 4) to its uppercase hexadecimal representation (no `0x` prefix).

The key insight to internalize: each hex digit maps **exactly** to a 4-bit group. This mapping is a lookup table in your head — practice until it is instant.

## Skills Practiced

- Grouping binary bits into nibbles (4-bit groups)
- Mapping between hex digits and 4-bit binary patterns
- Handling leading zeros (hex `0A` → binary `00001010`, not `1010`)
- Reading register-dump and instruction-encoding output from real tools

## Getting Started

Work through the conversion table mentally before coding. The key digit-to-nibble mappings to memorize:

| Hex | Binary |
|-----|--------|
| 0   | 0000   |
| 1   | 0001   |
| 4   | 0100   |
| 8   | 1000   |
| A   | 1010   |
| F   | 1111   |

Your solution should produce output with no extra whitespace, using uppercase A–F for hex digits. Each result goes on its own line.
