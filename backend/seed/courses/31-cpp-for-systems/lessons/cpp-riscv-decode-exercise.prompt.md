# Prompt: Decode RISC-V R-Type Instructions

## Problem Description

You are given a sequence of 32-bit RISC-V instruction words encoded as unsigned hexadecimal integers (no `0x` prefix, uppercase or lowercase accepted). Each word is an R-type instruction with `opcode = 0x33`. Your task is to decode each instruction and print its disassembly.

## R-Type Field Extraction

```
Bits [6:0]   -> opcode  (always 0x33 for R-type)
Bits [11:7]  -> rd      (destination register, 0-31)
Bits [14:12] -> funct3  (selects operation within group)
Bits [19:15] -> rs1     (source register 1, 0-31)
Bits [24:20] -> rs2     (source register 2, 0-31)
Bits [31:25] -> funct7  (distinguishes ADD/SUB and SRL/SRA)
```

## Operation Table

| funct3 | funct7  | Mnemonic |
|--------|---------|----------|
| 0x0    | 0x00    | ADD      |
| 0x0    | 0x20    | SUB      |
| 0x4    | 0x00    | XOR      |
| 0x6    | 0x00    | OR       |
| 0x7    | 0x00    | AND      |
| 0x1    | 0x00    | SLL      |
| 0x5    | 0x00    | SRL      |
| 0x5    | 0x20    | SRA      |
| 0x2    | 0x00    | SLT      |
| 0x3    | 0x00    | SLTU     |

Any combination not in the table above should output `UNKNOWN`.

## Input Format

- The first line contains a single integer `N` (1 <= N <= 100): the number of instructions.
- The next `N` lines each contain one 32-bit unsigned integer in hexadecimal (no `0x` prefix, 1–8 hex digits).

## Output Format

For each instruction, print exactly one line:

```
MNEMONIC x<rd>, x<rs1>, x<rs2>
```

where `<rd>`, `<rs1>`, `<rs2>` are decimal integers in the range 0–31. If the instruction is not a recognised R-type operation, print `UNKNOWN`.

## Constraints

- 1 <= N <= 100
- Each value fits in a 32-bit unsigned integer.
- All inputs have `opcode == 0x33`; you do not need to validate the opcode field.
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input

```
5
00B50533
40B50533
00B54533
00B56533
00B57533
```

## Sample Output

```
ADD x10, x10, x11
SUB x10, x10, x11
XOR x10, x10, x11
OR x10, x10, x11
AND x10, x10, x11
```

## Explanation

- `00B50533`: funct7=0x00, rs2=x11, rs1=x10, funct3=0x0, rd=x10 -> ADD x10, x10, x11
- `40B50533`: funct7=0x20, same fields -> SUB x10, x10, x11
- `00B54533`: funct3=0x4 -> XOR
- `00B56533`: funct3=0x6 -> OR
- `00B57533`: funct3=0x7 -> AND
