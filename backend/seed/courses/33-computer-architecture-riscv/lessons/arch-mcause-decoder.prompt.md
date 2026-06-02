# Prompt: Decode an mcause Value

## Problem Statement

Given a 32-bit unsigned integer representing the RISC-V `mcause` CSR value, decode and print its human-readable trap description.

The `mcause` register uses **bit 31** as the interrupt bit:
- Bit 31 = 1 → Interrupt; the interrupt code is in bits [30:0].
- Bit 31 = 0 → Exception; the exception code is in bits [30:0].

## Exception Codes (bit 31 = 0)

| Code | Description |
|------|-------------|
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

## Interrupt Codes (bit 31 = 1)

| Code | Description |
|------|-------------|
| 1    | Supervisor software interrupt |
| 3    | Machine software interrupt |
| 5    | Supervisor timer interrupt |
| 7    | Machine timer interrupt |
| 9    | Supervisor external interrupt |
| 11   | Machine external interrupt |

## Input Format

A single line containing one non-negative integer representing a 32-bit `mcause` value. The integer may be:
- A **decimal** number (e.g., `8`), or
- A **hexadecimal** number with a `0x` prefix (e.g., `0x80000007`).

The value is always in the range [0, 2^32 - 1].

## Output Format

A single line in one of these formats:
- `Exception: <description>` if bit 31 is 0.
- `Interrupt: <description>` if bit 31 is 1.
- `Exception: Unknown cause` or `Interrupt: Unknown cause` for unrecognized codes.

## Constraints

- Input is a valid 32-bit unsigned integer (0 to 4294967295).
- No multi-line input; exactly one value per run.
- Output exactly one line with no trailing spaces.

## Sample Input / Output

**Sample 1**
```
Input:  8
Output: Exception: Environment call from U-mode
```

**Sample 2**
```
Input:  0x80000007
Output: Interrupt: Machine timer interrupt
```

**Sample 3**
```
Input:  2147483651
Output: Interrupt: Machine software interrupt
```
*(2147483651 = 0x80000003)*

**Sample 4**
```
Input:  2
Output: Exception: Illegal instruction
```

**Sample 5**
```
Input:  0x80000010
Output: Interrupt: Unknown cause
```
*(code 16 is not in the standard table)*
