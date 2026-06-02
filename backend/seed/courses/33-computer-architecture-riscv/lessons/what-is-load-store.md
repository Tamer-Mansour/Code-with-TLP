# What Is a Load-Store Architecture?

A load-store architecture is a CPU design philosophy where **only dedicated load and store instructions can access memory**. All other instructions — arithmetic, logic, comparisons — operate exclusively on registers. This is the defining trait of RISC processors including RISC-V, ARM, and MIPS.

## The Core Constraint

In a load-store ISA, you cannot, for example, add a value directly from memory to a register in a single instruction. You must:

1. Load the memory value into a register.
2. Perform the operation on two registers.
3. Optionally store the result back to memory.

```asm
# RISC-V example: add value at address in x1 to register x2
lw   x3, 0(x1)     # Step 1: load word from memory[x1+0] into x3
add  x2, x2, x3    # Step 2: add register to register
sw   x2, 0(x1)     # Step 3: store result back (if needed)
```

On a CISC architecture like x86, a single `ADD [mem], reg` instruction can do all three steps. RISC-V explicitly forbids this.

## Why Does This Restriction Exist?

The separation is not a limitation — it is a deliberate engineering trade-off:

- **Simpler decode logic**: Every instruction's operands are always registers (except load/store), making the decode stage uniform and fast.
- **Better pipelining**: Arithmetic instructions have predictable, single-cycle latency. Memory accesses have variable latency and are isolated to a single instruction class.
- **Register pressure is visible**: The compiler must explicitly manage what is in a register vs in memory, encouraging efficient register allocation.
- **Hardware simplicity**: The ALU never needs a memory port. Memory access hardware is fully decoupled from arithmetic hardware.

## Comparison with CISC (Register-Memory)

| Feature | Load-Store (RISC-V) | Register-Memory (x86) |
|---|---|---|
| Memory access | Only LW/SW variants | Many instructions |
| Instruction count | More instructions | Fewer instructions |
| Code density | Lower | Higher |
| Pipeline simplicity | High | Complex |
| Compiler workload | Higher | Lower |

## Registers Are the Workspace

Because all computation happens in registers, a load-store ISA relies on having enough registers to hold active data. RISC-V provides 32 general-purpose integer registers (`x0`–`x31`), which is substantially more than the 8 general-purpose registers in 32-bit x86. This larger register file compensates for the inability to work directly with memory operands.

## The Worked Example: Incrementing a Counter

Suppose a counter is stored at memory address `0x1000`. In RISC-V:

```asm
li   x1, 0x1000    # load immediate: x1 = 0x1000 (pointer to counter)
lw   x2, 0(x1)     # load word: x2 = memory[0x1000]
addi x2, x2, 1     # increment: x2 = x2 + 1
sw   x2, 0(x1)     # store word: memory[0x1000] = x2
```

Four instructions. Explicit. Every step is visible to the hardware and the programmer.

## Common Pitfall

Beginners often try to treat an address in a register as "the value" without loading it first. If `x1` holds address `0x1000`, then `add x2, x1, x0` gives you `0x1000` — the address itself — not the value stored there.

> **Interview answer:** In a load-store architecture, only load and store instructions touch memory; all arithmetic and logic operate purely on registers. This simplifies pipelining and hardware design at the cost of slightly higher instruction count.
