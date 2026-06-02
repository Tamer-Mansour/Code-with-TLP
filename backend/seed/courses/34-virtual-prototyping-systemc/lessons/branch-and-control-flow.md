# Branches and Control Flow

Sequential execution — fetching one instruction after another — cannot by itself express loops, conditionals, or function calls. **Branch instructions** alter the program counter to redirect execution, making them the backbone of all control flow.

## Types of Control-Flow Instructions

| Category | What it does | PC update |
|---|---|---|
| Unconditional branch / jump | Always redirects PC | `PC = target` |
| Conditional branch | Redirects only if a condition holds | `PC = (cond) ? target : PC+4` |
| Call (JAL/BL) | Redirects PC, saves return address | `RA = PC+4; PC = target` |
| Return (JALR/RET) | Jumps to saved return address | `PC = RA` |
| Indirect jump | Jumps to address in a register | `PC = reg + offset` |

## Branch Targets: PC-Relative Addressing

Most ISAs encode branch targets as a **signed offset from the current PC**. This makes code position-independent — the binary does not need patching when loaded at a different base address.

```asm
; RISC-V conditional branch (B-type format)
; beq rs1, rs2, offset  →  if (rs1 == rs2) PC += sign_extend(offset)
beq x5, x6, loop_top    ; branch back if x5 == x6
```

The offset is encoded in bits scattered across the B-type instruction word (a quirk that simplifies RISC-V hardware mux routing):

```
 31  30    25  24  20  19  15  14  12  11   8   7   6    0
 [imm12][imm10:5][rs2 ][rs1 ][fn3][imm4:1][imm11][opcode]
```

Assembling the immediate:

```cpp
int32_t branch_offset(uint32_t instr) {
    uint32_t imm12  = (instr >> 31) & 1;
    uint32_t imm11  = (instr >>  7) & 1;
    uint32_t imm10_5 = (instr >> 25) & 0x3F;
    uint32_t imm4_1  = (instr >>  8) & 0xF;
    uint32_t raw = (imm12 << 12) | (imm11 << 11) | (imm10_5 << 5) | (imm4_1 << 1);
    return (int32_t)(raw << 19) >> 19;  // sign-extend from bit 12
}
```

## Condition Codes vs Compare-and-Branch

Two philosophies exist in ISA design:

**Condition code model (x86, ARM A32):**
- ALU instructions set implicit flags (Zero, Negative, Carry, Overflow) in the status register.
- Branch instructions test those flags: `JE`, `JNE`, `JLT`, etc.

**Compare-and-branch model (RISC-V, MIPS):**
- A dedicated compare instruction or the branch instruction itself compares two registers.
- No implicit side-effects on other instructions.

```asm
; RISC-V: compare two registers inside the branch
blt x5, x6, label    ; branch if x5 < x6 (signed)
bltu x5, x6, label   ; branch if x5 < x6 (unsigned)
```

## Modeling Branches in SystemC

```cpp
case OPCODE_BRANCH: {
    uint32_t rs1_val = read_reg(rs1);
    uint32_t rs2_val = read_reg(rs2);
    bool taken = false;

    switch (funct3) {
        case 0b000: taken = (rs1_val == rs2_val);                   break; // BEQ
        case 0b001: taken = (rs1_val != rs2_val);                   break; // BNE
        case 0b100: taken = ((int32_t)rs1_val <  (int32_t)rs2_val); break; // BLT
        case 0b101: taken = ((int32_t)rs1_val >= (int32_t)rs2_val); break; // BGE
        case 0b110: taken = (rs1_val <  rs2_val);                   break; // BLTU
        case 0b111: taken = (rs1_val >= rs2_val);                   break; // BGEU
    }
    pc = taken ? (pc + branch_offset(instr)) : (pc + 4);
    break;
}
```

## Branch Prediction and Its Implications

Real processors predict the next PC before the branch is decoded, and flush incorrectly fetched instructions on a misprediction. In a SystemC model:

- A **functional model** (no timing) simply resolves the branch and sets the correct PC.
- A **timed model** must model the branch penalty (typically 1-3 cycles on an in-order pipeline, potentially many more out-of-order).

## Common Pitfalls

- **Unsigned vs signed comparison** — using `<` on `uint32_t` always does unsigned comparison. Cast to `int32_t` for signed branches (BLT, BGE).
- **Branch offset multiplied by 2** — RISC-V branch offsets are in units of bytes but the LSB is always 0 (instructions are 2-byte aligned). The encoded field omits the LSB, so you must shift left by 1 when reconstructing the offset.
- **Forgetting PC+4 on not-taken paths** — every not-taken branch still advances PC by one instruction.

## Interview Answer

> "Branch instructions modify the PC to redirect control flow. RISC-V uses compare-and-branch semantics — the comparison is embedded in the branch instruction itself, avoiding implicit flag side-effects. Branch targets are PC-relative offsets, making code position-independent. In a pipeline model, a branch introduces a hazard because the correct next PC is not known until the branch is resolved."
