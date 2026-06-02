# Prompt: Compute Effective Address for a RISC-V Load

## Problem Statement

Implement a program that simulates the RISC-V effective address calculation for load and store instructions.

Every RISC-V memory instruction computes:

```
effective_address = base_register_value + sign_extend(offset_12bit)
```

Rules:
- The offset is a 12-bit **signed** integer in the range [-2048, 2047].
- Sign-extension fills the upper bits with the sign bit of the 12-bit value.
- All arithmetic is modular: the result wraps modulo 2^64 (i.e., 64-bit unsigned addition).

## Input Format

```
N
base1 offset1
base2 offset2
...
baseN offsetN
```

- First line: integer N (1 <= N <= 100) — number of queries.
- Each of the next N lines contains two space-separated integers:
  - `base`: the base register value, given as a **non-negative decimal integer** (0 <= base < 2^64).
  - `offset`: the 12-bit signed offset, given as a **signed decimal integer** (-2048 <= offset <= 2047).

## Output Format

Print N lines. Each line must contain the effective address as:

```
0x<16 uppercase hex digits>
```

Zero-pad on the left so the hex portion is always exactly 16 characters (64 bits).

## Constraints

- 1 <= N <= 100
- 0 <= base < 2^64 (fits in Python's arbitrary-precision int)
- -2048 <= offset <= 2047
- Result must be computed modulo 2^64

## Sample Input

```
4
4096 16
4096 -8
18446744073709551615 1
0 -1
```

## Sample Output

```
0x0000000000001010
0x0000000000000FF8
0x0000000000000000
0xFFFFFFFFFFFFFFFF
```

## Explanation

- `4096 + 16 = 4112` → `0x1010`
- `4096 + (-8) = 4088` → `0xFF8` → zero-padded to `0x0000000000000FF8`
- `(2^64 - 1) + 1 = 2^64` → modulo 2^64 = 0 → `0x0000000000000000`
- `0 + (-1) = -1` → modulo 2^64 = `2^64 - 1 = 0xFFFFFFFFFFFFFFFF`

## Notes

- The offset may be negative; treat it as a standard Python signed integer (no extra sign-extension logic is needed since Python handles arbitrary-precision signed integers natively).
- Use the mask `(1 << 64) - 1` to reduce the result modulo 2^64.
- Format using Python's `f"0x{result:016X}"`.
