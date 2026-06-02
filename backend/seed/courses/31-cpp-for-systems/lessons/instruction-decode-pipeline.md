# Fetch, Decode, Execute: A Simple Interpreter Loop

Every instruction-set simulator at its heart is a `while(running)` loop with three stages: **fetch** an instruction word from memory, **decode** it into an operation and operands, and **execute** the operation, updating state. This lesson builds a minimal but correct loop for a subset of RISC-V.

## The Interpreter Loop Skeleton

```cpp
void CPU::run() {
    while (!halted_) {
        uint32_t instr = mem_.load32(pc_);   // 1. Fetch
        pc_ += 4;                             //    advance PC before execute
        decode_and_execute(instr);            // 2+3. Decode & Execute
    }
}
```

Advancing `pc_` **before** execute simplifies JAL/JALR: the "return address" saved to `rd` is already `old_pc + 4`, which is now just the current `pc_`.

## The Decode Switch

The most readable approach is a two-level switch: outer on `opcode`, inner on `funct3` (and sometimes `funct7`):

```cpp
void CPU::decode_and_execute(uint32_t instr) {
    uint32_t opcode = instr & 0x7F;
    uint32_t rd     = (instr >>  7) & 0x1F;
    uint32_t funct3 = (instr >> 12) & 0x07;
    uint32_t rs1    = (instr >> 15) & 0x1F;
    uint32_t rs2    = (instr >> 20) & 0x1F;
    uint32_t funct7 = (instr >> 25) & 0x7F;

    switch (opcode) {
    case 0x33:   // R-type ALU
        exec_r(rd, funct3, rs1, rs2, funct7);
        break;
    case 0x13:   // I-type ALU immediate
        exec_i_alu(rd, funct3, rs1, imm_i(instr));
        break;
    case 0x03:   // Loads
        exec_load(rd, funct3, rs1, imm_i(instr));
        break;
    case 0x23:   // Stores
        exec_store(funct3, rs1, rs2, imm_s(instr));
        break;
    case 0x63:   // Branches
        exec_branch(funct3, rs1, rs2, imm_b(instr));
        break;
    default:
        throw std::runtime_error("illegal instruction");
    }
}
```

## Executing R-Type Instructions

```cpp
void CPU::exec_r(int rd, int fn3, int rs1, int rs2, int fn7) {
    uint32_t a = rf_.read(rs1);
    uint32_t b = rf_.read(rs2);
    uint32_t result = 0;

    switch (fn3) {
    case 0x0: result = (fn7 == 0x20) ? (a - b) : (a + b); break; // SUB / ADD
    case 0x4: result = a ^ b;   break;  // XOR
    case 0x6: result = a | b;   break;  // OR
    case 0x7: result = a & b;   break;  // AND
    case 0x1: result = a << (b & 0x1F); break;  // SLL
    case 0x5: result = (fn7 == 0x20)
                ? static_cast<uint32_t>(static_cast<int32_t>(a) >> (b & 0x1F))
                : (a >> (b & 0x1F));            // SRA / SRL
              break;
    case 0x2: result = (static_cast<int32_t>(a) < static_cast<int32_t>(b)) ? 1 : 0; break; // SLT
    case 0x3: result = (a < b) ? 1 : 0; break;  // SLTU
    }
    rf_.write(rd, result);
}
```

Note the cast to `int32_t` for SRA and SLT — missing this collapses signed and unsigned comparisons into the same wrong answer.

## Executing a Load (LW)

```cpp
void CPU::exec_load(int rd, int fn3, int rs1, int32_t imm) {
    uint32_t addr = rf_.read(rs1) + static_cast<uint32_t>(imm);
    uint32_t val  = 0;
    switch (fn3) {
    case 0x2: val = bus_.read32(addr); break;              // LW
    case 0x0: val = static_cast<int32_t>(
                    static_cast<int8_t>(bus_.read8(addr))); break;  // LB sign-extend
    case 0x4: val = bus_.read8(addr);  break;              // LBU zero-extend
    // LH, LHU similar…
    }
    rf_.write(rd, val);
}
```

## Branch Execution

```cpp
void CPU::exec_branch(int fn3, int rs1, int rs2, int32_t imm) {
    uint32_t a = rf_.read(rs1);
    uint32_t b = rf_.read(rs2);
    bool taken = false;
    switch (fn3) {
    case 0x0: taken = (a == b);                                              break; // BEQ
    case 0x1: taken = (a != b);                                              break; // BNE
    case 0x4: taken = (static_cast<int32_t>(a) < static_cast<int32_t>(b));  break; // BLT
    case 0x5: taken = (static_cast<int32_t>(a) >= static_cast<int32_t>(b)); break; // BGE
    case 0x6: taken = (a < b);                                               break; // BLTU
    case 0x7: taken = (a >= b);                                              break; // BGEU
    }
    if (taken) pc_ = (pc_ - 4) + static_cast<uint32_t>(imm); // pc_ was already +4'd
}
```

The `pc_ - 4` corrects for the pre-increment done in the fetch stage.

## Common Pitfalls

- **Not sign-extending immediates** — the most frequent ISS bug.
- **Forgetting the pre-increment correction in branches** — results in jumps landing 4 bytes too late.
- **Writing to x0** — always guard the register write with `if (rd != 0)`.
- **Missing the shift-amount mask** — RISC-V only uses bits [4:0] of the shift operand; a shift of `0xFFFF` should shift by 31, not undefined behavior.

## Interview Answer

> **Interview answer:** "The interpreter loop fetches a 32-bit word from the PC, increments PC by 4, then dispatches on the opcode using a switch. Each handler extracts fields with shifts and masks, applies sign extension to immediates, updates the register file or memory, and — for branches — rewrites PC. The key correctness rules are: guard x0 writes, always sign-extend, and mask shift amounts to 5 bits."
