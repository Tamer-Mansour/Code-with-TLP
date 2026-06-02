# Exercise: Decode an mcause Value

In this exercise you will write a program that decodes a raw `mcause` register value and identifies the trap type in human-readable form.

## Background

`mcause` is an XLEN-bit register where the most significant bit (bit 31 for RV32, bit 63 for RV64) is the **interrupt bit**. When it is 1 the trap was an interrupt; when it is 0 the trap was an exception. The remaining lower bits encode the specific cause number.

For this exercise we work with **32-bit** `mcause` values (RV32). The interrupt bit is bit 31.

## What You Will Implement

Given a 32-bit unsigned integer representing `mcause`, your program must:

1. Determine whether the value represents an **interrupt** or an **exception**.
2. Extract the exception/interrupt code (lower 31 bits).
3. Print the human-readable name of the cause.

## Cause Name Table

Use these exact strings for your output:

**Exceptions (interrupt bit = 0):**

| Code | Name |
|------|------|
| 0    | Instruction address misaligned |
| 1    | Instruction access fault |
| 2    | Illegal instruction |
| 3    | Breakpoint |
| 4    | Load address misaligned |
| 5    | Load access fault |
| 6    | Store/AMO address misaligned |
| 7    | Store/AMO access fault |
| 8    | Environment call from U-mode |
| 9    | Environment call from S-mode |
| 11   | Environment call from M-mode |
| 12   | Instruction page fault |
| 13   | Load page fault |
| 15   | Store/AMO page fault |

**Interrupts (interrupt bit = 1):**

| Code | Name |
|------|------|
| 1    | Supervisor software interrupt |
| 3    | Machine software interrupt |
| 5    | Supervisor timer interrupt |
| 7    | Machine timer interrupt |
| 9    | Supervisor external interrupt |
| 11   | Machine external interrupt |

For any unrecognized code, print `Unknown cause`.

## Input / Output

- **Input**: a single line containing one 32-bit unsigned integer (decimal or hex with `0x` prefix).
- **Output**: a single line with the cause description in the format shown below.

## Example

```
Input:  2147483655
Output: Interrupt: Machine timer interrupt
```

```
Input:  8
Output: Exception: Environment call from U-mode
```

## Getting Started

```python
import sys

EXCEPTIONS = {
    0:  "Instruction address misaligned",
    1:  "Instruction access fault",
    2:  "Illegal instruction",
    3:  "Breakpoint",
    4:  "Load address misaligned",
    5:  "Load access fault",
    6:  "Store/AMO address misaligned",
    7:  "Store/AMO access fault",
    8:  "Environment call from U-mode",
    9:  "Environment call from S-mode",
    11: "Environment call from M-mode",
    12: "Instruction page fault",
    13: "Load page fault",
    15: "Store/AMO page fault",
}

INTERRUPTS = {
    1:  "Supervisor software interrupt",
    3:  "Machine software interrupt",
    5:  "Supervisor timer interrupt",
    7:  "Machine timer interrupt",
    9:  "Supervisor external interrupt",
    11: "Machine external interrupt",
}

def decode_mcause(raw):
    # TODO: implement this function
    pass

raw = int(input().strip(), 0)  # int(..., 0) handles both decimal and 0x hex
print(decode_mcause(raw))
```

Implement `decode_mcause` to produce the correct output.
