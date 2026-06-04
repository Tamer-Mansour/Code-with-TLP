# RISC-V R-Type Instruction Decoder

Decode RISC-V **R-type** instructions from their 32-bit hexadecimal machine code representation.

## R-Type Instruction Format

RISC-V R-type instructions have a fixed 32-bit layout:

```
Bits [31:25]  funct7  (7 bits)  — operation variant (e.g., ADD vs SUB)
Bits [24:20]  rs2     (5 bits)  — source register 2
Bits [19:15]  rs1     (5 bits)  — source register 1
Bits [14:12]  funct3  (3 bits)  — operation code
Bits [11:7]   rd      (5 bits)  — destination register
Bits [6:0]    opcode  (7 bits)  — instruction class
```

The opcode for all integer R-type arithmetic instructions in RISC-V is `0110011` in binary (decimal 51).

## Input Format

```
Line 1: T — number of test cases (1 <= T <= 10)
Each of the next T lines: one 8-digit hex string (the 32-bit instruction, e.g. 003100B3)
```

## Output Format

For each instruction, print the five decoded fields:

```
opcode: D
rd: D
funct3: D
rs1: D
rs2: D
funct7: D
```

where D is the decimal value of each field. Separate test cases with a blank line.

## Examples

**Input:**
```
2
003100B3
407302B3
```

**Output:**
```
opcode: 51
rd: 1
funct3: 0
rs1: 2
rs2: 3
funct7: 0

opcode: 51
rd: 5
funct3: 0
rs1: 6
rs2: 7
funct7: 32
```

**Explanation:**

Instruction `0x003100B3`:
- Binary: `0000 0000 0011 0001 0000 0000 1011 0011`
- opcode = bits[6:0] = `0110011` = 51 (R-type arithmetic)
- rd = bits[11:7] = `00001` = 1
- funct3 = bits[14:12] = `000` = 0 (ADD/SUB selector)
- rs1 = bits[19:15] = `00010` = 2
- rs2 = bits[24:20] = `00011` = 3
- funct7 = bits[31:25] = `0000000` = 0 → **ADD** (funct7=32 would mean SUB)

## Hints

- Use Python's `int(hex_str, 16)` to parse the hex value.
- Extract fields using bit shifts and masks:
  - `opcode = value & 0x7F` (mask for 7 bits)
  - `rd = (value >> 7) & 0x1F` (mask for 5 bits)
  - `funct3 = (value >> 12) & 0x7` (mask for 3 bits)
  - `rs1 = (value >> 15) & 0x1F`
  - `rs2 = (value >> 20) & 0x1F`
  - `funct7 = (value >> 25) & 0x7F`
