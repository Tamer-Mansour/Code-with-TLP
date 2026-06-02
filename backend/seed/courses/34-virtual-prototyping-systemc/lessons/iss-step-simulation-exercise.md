# Step a Tiny ISS and Report Final Register State

In this exercise you will implement a minimal Instruction-Set Simulator for a simple 8-register, 16-bit RISC architecture. Your simulator reads a program from standard input and steps through it instruction by instruction, updating the register file after each instruction. At the end of the program (when a HALT instruction is reached), your simulator prints the final value of every register.

## What You Will Implement

Your ISS must support the following instruction set:

| Mnemonic | Encoding | Operation |
|---|---|---|
| `LOAD Rd, imm` | `0 ddd iiiiiiii` | `Rd = imm` (8-bit unsigned immediate) |
| `ADD Rd, Rs1, Rs2` | `1 ddd sss ttt 00` | `Rd = Rs1 + Rs2` (mod 256) |
| `SUB Rd, Rs1, Rs2` | `1 ddd sss ttt 01` | `Rd = Rs1 - Rs2` (mod 256, unsigned) |
| `AND Rd, Rs1, Rs2` | `1 ddd sss ttt 10` | `Rd = Rs1 & Rs2` |
| `OR  Rd, Rs1, Rs2` | `1 ddd sss ttt 11` | `Rd = Rs1 \| Rs2` |
| `HALT` | `1 111 000 000 00` | Stop simulation |

Registers are R0–R7, each holding an 8-bit unsigned value initialized to 0. R0 is a general-purpose register (it is NOT hardwired to zero in this architecture).

## Input Format

The program is given as a series of 16-bit instructions in decimal, one per line. Each value fits in `[0, 65535]`. The last instruction is always HALT.

## Output Format

After HALT, print the register file as 8 lines:

```
R0=<value>
R1=<value>
...
R7=<value>
```

Values are printed as unsigned decimal integers in `[0, 255]`.

## Example

**Input:**
```
5        <- LOAD R0, 5   (binary: 0 000 00000101)
261      <- LOAD R1, 5   (binary: 0 001 00000101)
32768    <- ADD R0, R0, R1 (binary: 1 000 000 001 00 → opcode=1, d=0, s=0, t=1, op=00)
57344    <- HALT          (binary: 1 111 000 000 00)
```

**Output:**
```
R0=10
R1=5
R2=0
R3=0
R4=0
R5=0
R6=0
R7=0
```

## What to Implement

Write a Python program (`solution.py`) that:

1. Reads instruction words from stdin, one integer per line.
2. Steps through the fetch-execute loop.
3. On HALT (word == `0b1_111_000_000_00` = 57344), stops.
4. Prints `R0=` through `R7=` with their final 8-bit values.

This exercise reinforces the decode-execute loop structure you studied in the reading lessons. Focus on correct bit-field extraction — the most common bug in ISS implementations is off-by-one bit shifts in the decode step.
