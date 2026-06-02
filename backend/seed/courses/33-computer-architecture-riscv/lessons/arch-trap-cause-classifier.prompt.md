# Prompt: Classify Traps from mcause Codes

## Problem Description

You are writing firmware for a RISC-V system. Your trap handler logs raw `mcause` CSR values. Write a program that decodes each logged `mcause` value and prints a human-readable classification.

The `mcause` register is a 64-bit unsigned integer:
- If the **most significant bit (bit 63)** is `1`, the trap is an **Interrupt** and bits 62:0 are the interrupt code.
- If the **most significant bit** is `0`, the trap is an **Exception** and bits 62:0 are the exception code.

### Exception Codes (MSB = 0)

| Code | Cause Name |
|------|------------|
| 0 | Instruction address misaligned |
| 1 | Instruction access fault |
| 2 | Illegal instruction |
| 3 | Breakpoint |
| 4 | Load address misaligned |
| 5 | Load access fault |
| 6 | Store address misaligned |
| 7 | Store access fault |
| 8 | Environment call from U-mode |
| 9 | Environment call from S-mode |
| 11 | Environment call from M-mode |
| 12 | Instruction page fault |
| 13 | Load page fault |
| 15 | Store page fault |

Any other exception code: output `Unknown`.

### Interrupt Codes (MSB = 1)

| Code | Cause Name |
|------|------------|
| 1 | Supervisor software interrupt |
| 3 | Machine software interrupt |
| 5 | Supervisor timer interrupt |
| 7 | Machine timer interrupt |
| 9 | Supervisor external interrupt |
| 11 | Machine external interrupt |

Any other interrupt code: output `Unknown`.

## Input Format

- First line: a single integer `N` (1 <= N <= 100) — the number of `mcause` values.
- Next `N` lines: one unsigned decimal integer per line representing a 64-bit `mcause` value (0 <= value < 2^64).

## Output Format

For each `mcause` value, print exactly one line:
```
<Type>: <Cause Name>
```
Where `<Type>` is either `Interrupt` or `Exception`, or just `Unknown` for unrecognized codes.

## Constraints

- 1 <= N <= 100
- 0 <= mcause value < 2^64
- All values fit in a 64-bit unsigned integer (Python handles big integers natively)
- No trailing spaces; output lines end with a newline
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input

```
6
9223372036854775815
13
2
9223372036854775811
0
9223372036854775808
```

## Sample Output

```
Interrupt: Machine timer interrupt
Exception: Load page fault
Exception: Illegal instruction
Interrupt: Machine software interrupt
Exception: Instruction address misaligned
Unknown
```

## Explanation of Sample

- `9223372036854775815` = 2^63 + 7 -> MSB=1 (Interrupt), code=7 -> Machine timer interrupt
- `13` = 0x0D -> MSB=0 (Exception), code=13 -> Load page fault
- `2` -> MSB=0 (Exception), code=2 -> Illegal instruction
- `9223372036854775811` = 2^63 + 3 -> MSB=1 (Interrupt), code=3 -> Machine software interrupt
- `0` -> MSB=0 (Exception), code=0 -> Instruction address misaligned
- `9223372036854775808` = 2^63 + 0 -> MSB=1 (Interrupt), code=0 -> Unknown (code 0 is reserved)

## Notes for Implementers

- Use Python's arbitrary precision integers — no overflow concerns.
- Extract the interrupt bit: `interrupt_bit = (mcause >> 63) & 1`
- Extract the code: `code = mcause & ((1 << 63) - 1)`
- Use dictionaries for O(1) cause lookup.
- If a code is not in the lookup table, print `Unknown` (no `Interrupt:` or `Exception:` prefix).
