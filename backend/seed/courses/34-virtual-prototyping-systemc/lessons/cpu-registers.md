# CPU Registers: General-Purpose and Special

Registers are the fastest storage inside a CPU — small arrays of flip-flops built directly into the processor die. Because they are on-chip and accessed in a single clock cycle, every ISA design maximizes register use to avoid slower memory accesses.

## General-Purpose Registers (GPRs)

GPRs hold the operands and results of arithmetic, logic, and data-movement instructions. The count is architecture-defined:

| Architecture | GPR count | Width |
|---|---|---|
| RISC-V RV32I | 32 (x0–x31) | 32 bits |
| ARM Cortex-A (AArch64) | 31 (x0–x30) + SP | 64 bits |
| x86-64 | 16 (rax–r15) | 64 bits |
| MIPS32 | 32 ($0–$31) | 32 bits |

More registers reduce spilling to memory (a major performance win), but cost silicon area and increase instruction-word bits needed to encode register indices.

### The Zero Register Convention

RISC-V `x0` is hardwired to zero — any write to it is silently discarded, any read returns 0. This eliminates the need for a dedicated `ZERO` opcode and simplifies ISA encoding.

```asm
; RISC-V: synthesize "move" using addi with zero register
addi x5, x0, 42    ; x5 = 0 + 42 = 42
add  x6, x5, x0    ; x6 = x5 + 0  (move x5 → x6)
```

## Special-Purpose Registers

These registers have a defined architectural role and are often read or written implicitly by certain instructions.

| Register | Name | Role |
|---|---|---|
| PC | Program Counter | Address of the next instruction to fetch |
| SP | Stack Pointer | Top of the current stack frame |
| LR / RA | Link / Return Address | Return address saved on CALL |
| SR / FLAGS | Status / Flag Register | Condition codes (Zero, Carry, Overflow, Negative) |
| CSRs | Control and Status Regs | Privileged configuration (RISC-V: mstatus, mtvec, …) |

### Program Counter (PC)

The PC advances by the instruction size (4 bytes for fixed-width 32-bit ISAs) after each fetch. Branch and jump instructions modify it directly.

```cpp
// SystemC CPU model — PC update
if (is_branch && branch_taken) {
    pc = branch_target;
} else {
    pc += 4;  // next sequential instruction
}
```

### Link Register

On a function call, the return address (PC + 4) is saved into the link register. The callee restores execution by jumping to that value.

```asm
; RISC-V call convention
jal  x1, my_function   ; x1 (ra) = PC+4; PC = my_function
; ... inside my_function:
jalr x0, x1, 0         ; PC = x1; (return)
```

## Register File in a CPU Model

In SystemC you model the register file as an array:

```cpp
// RISC-V 32-register file
uint32_t rf[32] = {};

// Read operand (x0 always returns 0)
auto read_reg = [&](uint32_t idx) -> uint32_t {
    return (idx == 0) ? 0u : rf[idx];
};

// Write result (ignore writes to x0)
auto write_reg = [&](uint32_t idx, uint32_t val) {
    if (idx != 0) rf[idx] = val;
};
```

## Common Pitfalls

- **Forgetting the zero-register rule** — writing to x0/r0 in simulation must be a no-op, or register-file reads will return wrong values.
- **Confusing caller-saved vs callee-saved registers** — the ABI defines which GPRs a function must preserve. A CPU model does not enforce this, but your test programs must respect it.
- **PC width mismatch** — on a 32-bit ISA the PC is 32 bits. Using a 64-bit variable in your model is fine, but make sure wrapping behavior on overflow matches the spec.

## Interview Answer

> "GPRs hold operands and results for ALU operations. Special registers like the PC, SP, and flags register serve architectural roles that are implicitly updated by specific instructions. In a RISC-V model the zero register (x0) is hardwired to zero — writes are discarded and reads always return 0 — simplifying ISA encoding significantly."
