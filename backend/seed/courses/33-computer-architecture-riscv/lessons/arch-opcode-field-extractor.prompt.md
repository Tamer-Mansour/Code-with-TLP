# Prompt: Extract Opcode Fields from an Instruction Word

## Problem Statement

Given one or more 32-bit RISC-V instruction words (encoded as unsigned decimal integers), extract the six standard field values and print them.

The RISC-V RV32 instruction format places fields at **fixed bit positions** across all instruction types:

```
Bits [6:0]   → opcode  (7 bits)
Bits [11:7]  → rd      (5 bits)
Bits [14:12] → funct3  (3 bits)
Bits [19:15] → rs1     (5 bits)
Bits [24:20] → rs2     (5 bits)
Bits [31:25] → funct7  (7 bits)
```

## Input Format

```
N
word_1
word_2
...
word_N
```

- Line 1: integer `N` (1 ≤ N ≤ 100) — number of instruction words.
- Lines 2 to N+1: one unsigned decimal integer per line representing a 32-bit instruction word (0 ≤ word ≤ 4294967295).

## Output Format

For each instruction word, print exactly one line:

```
opcode=<opcode> rd=<rd> funct3=<funct3> rs1=<rs1> rs2=<rs2> funct7=<funct7>
```

All values are printed as **decimal integers** (no leading zeros, no `0x` prefix).

## Constraints

- 1 ≤ N ≤ 100
- 0 ≤ each word ≤ 4294967295 (fits in a 32-bit unsigned integer)
- No invalid input; each number fits on a single line.
- Pure standard library only; read from stdin, print to stdout.

## Sample Input

```
3
4391603
4391571
4302083
```

## Sample Output

```
opcode=51 rd=5 funct3=0 rs1=6 rs2=4 funct7=0
opcode=19 rd=5 funct3=0 rs1=6 rs2=4 funct7=0
opcode=3 rd=10 funct3=2 rs1=3 rs2=4 funct7=0
```

### Explanation of the sample

- `4391603` = `0x004302B3` → `add x5, x6, x4`  (R-type, opcode=51=0x33)
- `4391571` = `0x00430293` → `addi x5, x6, 4`  (I-type, opcode=19=0x13)
- `4302083` = `0x0041A503` → `lw x10, 4(x3)`   (I-type load, opcode=3=0x03)

## Notes

- Use Python bitwise operators: `&` for masking, `>>` for shifting.
- A 7-bit mask is `0x7F` (127 decimal).
- A 5-bit mask is `0x1F` (31 decimal).
- A 3-bit mask is `0x07` (7 decimal).
- Field at bits [N:M]: `(word >> M) & mask` where `mask` has `(N - M + 1)` ones.
