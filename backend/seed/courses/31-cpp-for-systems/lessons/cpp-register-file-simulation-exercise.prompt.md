# Prompt: Simulate a Register File and Load/Store

## Problem Description

Simulate a minimal RISC-V-like execution environment consisting of:

- 32 general-purpose 32-bit registers `x0`–`x31`, all initialised to 0. `x0` is hardwired to zero (reads always return 0; writes are silently discarded).
- 64 KiB of byte-addressable memory (addresses 0–65535), all initialised to 0. Storage is little-endian.

Process a sequence of commands and print output for each `PRINT` command.

## Commands

### SET rd val
Write the 32-bit unsigned value `val` to register `x[rd]`.
- `rd` is an integer 0–31.
- `val` is a non-negative integer that fits in 32 bits (0 <= val <= 4294967295).
- If `rd == 0`, the write is silently ignored.

### ADD rd rs1 rs2
`x[rd] = (x[rs1] + x[rs2]) mod 2^32`
- All three are register indices 0–31.
- If `rd == 0`, the result is discarded.

### SW rs2 offset rs1
Store the 32-bit value of `x[rs2]` to memory address `(x[rs1] + offset) mod 65536` as four bytes in little-endian order.
- `offset` is a signed decimal integer (-2048 <= offset <= 2047).
- The effective address is computed as `(x[rs1] + offset) & 0xFFFF` (wraps within 64 KiB).
- Assume the access is always 4-byte aligned within the 64 KiB window.

### LW rd offset rs1
Load a 32-bit little-endian value from memory address `(x[rs1] + offset) & 0xFFFF` into `x[rd]`.
- If `rd == 0`, the result is discarded.

### PRINT rd
Print the current unsigned decimal value of `x[rd]` followed by a newline.

## Input Format

- First line: integer `N` (1 <= N <= 200), number of commands.
- Next `N` lines: one command per line.

## Output Format

One line of output (unsigned decimal integer) for each `PRINT` command encountered, in order.

## Constraints

- 1 <= N <= 200
- Register indices: 0–31
- val in SET: 0 <= val <= 4294967295
- offset in SW/LW: -2048 <= offset <= 2047
- All effective memory addresses after wrapping will be valid (0–65532) for 4-byte access.
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input

```
7
SET 1 100
SET 2 200
ADD 3 1 2
PRINT 3
SW 3 0 0
LW 4 0 1
PRINT 4
```

## Sample Output

```
300
0
```

## Explanation

- `SET 1 100`: x1 = 100
- `SET 2 200`: x2 = 200
- `ADD 3 1 2`: x3 = 100 + 200 = 300
- `PRINT 3`: prints 300
- `SW 3 0 0`: store x3=300 to address x0+0 = 0 (little-endian bytes: 0x2C,0x01,0x00,0x00)
- `LW 4 0 1`: load from address x1+0 = 100; address 100 was never written, contains 0
- `PRINT 4`: prints 0
