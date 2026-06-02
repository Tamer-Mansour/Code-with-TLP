# Set, Clear, and Toggle Bits in a Register

In this exercise you will implement three fundamental register operations — setting a bit, clearing a bit, and toggling a bit — given a register value and a bit position. This pattern appears in virtually every hardware driver and is the first thing embedded engineers reach for.

## What You Will Implement

You will write a Python program that reads a sequence of register manipulation commands from standard input and prints the resulting register value after each operation.

Each command is one of:
- `SET <register_value> <bit_position>` — sets the specified bit to 1
- `CLR <register_value> <bit_position>` — clears the specified bit to 0
- `TGL <register_value> <bit_position>` — toggles the specified bit

All register values are 8-bit unsigned integers (0–255). Bit positions are 0 (LSB) through 7 (MSB).

## Core Patterns to Use

```python
# Set bit N
result = reg | (1 << N)

# Clear bit N
result = reg & ~(1 << N)

# Toggle bit N
result = reg ^ (1 << N)
```

Remember to mask the final result to 8 bits: `result & 0xFF`.

## Input Format

- First line: integer T — number of operations
- Next T lines: `OPCODE reg_value bit_pos`

## Output Format

- T lines, each containing the resulting 8-bit register value as a **decimal** integer.

## Example

Input:
```
3
SET 0 3
CLR 255 0
TGL 170 1
```

Output:
```
8
254
168
```

Work through each operation, apply the correct bitwise formula, and output the result.
