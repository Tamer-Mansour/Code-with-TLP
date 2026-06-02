# Exercise: Classify Traps from mcause Codes

In this exercise you will write a program that reads RISC-V `mcause` register values and classifies each one into its trap category — identifying whether it is an exception or an interrupt and naming the specific cause.

## Background

The `mcause` CSR encodes a trap cause as follows:

- **Bit XLEN-1 (MSB):** `1` = interrupt, `0` = exception.
- **Bits XLEN-2:0:** The cause code number.

A 64-bit `mcause` value of `0x8000000000000007` means interrupt (MSB set) with code 7 (machine timer interrupt). A value of `0x000000000000000D` means exception (MSB clear) with code 13 (load page fault).

## What You Will Implement

You will write a Python program that:

1. Reads a series of `mcause` values from standard input (one per line, given as decimal integers).
2. For each value, prints a single line describing the trap:
   - Whether it is an `Interrupt` or `Exception`.
   - The cause name from the standard RISC-V cause table.
   - If the code is unknown/reserved, print `Unknown`.

## Cause Reference Table

Your program should know these cause names:

**Exceptions (I=0):**

| Code | Name |
|---|---|
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

**Interrupts (I=1):**

| Code | Name |
|---|---|
| 1 | Supervisor software interrupt |
| 3 | Machine software interrupt |
| 5 | Supervisor timer interrupt |
| 7 | Machine timer interrupt |
| 9 | Supervisor external interrupt |
| 11 | Machine external interrupt |

## Input / Output Format

- **Input:** One `mcause` value per line as an unsigned decimal integer.
- **Output:** One classification line per input value in the format:
  `<Type>: <Cause Name>`
  where `<Type>` is either `Interrupt` or `Exception`.

## Example

Input:
```
9223372036854775815
13
2
9223372036854775819
```

Output:
```
Interrupt: Machine timer interrupt
Exception: Load page fault
Exception: Illegal instruction
Interrupt: Machine software interrupt
```

## Skills Practiced

- Bit manipulation (extracting MSB and lower bits from 64-bit values).
- Table-driven dispatch using Python dictionaries.
- Translating hardware register semantics into readable output.
- Handling edge cases (reserved/unknown codes).
