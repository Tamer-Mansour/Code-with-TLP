# The Stored-Program Concept Explained

Before 1945, computers were *programmed by wiring* — you rewired plug boards, set switches, or physically reconnected components to change what the machine computed. The stored-program concept changed everything: it moved the program itself into memory, treating instructions as data.

## The Core Idea

A stored-program computer obeys one simple rule:

> **Instructions are data stored in the same memory as the values they operate on. The CPU fetches each instruction from memory, decodes it, and executes it — then advances the program counter to the next instruction.**

This means a program is nothing more than a sequence of numbers in memory. The CPU does not know in advance what the program will do; it discovers each step at runtime by reading from memory.

## Why It Is Revolutionary

Before stored programs, changing a computation meant changing the hardware. With stored programs:

1. **Programs can be loaded from disk** — an operator types the program into memory, or reads it from tape/disk, without touching any wires.
2. **Programs can be modified at runtime** — a program can write new instruction words into memory and then jump to them (self-modifying code, JIT compilers).
3. **Programs can be treated as data** — an operating system loads one program, saves its state, loads another. Compilers write programs as their output. Interpreters read programs as their input.
4. **Conditional branching becomes natural** — the program counter (PC) is just another register; the program can write a new address into it based on a computed result.

## The Fetch–Decode–Execute Cycle

Every stored-program CPU repeats this loop indefinitely:

```
while (true):
    instruction = Memory[PC]   // FETCH
    PC = PC + instruction_size // advance program counter
    decoded = decode(instruction) // DECODE
    execute(decoded)              // EXECUTE (may update PC for branches)
```

In assembly this looks like:

```asm
# RISC-V example: simple loop counting down from 5
    li   t0, 5          # load immediate: t0 = 5
loop:
    addi t0, t0, -1     # t0 = t0 - 1
    bnez t0, loop       # branch if t0 != 0 (writes new PC)
    # PC advances sequentially unless branch is taken
```

The `bnez` instruction is just a number in memory. The CPU reads it, decodes "branch if not equal to zero", evaluates the condition, and either writes a new address into PC or does nothing.

## Instructions Are Numbers

In RISC-V, every base instruction is a 32-bit integer. The instruction `addi t0, t0, -1` encodes as:

```
 31      20  19  15  14  12  11   7  6      0
+----------+-------+------+--------+---------+
| imm[11:0]|  rs1  | funct3|  rd   | opcode  |
| 111111111111| 00101|  000  | 00101 | 0010011 |
+----------+-------+------+--------+---------+
```

That 32-bit word lives in memory. The CPU reads it, interprets the bit fields, and performs an addition. Nothing prevents a program from writing a *different* 32-bit value into that memory location, changing the instruction — though modern operating systems mark code pages as read-only to prevent accidental self-modification.

## Historical Milestones

| Year | Machine | Significance |
|---|---|---|
| 1945 | EDVAC design | First written description of stored-program concept (von Neumann report) |
| 1948 | Manchester Baby | First machine to run a stored program in electronic memory |
| 1949 | EDSAC | First practical stored-program computer in regular use |
| 1951 | UNIVAC I | First commercial stored-program computer |

## Common Pitfall

Students sometimes confuse "stored program" with "having a hard drive". The key is that the *CPU fetches instructions from the same addressable memory it uses for data* — not where the program was loaded from originally.

> **Interview answer:** "The stored-program concept means that a program is stored as data in memory, and the CPU fetches each instruction sequentially via the program counter. This allows programs to be loaded, modified, and even written by other programs — making compilers, operating systems, and JIT engines possible. Every modern computer, from microcontrollers to servers, is a stored-program machine."
