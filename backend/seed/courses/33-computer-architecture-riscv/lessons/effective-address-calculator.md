# Exercise: Compute Effective Address for a Load

In this exercise you will implement a simulator that computes the **effective address** for RISC-V load and store instructions using the base-plus-offset model.

## Background

Every RISC-V load and store instruction encodes a 12-bit signed immediate offset. The CPU computes:

```
effective_address = base_register_value + sign_extend(offset_12bit)
```

Key rules:

- The offset is a **signed** 12-bit integer, ranging from -2048 to +2047.
- The 12-bit value is sign-extended to the full address width (64 bits for RV64) before addition.
- The result wraps around modulo 2^64 (unsigned 64-bit addition).

## What You Will Implement

Write a Python program that reads a series of (base_value, offset) pairs from stdin. For each pair, compute and print the effective address as an **unsigned 64-bit hexadecimal** value, zero-padded to 16 hex digits.

Input format:

- First line: integer N — number of queries
- Next N lines: two space-separated integers on each line
  - `base`: the value in the base register (0 to 2^64 - 1, given as a non-negative decimal integer)
  - `offset`: the 12-bit signed offset (-2048 to 2047, given as a signed decimal integer)

Output format:

- N lines, each containing the effective address as `0x` followed by exactly 16 uppercase hex digits.

## Example

Input:
```
3
4096 16
4096 -8
18446744073709551615 1
```

Output:
```
0x0000000000001010
0x0000000000000FF8
0x0000000000000000
```

Explanation:
- `4096 + 16 = 4112 = 0x1010`
- `4096 + (-8) = 4088 = 0xFF8`
- `0xFFFFFFFFFFFFFFFF + 1 = 0` (wraps modulo 2^64)

## Skills Practiced

- Binary/hex arithmetic
- Two's complement sign extension
- Unsigned integer overflow (modular arithmetic)
- Translating RISC-V addressing rules to code

Start by implementing the sign-extension step, then perform the addition modulo 2^64, and format the result as a 16-digit uppercase hexadecimal string.
