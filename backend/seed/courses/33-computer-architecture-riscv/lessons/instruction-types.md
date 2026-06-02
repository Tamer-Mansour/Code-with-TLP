# Instruction Types: Data, Arithmetic, Control

Every ISA organizes its instructions into functional groups. Understanding these groups lets you read disassembly fluently and reason about what a compiler is doing. The three major categories are **data-movement**, **arithmetic/logic**, and **control-flow** instructions.

## 1. Data-Movement Instructions

These instructions move values between registers, memory, and I/O ports. They do not compute a result — they transfer existing values.

| Sub-type | Example (RISC-V) | Meaning |
|---|---|---|
| Load from memory | `lw x5, 8(x6)` | x5 = Mem[x6 + 8] (32-bit word) |
| Store to memory | `sw x5, 8(x6)` | Mem[x6 + 8] = x5 |
| Load immediate | `lui x1, 0x12345` | x1 = 0x12345000 |
| Register copy | `mv x2, x3` (pseudo) | x2 = x3 (encoded as `addi x2, x3, 0`) |

RISC-V strictly separates memory-access instructions (loads/stores) from computation instructions. Only `lw`, `ld`, `sw`, `sd` (and their byte/half-word variants) touch memory. This **load-store architecture** simplifies the pipeline.

### Common pitfall

Sign extension on narrow loads:

```asm
lb  x1, 0(x2)    # load byte, SIGN-EXTEND to 32 bits
lbu x1, 0(x2)    # load byte, ZERO-EXTEND to 32 bits
```

Loading `0xFF` with `lb` gives `−1`; with `lbu` gives `255`. Mixing these is a classic C bug when a `char` is treated as a signed type unexpectedly.

## 2. Arithmetic and Logic Instructions

These instructions compute a new value from one or more source operands.

### Integer Arithmetic

```asm
add  x3, x1, x2    # x3 = x1 + x2
sub  x3, x1, x2    # x3 = x1 - x2
addi x3, x1, 10    # x3 = x1 + 10  (immediate form)
mul  x3, x1, x2    # x3 = lower 32 bits of x1 * x2  (M-extension)
```

RISC-V integer arithmetic wraps on overflow (two's-complement wraparound) — there is no overflow flag or exception for integer ADD/SUB.

### Shift Instructions

```asm
sll  x3, x1, x2    # x3 = x1 << x2  (logical left shift)
srl  x3, x1, x2    # x3 = x1 >> x2  (logical right, zero-fill)
sra  x3, x1, x2    # x3 = x1 >> x2  (arithmetic right, sign-fill)
```

> **Interview answer:** "Arithmetic right shift preserves the sign bit; logical right shift fills with zeros. Use `sra` to divide a signed integer by a power of two."

### Logical (Bitwise)

```asm
and  x3, x1, x2    # bitwise AND
or   x3, x1, x2    # bitwise OR
xor  x3, x1, x2    # bitwise XOR
```

Useful pattern — zero a register without loading a constant:

```asm
xor x1, x1, x1    # x1 = 0  (though RISC-V uses mv x1, x0 instead)
```

### Compare and Set

```asm
slt  x3, x1, x2    # x3 = (x1 < x2) ? 1 : 0  (signed)
sltu x3, x1, x2    # unsigned version
```

## 3. Control-Flow Instructions

Control-flow instructions change the **program counter (PC)** rather than a data register. They implement branches, loops, function calls, and returns.

### Conditional Branches

RISC-V uses compare-and-branch (not a flags register):

```asm
beq  x1, x2, label   # branch if x1 == x2
bne  x1, x2, label   # branch if x1 != x2
blt  x1, x2, label   # branch if x1 < x2 (signed)
bge  x1, x2, label   # branch if x1 >= x2 (signed)
bltu x1, x2, label   # unsigned variants
bgeu x1, x2, label
```

The offset is PC-relative and signed, allowing ±4 KiB range in the base encoding (12-bit immediate, scaled by 2).

### Unconditional Jump

```asm
jal  x1, label   # x1 = PC+4; PC = PC + offset  (jump and link)
jalr x1, x2, 0  # x1 = PC+4; PC = x2 + 0       (indirect jump)
```

`jal` with `rd = x0` (or the `j` pseudo-instruction) is a plain unconditional jump.

### Function Call Pattern

```asm
jal  ra, my_func    # call: save return address in ra (x1)
...
my_func:
    ...
    ret             # pseudo for: jalr x0, ra, 0  (return)
```

### System Calls

```asm
ecall               # transfer control to OS/supervisor
ebreak              # transfer to debugger
```

## Instruction Mix in Real Programs

Typical profiling of general-purpose C code:

```
~40% data movement  (loads dominate; stores ~25% of data moves)
~35% arithmetic/logic
~20% control flow
~5%  other (system, special)
```

This distribution motivates caching (loads are frequent), branch predictors (control-flow is frequent), and why RISC ISAs include very fast single-cycle ALU operations.
