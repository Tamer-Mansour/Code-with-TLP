# The Program Counter: Tracking the Next Instruction

The **Program Counter (PC)** is the register that holds the memory address of the instruction the CPU is about to fetch. It is the CPU's "bookmark" — without it, the processor would have no idea where in memory the program currently is.

## How the PC Moves

Under normal (sequential) execution, the PC advances by the size of one instruction after each fetch:

- **RISC-V (RV32I/RV64I):** PC ← PC + 4 (all base instructions are 4 bytes)
- **RISC-V with C extension:** instructions may be 2 bytes; PC increments by 2 or 4 depending on instruction size
- **x86:** variable-length instructions; PC advances by 1–15 bytes

The PC increment happens in dedicated adder hardware — it does not consume the ALU — so the addition is effectively free.

## PC Modifications: Branches and Jumps

Three events change the PC to something other than PC+4:

| Event | How PC Changes | RISC-V Instructions |
|---|---|---|
| Unconditional jump | PC ← target address | `jal`, `jalr` |
| Conditional branch (taken) | PC ← PC + sign_extend(offset)×2 | `beq`, `bne`, `blt`, `bge`, etc. |
| Conditional branch (not taken) | PC ← PC + 4 (normal) | (same instructions) |
| Exception / interrupt | PC ← mtvec (trap vector) | (hardware) |
| Return from trap | PC ← mepc | `mret` |

## PC in the Datapath

```
        ┌──────────────────────────────────────┐
        │                                      │
  ┌─────▼─────┐        ┌──────────┐           │
  │  PC Reg   │──────► │  Instr.  │           │
  └─────┬─────┘        │  Memory  │           │
        │              └──────────┘           │
        │                                      │
        ▼                                      │
  ┌───────────┐   PC+4 ◄─────── [+4 Adder]    │
  │ Branch    │                                │
  │ Target    │   PC+offset ◄── [Branch Adder] │
  │ Mux       │                                │
  └─────┬─────┘                                │
        │  selected next PC                    │
        └──────────────────────────────────────┘
```

A **2-to-1 mux** (or wider, if indirect jumps are included) selects the next PC value and feeds it back into the PC register on the next rising clock edge.

## Worked Example: A Simple Loop

```asm
# RISC-V: sum integers 0..9
#   a0 = sum, t0 = counter

    li    a0, 0          # PC = 0x0000
    li    t0, 0          # PC = 0x0004
loop:
    add   a0, a0, t0     # PC = 0x0008
    addi  t0, t0, 1      # PC = 0x000C
    li    t1, 10         # PC = 0x0010
    blt   t0, t1, loop   # PC = 0x0014  → if taken, PC = 0x0008
    # fall through        # PC = 0x0018
```

Each `blt` iteration: if t0 < 10, the branch is taken and PC jumps back to `0x0008`. The offset encoded in `blt` is `0x0008 − 0x0014 = −12` (sign-extended, multiplied by 1 since B-type offset encodes half-words, so the actual immediate in the instruction is `−6` in units of 2 bytes, i.e., `−12` bytes).

## PC Alignment Requirements

RISC-V base instructions must be **4-byte aligned** (address divisible by 4). Jumping to a misaligned address raises an **Instruction Address Misaligned** exception. The C (compressed) extension relaxes this to 2-byte alignment.

This is a common source of bugs when manually computing branch targets in assembly.

## The PC as a Base Address: AUIPC

`auipc rd, imm` places `PC + (imm << 12)` into `rd`. This lets position-independent code compute addresses relative to the current instruction:

```asm
auipc a0, 0        # a0 = PC of this instruction
```

Used heavily in position-independent executables (PIE) and shared libraries where absolute addresses are unknown at link time.

## Common Pitfalls

- **Off-by-one in branch targets.** RISC-V B-type immediates are in units of 2 bytes, so an offset of 1 means 2 bytes, not 1. Assemblers handle this automatically, but manual encoding trips people up.
- **Forgetting PC advances before the branch check.** In pipelined CPUs the PC may already point to the *next* instruction by the time the branch outcome is known — this creates branch hazards.
- **Writing to PC via a GPR.** In RISC-V you cannot do `mv pc, t0`. Use `jalr x0, t0, 0` instead (jump to address in t0, discard link).

## Interview Answer

> "The Program Counter is a special register that holds the address of the next instruction to fetch; it increments by the instruction size each cycle and is overwritten by branch/jump instructions or hardware events like interrupts to redirect program flow."
