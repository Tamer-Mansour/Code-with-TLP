# Prompt: arch-rv32i-instruction-simulator

## Problem Statement

Implement a simplified RV32I register-file simulator. Given a list of 32-bit RISC-V instruction words in hexadecimal, execute them against a register file (x0–x31) initialised to all zeros and report the final state of any non-zero registers.

## Supported Instructions

Decode using the standard RV32I bit fields:
- `opcode = instr & 0x7F`
- `rd     = (instr >>  7) & 0x1F`
- `funct3 = (instr >> 12) & 0x07`
- `rs1    = (instr >> 15) & 0x1F`
- `rs2    = (instr >> 20) & 0x1F`
- `funct7 = (instr >> 25) & 0x7F`
- I-type imm (12 bits, sign-extended): `imm = instr >> 20` with sign extension from bit 11

Instructions to handle:

| opcode | funct3 | funct7 | Instruction | Operation |
|--------|--------|--------|-------------|-----------|
| 0x13 | 0x0 | — | ADDI | rd = rs1 + imm |
| 0x33 | 0x0 | 0x00 | ADD | rd = rs1 + rs2 |
| 0x33 | 0x0 | 0x20 | SUB | rd = rs1 - rs2 |
| 0x33 | 0x7 | 0x00 | AND | rd = rs1 & rs2 |
| 0x33 | 0x6 | 0x00 | OR | rd = rs1 \| rs2 |
| 0x33 | 0x4 | 0x00 | XOR | rd = rs1 ^ rs2 |
| 0x13 | 0x7 | — | ANDI | rd = rs1 & imm |
| 0x13 | 0x6 | — | ORI | rd = rs1 \| imm |
| 0x13 | 0x4 | — | XORI | rd = rs1 ^ imm |
| 0x13 | 0x1 | 0x00 | SLLI | rd = rs1 << shamt |
| 0x13 | 0x5 | 0x00 | SRLI | rd = rs1 >> shamt (logical) |
| 0x13 | 0x5 | 0x20 | SRAI | rd = rs1 >> shamt (arithmetic) |

For shift instructions, `shamt = (instr >> 20) & 0x1F` and `funct7 = (instr >> 25) & 0x7F`.

All register values are stored and printed as **unsigned 32-bit integers** (range 0 to 4294967295). Arithmetic wraps modulo 2^32. For SRAI, perform arithmetic right shift on the signed interpretation, then store as unsigned 32-bit.

`x0` is hardwired zero — writes are silently discarded.

## Input Format

```
N
hex_instr_1
hex_instr_2
...
hex_instr_N
```

- Line 1: integer N (1 ≤ N ≤ 100).
- Lines 2..N+1: exactly 8 uppercase or lowercase hex characters representing the 32-bit instruction word.

## Output Format

After executing all instructions, print each register with a non-zero value in ascending order of register number:

```
x<num>=<unsigned_decimal_value>
```

If all registers are zero, print the single line:

```
all zero
```

## Constraints

- 1 ≤ N ≤ 100
- All instructions are valid encodings from the supported subset.
- No memory or branch instructions.
- No instruction writes to x0 in a meaningful way (though your code must guard against it).

## Sample Input 1

```
3
00500513
00600593
00B50633
```

## Sample Output 1

```
x10=5
x11=6
x12=11
```

**Explanation:**
- `00500513` → ADDI x10, x0, 5  → x10 = 0 + 5 = 5
- `00600593` → ADDI x11, x0, 6  → x11 = 0 + 6 = 6
- `00B50633` → ADD  x12, x10, x11 → x12 = 5 + 6 = 11

## Sample Input 2

```
2
FFF00513
00000013
```

## Sample Output 2

```
x10=4294967295
```

**Explanation:**
- `FFF00513` → ADDI x10, x0, -1 (imm=0xFFF sign-extended = -1) → x10 = 0xFFFFFFFF = 4294967295
- `00000013` → NOP (ADDI x0, x0, 0) — x0 stays 0

## Starter Code (Python)

```python
import sys

def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

def simulate(instructions):
    regs = [0] * 32

    for instr in instructions:
        opcode = instr & 0x7F
        rd     = (instr >>  7) & 0x1F
        funct3 = (instr >> 12) & 0x07
        rs1    = (instr >> 15) & 0x1F
        rs2    = (instr >> 20) & 0x1F
        funct7 = (instr >> 25) & 0x7F
        imm_i  = sign_extend(instr >> 20, 12)
        shamt  = (instr >> 20) & 0x1F

        result = 0
        if opcode == 0x13:  # I-type
            # TODO: implement ADDI, ANDI, ORI, XORI, SLLI, SRLI, SRAI
            pass
        elif opcode == 0x33:  # R-type
            # TODO: implement ADD, SUB, AND, OR, XOR
            pass

        if rd != 0:
            regs[rd] = result & 0xFFFFFFFF
        regs[0] = 0

    return regs

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    instructions = [int(data[i+1], 16) for i in range(n)]
    regs = simulate(instructions)
    output = [f"x{i}={regs[i]}" for i in range(32) if regs[i] != 0]
    print('\n'.join(output) if output else "all zero")

main()
```
