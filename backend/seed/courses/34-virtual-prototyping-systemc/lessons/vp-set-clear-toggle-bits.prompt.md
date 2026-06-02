# Exercise Prompt: Set, Clear, and Toggle Bits in a Register

## Problem Statement

You are implementing a tiny register manipulation engine. Given an 8-bit register value and a bit position, apply one of three operations and return the resulting register value.

Operations:
- `SET reg bit` — set bit `bit` to 1 in `reg`
- `CLR reg bit` — clear bit `bit` to 0 in `reg`
- `TGL reg bit` — toggle bit `bit` in `reg`

All values are 8-bit unsigned (0–255). Bit positions are 0 (LSB) to 7 (MSB). Output each result as a decimal integer.

## Input Format

```
T
OPCODE reg_value bit_pos
...
```

- Line 1: integer T (1 ≤ T ≤ 1000) — number of operations
- Next T lines: one operation each
  - `OPCODE` is one of `SET`, `CLR`, `TGL`
  - `reg_value` is an integer in [0, 255]
  - `bit_pos` is an integer in [0, 7]

## Output Format

T lines, each containing a single decimal integer in [0, 255] — the register value after applying the operation.

## Constraints

- 1 ≤ T ≤ 1000
- 0 ≤ reg_value ≤ 255
- 0 ≤ bit_pos ≤ 7

## Sample Input

```
5
SET 0 3
CLR 255 0
TGL 170 1
SET 128 0
CLR 0 5
```

## Sample Output

```
8
254
168
129
0
```

## Explanation

- `SET 0 3`: 0 | (1<<3) = 8
- `CLR 255 0`: 255 & ~1 = 254
- `TGL 170 1`: 170 (0b10101010) ^ 0b00000010 = 0b10101000 = 168
- `SET 128 0`: 128 | 1 = 129
- `CLR 0 5`: 0 & ~(1<<5) = 0

## Time and Memory Limits

- Time limit: 3000 ms
- Memory limit: 256 MB
