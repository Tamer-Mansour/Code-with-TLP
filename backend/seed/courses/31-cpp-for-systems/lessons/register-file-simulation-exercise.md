# Exercise: Simulate a Register File and Load/Store

In this exercise you will build a minimal simulation of a RISC-V register file combined with a flat byte-addressable memory. You will process a sequence of simple register and memory operations and print the final state.

## What You Will Implement

Your program reads a series of commands that model register writes, memory stores, and memory loads, then answers queries about register values:

| Command | Semantics |
|---|---|
| `SET rd val` | Write 32-bit unsigned `val` to register `rd` (x0 always stays 0) |
| `ADD rd rs1 rs2` | `x[rd] = x[rs1] + x[rs2]` (32-bit wraparound) |
| `SW rs2 offset rs1` | Store 32-bit value of `x[rs2]` to address `x[rs1] + offset` |
| `LW rd offset rs1` | Load 32-bit value from address `x[rs1] + offset` into `x[rd]` |
| `PRINT rd` | Print the current value of `x[rd]` as an unsigned decimal integer |

## Correctness Rules

- Register `x0` is hardwired to zero: any `SET 0 val` or write targeting `x0` is silently ignored, and `x0` always reads as 0.
- Memory is byte-addressable and little-endian. Address range is 0–65535 (64 KiB). Addresses outside this range will not appear in the test cases.
- All values are 32-bit unsigned integers. Arithmetic wraps modulo 2^32.
- `offset` in `SW`/`LW` is a signed decimal integer in the range -2048 to 2047.

## Why This Matters

This exercise mirrors what happens inside a VP's main loop: a stream of decoded micro-operations updates a register file and memory, with loads and stores crossing the bus. Getting x0, sign-extension of the offset, and little-endian byte layout correct is exactly what interviewers probe.

## Example

Input:
```
SET 1 100
SET 2 200
ADD 3 1 2
PRINT 3
SW 3 0 0
LW 4 0 1
PRINT 4
```

Expected output:
```
300
0
```

Explanation: `ADD x3, x1, x2` = 300. `SW x3, 0(x0)` stores 300 to address 0 (but `x0 = 0` so address = 0 + 0 = 0). `LW x4, 0(x1)` loads from address `x1 + 0 = 100 + 0 = 100`, which has never been written and is therefore 0.

Open the coding environment and implement the simulation. The solution requires roughly 50 lines of Python.
