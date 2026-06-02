# Prompt: Parse a Hexdump and Reconstruct Values

## Problem Statement

You are given a simplified hexdump and a list of memory read queries. Parse the hexdump to build a byte-addressable memory map, then answer each query by reconstructing the integer value at the specified address and width using the specified byte order.

## Input Format

```
<ENDIAN>
<H>
<hex_addr> <byte> <byte> ...
...
<Q>
<hex_addr> <width>
...
```

- Line 1: endianness — either `LE` or `BE`.
- Line 2: integer H (1 ≤ H ≤ 20) — number of hexdump lines.
- Next H lines: each hexdump line starts with an 8-hex-digit address (no colon), then 1–16 space-separated 2-hex-digit byte values. No ASCII column is present.
- Next line: integer Q (1 ≤ Q ≤ 50) — number of queries.
- Next Q lines: each has an 8-hex-digit address (no `0x` prefix) and an integer width (1, 2, or 4).

## Output Format

Q lines. Each line is the reconstructed value as an **uppercase hex string zero-padded** to `2 * width` digits (2 digits for width=1, 4 for width=2, 8 for width=4). No `0x` prefix.

## Constraints

- 1 ≤ H ≤ 20; 1 ≤ Q ≤ 50
- All queried addresses and their extents are guaranteed to be present in the hexdump.
- Width is exactly 1, 2, or 4.
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input

```
LE
1
00000000 78 56 34 12 DE AD BE EF FF 00 A5 5A 11 22 33 44
4
00000000 4
00000004 4
00000008 2
0000000A 1
```

## Sample Output

```
12345678
EFBEADDE
00FF
A5
```

## Explanation

Memory after parsing (hex):
```
addr 0x00: 0x78
addr 0x01: 0x56
addr 0x02: 0x34
addr 0x03: 0x12
addr 0x04: 0xDE
addr 0x05: 0xAD
addr 0x06: 0xBE
addr 0x07: 0xEF
addr 0x08: 0xFF
addr 0x09: 0x00
addr 0x0A: 0xA5
addr 0x0B: 0x5A
addr 0x0C: 0x11
addr 0x0D: 0x22
addr 0x0E: 0x33
addr 0x0F: 0x44
```

- Query 1 (addr=0x00, width=4, LE): bytes = [0x78, 0x56, 0x34, 0x12]; LE reconstruction: b0 is LSB, b3 is MSB → (0x12 << 24) | (0x34 << 16) | (0x56 << 8) | 0x78 = 0x12345678 → `12345678`
- Query 2 (addr=0x04, width=4, LE): bytes = [0xDE, 0xAD, 0xBE, 0xEF]; LE: (0xEF << 24) | (0xBE << 16) | (0xAD << 8) | 0xDE = 0xEFBEADDE → `EFBEADDE`
- Query 3 (addr=0x08, width=2, LE): bytes = [0xFF, 0x00]; LE: (0x00 << 8) | 0xFF = 0x00FF → `00FF`
- Query 4 (addr=0x0A, width=1): byte = 0xA5 → `A5`
