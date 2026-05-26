# Assembly Language Basics

Assembly language is a human-readable representation of a CPU's machine code. Each assembly statement corresponds directly to one machine instruction (or one micro-op on CISC). This lesson uses RISC-V assembly because of its clean, orthogonal design.

## Registers (RISC-V)

RISC-V has 32 general-purpose registers, `x0`–`x31`, with ABI names:

| Register | ABI Name | Role |
|---|---|---|
| x0 | zero | Always reads as 0; writes are ignored |
| x1 | ra | Return address |
| x2 | sp | Stack pointer |
| x5–x7 | t0–t2 | Temporaries |
| x10–x17 | a0–a7 | Function arguments / return values |
| x18–x27 | s0–s11 | Saved registers (callee must preserve) |
| x28–x31 | t3–t6 | More temporaries |

## Instruction Formats

### R-type (Register-Register)

```
add  rd, rs1, rs2    # rd = rs1 + rs2
sub  rd, rs1, rs2    # rd = rs1 - rs2
and  rd, rs1, rs2    # rd = rs1 & rs2
or   rd, rs1, rs2    # rd = rs1 | rs2
xor  rd, rs1, rs2    # rd = rs1 ^ rs2
sll  rd, rs1, rs2    # rd = rs1 << rs2  (shift left logical)
srl  rd, rs1, rs2    # rd = rs1 >> rs2  (shift right logical)
sra  rd, rs1, rs2    # rd = rs1 >>> rs2 (shift right arithmetic, sign-extend)
```

### I-type (Immediate)

The immediate is a 12-bit signed constant embedded in the instruction:

```
addi rd, rs1, imm    # rd = rs1 + imm
lw   rd, imm(rs1)    # rd = Memory[rs1 + imm]  (load word)
```

### S-type (Store)

```
sw   rs2, imm(rs1)   # Memory[rs1 + imm] = rs2
```

### B-type (Branch)

```
beq  rs1, rs2, label  # if rs1 == rs2, PC = label
bne  rs1, rs2, label  # if rs1 != rs2, PC = label
blt  rs1, rs2, label  # if rs1 <  rs2 (signed), PC = label
bge  rs1, rs2, label  # if rs1 >= rs2 (signed), PC = label
```

## A Complete Example: Summing an Array

```asm
# Sum an array of n 32-bit integers
# a0 = base address of array
# a1 = n (number of elements)
# Returns: a0 = sum

sum_array:
    li   t0, 0          # t0 = sum = 0
    li   t1, 0          # t1 = i = 0
loop:
    bge  t1, a1, done   # if i >= n, exit loop
    slli t2, t1, 2      # t2 = i * 4 (byte offset for word array)
    add  t3, a0, t2     # t3 = &array[i]
    lw   t4, 0(t3)      # t4 = array[i]
    add  t0, t0, t4     # sum += array[i]
    addi t1, t1, 1      # i++
    j    loop
done:
    mv   a0, t0         # return value in a0
    ret
```

## Addressing Modes

Most RISC ISAs support only a handful of addressing modes:

| Mode | Syntax | Effective Address |
|---|---|---|
| Register indirect | 0(rs1) | rs1 |
| Base + offset | imm(rs1) | rs1 + imm |
| PC-relative | label | PC + offset |

CISC ISAs (x86) add: scaled index, base+index+displacement, and more.

## From C to Assembly

```c
int x = a + b * 2;
```

Compiles to (approximately):

```asm
slli t0, s1, 1     # t0 = b * 2
add  s0, s0, t0    # a = a + t0  (s0=a, s1=b)
```

Understanding assembly is essential for performance-critical code, debugging compiler output (via `objdump -d`), and understanding security vulnerabilities like buffer overflows.
