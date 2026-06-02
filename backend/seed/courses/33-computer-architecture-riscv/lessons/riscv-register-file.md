# The RISC-V Register File: 32 GP Registers

RISC-V exposes exactly **32 general-purpose integer registers**, each 32 bits wide in RV32 or 64 bits wide in RV64. This fixed-size register file is one of the defining features of the RISC philosophy: enough registers to keep hot data on-chip and avoid memory round-trips, yet few enough that encoding fits cleanly in a 5-bit field inside every instruction word.

## Register Numbering

Registers are named **x0 through x31**. Every R-type and I-type instruction encodes source and destination registers using 5-bit fields (`rs1`, `rs2`, `rd`), which is why 32 registers — not 64 — is the natural choice: 2^5 = 32.

```
31      25 24   20 19   15 14  12 11    7 6       0
| funct7  |  rs2  |  rs1  |funct3|  rd   | opcode  |  R-type
```

- Bits [19:15] select `rs1` (0–31)
- Bits [24:20] select `rs2` (0–31)
- Bits [11:7]  select `rd`  (0–31)

## What Makes a Register File "General-Purpose"?

General-purpose means any register (except x0) can hold any integer value: a pointer, a counter, a function argument, or a boolean flag. There are no dedicated arithmetic-only or address-only registers as found in some older architectures. This uniformity simplifies both the compiler and the hardware — the register file is a small, fast SRAM array with two read ports and one write port per cycle.

## The 32 Registers at a Glance

| Number | ABI Name | Conventional Role |
|--------|----------|-------------------|
| x0 | zero | Hardwired 0 |
| x1 | ra | Return address |
| x2 | sp | Stack pointer |
| x3 | gp | Global pointer |
| x4 | tp | Thread pointer |
| x5–x7 | t0–t2 | Temporaries (caller-saved) |
| x8–x9 | s0–s1 | Saved registers (callee-saved) |
| x10–x17 | a0–a7 | Function arguments / return values |
| x18–x27 | s2–s11 | Saved registers (callee-saved) |
| x28–x31 | t3–t6 | Temporaries (caller-saved) |

ABI names are a software convention layered on top of the hardware numbers. The hardware itself treats x1–x31 identically.

## Why 32 and Not More?

Increasing the register count to 64 would require 6-bit register fields, adding 3 bits to every instruction and breaking the 32-bit fixed-width encoding. Studies show that 32 registers already capture the hot working set for most loops and functions. Compilers rarely spill to memory when 32 registers are available — making more registers a diminishing return for a real encoding cost.

## Worked Example: Reading an R-type Encoding

```asm
add x5, x6, x7     # rd=x5, rs1=x6, rs2=x7
```

Binary breakdown:

```
funct7   rs2    rs1  funct3  rd     opcode
0000000 00111 00110  000   00101  0110011
```

- `rs2 = 00111` = 7 → x7
- `rs1 = 00110` = 6 → x6
- `rd  = 00101` = 5 → x5

This shows exactly how a 5-bit field maps to the register file.

## Common Pitfalls

- **Confusing register number with value.** x5 is the name of a storage slot; it holds whatever value was last written.
- **Treating ABI names as hardware.** The chip only knows x0–x31. ABI names like `ra` or `sp` are a calling-convention promise, not enforced by hardware.
- **Assuming RV32 and RV64 share register widths.** In RV64, each register is 64 bits; a 32-bit operation on `x5` sign-extends the result into the full 64-bit register.

> **Interview answer:** RISC-V has 32 general-purpose integer registers (x0–x31), each sized to the base ISA width (32 or 64 bits). They are encoded in 5-bit fields inside every instruction, and x0 is hardwired to zero.
