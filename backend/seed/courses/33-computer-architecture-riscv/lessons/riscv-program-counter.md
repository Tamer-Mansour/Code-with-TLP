# The Program Counter in RISC-V

The **program counter (PC)** is a dedicated register that holds the address of the instruction currently being fetched. It is architecturally separate from the 32 general-purpose registers — you cannot reference it as x0–x31 in most instructions — yet it is tightly coupled to instruction flow and several RISC-V opcodes operate on it explicitly.

## PC Basics

At reset, the PC is initialised to a platform-defined address (commonly `0x00000000` or `0x80000000` for Linux systems). After each instruction is fetched, the hardware updates the PC:

- **Normal flow:** `PC = PC + 4` (all base instructions are 4 bytes wide in RV32I/RV64I).
- **Compressed extension (RVC):** `PC = PC + 2` for 16-bit instructions.
- **Branch/jump taken:** PC is set to the branch or jump target.

## PC-Relative Addressing

RISC-V uses **PC-relative** addressing for branches and jumps, not absolute addresses. This makes position-independent code (PIC) natural — the binary works at any load address without patching.

### Branch instructions (B-type)

```asm
beq  x1, x2, offset    # PC = PC + sign_extend(offset) if x1 == x2
```

The 12-bit immediate encodes a byte offset in multiples of 2, giving a ±4 KiB reach from the current instruction.

### JAL — Jump and Link

```asm
jal  x1, offset        # x1 = PC + 4; PC = PC + sign_extend(offset)
```

- Saves the **return address** (PC + 4) into `rd`.
- Jumps to `PC + offset` (±1 MiB range with a 20-bit immediate).
- Used for function calls.

### JALR — Jump and Link Register

```asm
jalr x1, x2, offset    # x1 = PC + 4; PC = (x2 + offset) & ~1
```

- Computes an absolute target from a base register plus immediate.
- The LSB of the result is forced to 0 (instruction alignment).
- Used for **indirect calls** and **returns** (`ret` = `jalr x0, x1, 0`).

### AUIPC — Add Upper Immediate to PC

```asm
auipc x5, 0x12345      # x5 = PC + (0x12345 << 12)
```

`AUIPC` is the workhorse for reaching any 32-bit address in a two-instruction sequence:

```asm
auipc x5, %hi(symbol)   # upper 20 bits relative to PC
addi  x5, x5, %lo(symbol) # lower 12 bits
```

This pattern is how the linker materialises arbitrary addresses in PIC code.

## The PC Is Not in the Register File

Unlike some architectures (ARM's r15, x86's RIP relative addressing), you cannot write `add x5, pc, x0` in RISC-V. The PC is not aliased to any xN register. The only way to read the PC into a register is with `auipc` or `jal` (which writes `PC + 4` to `rd`).

```asm
# Read current PC into t0 (common idiom)
auipc t0, 0       # t0 = PC of this instruction
```

## Alignment Requirements

In the base RV32I/RV64I ISA, all instructions must be **4-byte aligned**. Jumping to a misaligned address causes an instruction-address-misaligned exception. With the C (compressed) extension, 2-byte alignment is sufficient.

## Worked Example: Computing a Return Address

```asm
# Calling a function at label 'foo'
jal  ra, foo    # ra = PC + 4 (return address); PC = address of foo

# Inside foo, returning to caller:
jalr x0, ra, 0  # PC = ra; result discarded (write to x0)
# Assembler pseudo: ret
```

## Common Pitfalls

- **Assuming PC holds the current or next instruction.** In a pipelined CPU the PC may already point to a later instruction during execution of the current one. Architecturally, RISC-V defines PC as the address of the *current* instruction at the fetch stage.
- **Mixing up JAL and JALR ranges.** JAL has a 20-bit offset (±1 MiB); JALR has a 12-bit offset from a base register (any address reachable via base + ±2 KiB).
- **Forgetting the forced-zero LSB in JALR.** The hardware clears bit 0 of the computed target to enforce alignment.

> **Interview answer:** The RISC-V PC is a separate register holding the fetch address. It advances by 4 on each instruction and is updated by branches and jumps using PC-relative offsets. It cannot be accessed as a general-purpose register — `AUIPC` is the standard way to materialise a PC-relative address.
