# Exercise Prompt: Step a Tiny ISS and Report Final Register State

## Architecture Specification

You are implementing an ISS for a tiny 8-register, 8-bit CPU. All registers (R0–R7) hold unsigned 8-bit values (0–255) and are initialized to 0. There is no register hardwired to zero.

Instructions are 16-bit words given as unsigned decimal integers. The encoding is:

### LOAD Instruction (bit 15 = 0)

```
Bit:  15   14 13 12   11..8   7 6 5 4 3 2 1 0
      0    [  Rd  ]  unused  [    imm8        ]
```

Operation: `Rd = imm8`

- `Rd` = bits [14:12] (register index 0–7, but not 7 — HALT uses that)
- `imm8` = bits [7:0] (unsigned 8-bit immediate, 0–255)

### ALU Instruction (bit 15 = 1)

```
Bit:  15   14 13 12   11 10 9   8 7 6   5 4 3 2   1 0
      1    [  Rd  ]  [ Rs1  ]  [Rs2 ]   unused    [op]
```

- `Rd`  = bits [14:12]
- `Rs1` = bits [11:9]
- `Rs2` = bits [8:6]
- `op`  = bits [1:0]

| op | Operation |
|---|---|
| 00 | `Rd = (Rs1 + Rs2) mod 256` |
| 01 | `Rd = (Rs1 - Rs2) mod 256` (unsigned, wraps) |
| 10 | `Rd = Rs1 & Rs2` |
| 11 | `Rd = Rs1 \| Rs2` |

### HALT Instruction

Word value **61440** (`0b1111000000000000`): bit15=1, Rd=7(111), Rs1=0, Rs2=0, op=00.

When HALT is encountered, stop execution immediately and print the register file.

## Input Format

- Each line contains exactly one unsigned decimal integer (the 16-bit instruction word).
- The last instruction is always HALT (61440).
- The program contains between 1 and 100 instructions inclusive.
- All integers are in range [0, 65535].

## Output Format

Print exactly 8 lines in this format:

```
R0=<value>
R1=<value>
R2=<value>
R3=<value>
R4=<value>
R5=<value>
R6=<value>
R7=<value>
```

Where each `<value>` is the unsigned decimal integer in [0, 255].

## Constraints

- 1 ≤ number of instructions ≤ 100
- All instruction words are valid per the specification above
- HALT is always the last instruction
- No division or multiplication instructions exist
- Time limit: 3000 ms
- Memory limit: 256 MB

## Sample Input 1

```
5
4099
41024
61440
```

## Sample Output 1

```
R0=5
R1=3
R2=8
R3=0
R4=0
R5=0
R6=0
R7=0
```

**Explanation:** `LOAD R0,5` → R0=5. `LOAD R1,3` → R1=3. `ADD R2,R0,R1` → R2=8. `HALT`.

## Sample Input 2

```
61440
```

## Sample Output 2

```
R0=0
R1=0
R2=0
R3=0
R4=0
R5=0
R6=0
R7=0
```

**Explanation:** Immediate HALT with all registers at their initial value of 0.
