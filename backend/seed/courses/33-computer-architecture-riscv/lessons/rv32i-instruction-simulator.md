# Exercise: Execute RV32I Instructions on a Register File

In this exercise you will implement a simplified **RV32I instruction simulator** that processes a sequence of encoded RISC-V instructions and outputs the final register file state.

## What You Will Implement

Your program reads a stream of 32-bit RV32I instruction words (given in hexadecimal) and executes them against a register file initialised to all zeros. After all instructions are executed, it prints the final non-zero register values.

## Instructions to Support

You need to handle the following subset of RV32I:

| Opcode | Instruction(s) | funct3 / funct7 |
|---|---|---|
| `0x13` | ADDI | funct3=0x0 |
| `0x33` | ADD (funct7=0x00), SUB (funct7=0x20) | funct3=0x0 |
| `0x33` | AND, OR, XOR | funct3=0x7, 0x6, 0x4 |
| `0x13` | ANDI, ORI, XORI | funct3=0x7, 0x6, 0x4 |
| `0x13` | SLLI, SRLI, SRAI | funct3=0x1, 0x5 |

## Register Representation

- Registers are 32-bit (treat all values as unsigned 32-bit during storage; signed arithmetic applies where specified).
- `x0` is hardwired to zero — writes to it are silently discarded.
- Registers are named `x0`–`x31`.

## Input Format

```
N
hex_instr_1
hex_instr_2
...
hex_instr_N
```

- First line: number of instructions N (1 ≤ N ≤ 100).
- Next N lines: one 8-digit hexadecimal instruction word per line (no `0x` prefix).

## Output Format

Print each register that has a non-zero value after execution, one per line, in ascending register number order:

```
x<num>=<decimal_value>
```

If all registers are zero, print `all zero`.

## Constraints

- N ≤ 100 instructions.
- All instructions are valid encodings from the supported subset above.
- No memory instructions — only register-to-register and register-immediate operations.
- Values are unsigned 32-bit; print as unsigned decimal.

## Sample Input

```
3
00500513
00600593
00B50633
```

## Sample Output

```
x10=5
x11=6
x12=11
```

**Explanation:** `ADDI x10, x0, 5` → x10=5; `ADDI x11, x0, 6` → x11=6; `ADD x12, x10, x11` → x12=11.

## Tips

- Extract fields with bitmask and shift: `opcode = instr & 0x7F`, `rd = (instr >> 7) & 0x1F`, etc.
- Sign-extend I-type immediates: the 12-bit immediate lives in bits [31:20].
- For SRAI vs SRLI, check bit 30 of the instruction word.
- Remember: after every instruction, force `regs[0] = 0`.
