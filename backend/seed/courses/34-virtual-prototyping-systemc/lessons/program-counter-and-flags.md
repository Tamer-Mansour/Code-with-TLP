# Program Counter and Status Flags

Two special registers dominate CPU control flow behavior: the **Program Counter (PC)** that tracks the instruction stream, and the **Status Flags register** that records the outcome of the last operation. Together they form the decision-making backbone of any processor.

## The Program Counter

The PC (also called the Instruction Pointer, IP, on x86) holds the **byte address of the next instruction to fetch**. It is updated at the end of every fetch cycle:

- **Sequential flow**: `PC ← PC + instruction_size` (4 for 32-bit RISC, variable for x86)
- **Taken branch or jump**: `PC ← branch_target`
- **Exception / interrupt**: `PC ← exception_vector` (the old PC is saved to a special register)

### PC Alignment

Fixed-width ISAs enforce PC alignment. In RV32I all instructions are 4-byte aligned; attempting to fetch from an odd or 2-byte-aligned address raises an **Instruction Address Misaligned** exception.

```cpp
// SystemC: alignment check before fetch
if (pc & 0x3) {
    raise_exception(EXC_INSTR_MISALIGNED, pc);
    return;
}
uint32_t instr = mem_read_word(pc);
```

### Compressed Instructions (16-bit)

RISC-V "C" extension allows 16-bit (2-byte aligned) instructions. The decoder peeks at the lowest two bits of the instruction word; if `instr[1:0] != 11` the instruction is 16 bits and PC advances by 2.

## Status Flags (Condition Codes)

Architectures that use implicit flags (x86, ARM A32/A64) update a flags register after ALU operations:

| Flag | Abbreviation | Set when... |
|---|---|---|
| Zero | Z | Result is exactly zero |
| Negative | N | Result's MSB is 1 (two's complement negative) |
| Carry | C | Unsigned overflow / borrow |
| Overflow | V | Signed overflow (magnitude too large for destination) |

### Flag Examples (32-bit subtraction: `a - b`)

```
a = 0x00000001, b = 0x00000002  →  result = 0xFFFFFFFF
Z=0  (not zero)
N=1  (MSB set)
C=1  (borrow occurred — unsigned underflow)
V=0  (signed: 1 - 2 = -1, fits in int32_t, no overflow)
```

```
a = 0x7FFFFFFF, b = 0xFFFFFFFF  →  result = 0x80000000
Z=0
N=1
C=0  (no unsigned borrow: 0x7FFFFFFF >= 0xFFFFFFFF is false, borrow occurs — C=1 on some conventions)
V=1  (signed overflow: 2147483647 - (-1) = 2147483648, does not fit in int32_t)
```

Note: carry convention for subtraction varies — ARM clears C on borrow, x86 sets CF on borrow. Always check the ISA manual.

## Flags in RISC-V vs x86

RISC-V **has no implicit flags register** in the base ISA. Comparison is done explicitly:

```asm
; x86: cmp sets flags, then je tests them
cmp eax, ebx
je  equal

; RISC-V: comparison is part of the branch instruction
beq x10, x11, equal
```

For carry detection in RISC-V software must use explicit sequences:

```asm
; Detect unsigned addition overflow (carry out) in RISC-V
add  x5, x3, x4         ; x5 = x3 + x4
bltu x5, x3, overflow   ; if x5 < x3 (unsigned), carry occurred
```

## Modeling PC and Flags in SystemC

```cpp
struct CpuState {
    uint32_t pc   = RESET_VECTOR;
    uint32_t rf[32] = {};  // register file
    // Flags — only needed for x86/ARM models
    bool flag_z = false;
    bool flag_n = false;
    bool flag_c = false;
    bool flag_v = false;
};

void update_flags(CpuState& s, uint64_t result, uint32_t a, uint32_t b) {
    s.flag_z = (result & 0xFFFFFFFF) == 0;
    s.flag_n = (result >> 31) & 1;
    s.flag_c = result > 0xFFFFFFFF;          // unsigned carry
    // Overflow: both inputs same sign, result different sign
    s.flag_v = (~(a ^ b) & (a ^ (uint32_t)result)) >> 31;
}
```

## Common Pitfalls

- **Carry vs borrow semantics** — ARM inverts the carry flag for subtraction (borrow = NOT carry). Copying x86 flag logic to an ARM model is wrong.
- **PC value at branch time** — in many ISAs the PC visible inside a branch instruction already points to PC+4 (the next instruction). Confirm for your target ISA.
- **Flag persistence** — in flag-based architectures flags survive across non-ALU instructions (moves, loads). Only ALU instructions update them. Missing this causes spurious branch misfires.

## Interview Answer

> "The PC holds the address of the next instruction to fetch and is updated by each fetch or by branch/exception logic. Status flags record arithmetic outcomes — zero, negative, carry, and overflow — and are tested by conditional branches. RISC-V avoids implicit flags entirely; comparisons are embedded in branch instructions, eliminating flag-lifetime hazards in the pipeline."
