# Exercise: Simulate ALU Add and Set Flags

In this exercise you will implement a software model of an 8-bit ALU adder that computes the result of adding two unsigned 8-bit values and correctly sets all four status flags: **Zero**, **Carry**, **Sign**, and **Overflow**.

## What You Will Implement

You will write a program that:

1. Reads pairs of signed integers (each in the range -128 to 127, representing 8-bit two's complement values) from standard input.
2. For each pair, performs an 8-bit ALU addition — the same operation a hardware ALU performs.
3. Prints the 8-bit result (as an unsigned value 0-255) and the four flag values (0 or 1) in the format shown below.

This simulates exactly what happens inside the ALU when the CPU executes an `ADD` instruction and latches the status flags.

## Flag Definitions

| Flag | When set (= 1) |
|------|---------------|
| Z (Zero) | Result is 0x00 |
| C (Carry) | Unsigned sum exceeded 255 (carry-out from bit 7) |
| N (Sign/Negative) | Bit 7 of result is 1 |
| V (Overflow) | Signed result outside -128..127 (carry-in to bit 7 differs from carry-out of bit 7) |

## What to Read

Before attempting the exercise, review the lessons:

- **Half Adders and Full Adders** — how carries propagate bit by bit
- **ALU Status Flags: Zero, Carry, Sign, Overflow** — precise flag definitions and the hardware formula for overflow

## Starter Approach

```python
# Read A and B as signed integers, treat their 8-bit patterns in the adder
# Compute: result_full = (a & 0xFF) + (b & 0xFF)
# result   = result_full & 0xFF
# C        = result_full >> 8
# Z        = 1 if result == 0 else 0
# N        = result >> 7
# V        = 1 if signs of a and b are equal but result sign differs
```

Work through the test cases manually first to verify your flag logic before coding.
