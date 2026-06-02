# Exercise: Set, Clear, Toggle, and Query Bits from Commands

In this exercise you will implement a small bit-manipulation interpreter. A program reads a sequence of commands that operate on a single 32-bit unsigned integer register, initially set to `0`. Each command names an operation and a bit position. After processing all commands the program prints the final register value in decimal.

## What You Will Implement

Your solution must handle four operations on a register (initially `0`):

- **SET n** — set bit `n` (force it to 1)
- **CLEAR n** — clear bit `n` (force it to 0)
- **TOGGLE n** — toggle bit `n` (flip its current value)
- **QUERY n** — print `1` if bit `n` is set, `0` if it is clear (does NOT modify the register)

After all commands, print the final register value on its own line.

## Skills Practiced

- `value |= (1 << n)` for SET
- `value &= ~(1 << n)` for CLEAR
- `value ^= (1 << n)` for TOGGLE
- `(value >> n) & 1` for QUERY

## Constraints

- Bit positions are always in the range `[0, 30]`.
- There are between 1 and 200 commands.
- QUERY output appears immediately (one line per QUERY, before the final register line).

## Sample Interaction

**Input:**
```
SET 3
SET 5
TOGGLE 3
QUERY 5
CLEAR 5
QUERY 5
```

**Output:**
```
1
0
32
```

- SET 3 → register = 8 (bit 3)
- SET 5 → register = 40 (bits 3 and 5)
- TOGGLE 3 → register = 32 (bit 5 only, bit 3 flipped off)
- QUERY 5 → print `1` (bit 5 is set)
- CLEAR 5 → register = 0
- QUERY 5 → print `0` (bit 5 is clear)
- Final register = `0`

## Getting Started

Open the code editor, choose Python, and implement the interpreter. Use `int` (Python integers are arbitrary precision, but keep values in unsigned 32-bit range by masking with `0xFFFFFFFF` after each operation for correctness on large bit positions).
