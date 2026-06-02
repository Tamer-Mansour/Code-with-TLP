# Interview Review: RISC-V Deep Dive

RISC-V is increasingly the ISA of choice in interview questions at RISC-V Foundation member companies, semiconductor start-ups, and academic institutions. This lesson is a structured deep dive into the RISC-V-specific questions you are most likely to face.

## 1. What Makes RISC-V Different?

RISC-V is an **open, modular ISA** — not a product, but a specification anyone can implement royalty-free. Key characteristics:

- **Base ISAs**: RV32I (32-bit, 40 instructions), RV64I (64-bit), RV32E (embedded, 16 registers).
- **Standard extensions**: M (multiply/divide), A (atomic), F/D (float/double), C (compressed 16-bit), V (vector), Zicsr (CSR instructions).
- **Custom extensions**: an implementer may add non-standard instructions in opcode space reserved for that purpose.
- **No mandatory privileged mode**: the spec separates machine mode (M), supervisor mode (S), and user mode (U) into separate privilege specs.

> **Interview answer:** "RISC-V is a free, open, modular ISA. The base integer instruction set is small and fixed; features are added via standard extensions (M, A, F, D, C, V) or vendor-defined custom extensions, making it suitable for everything from tiny microcontrollers to application processors."

## 2. Register File

RV32I has 32 general-purpose integer registers, x0–x31. Calling convention (ABI) names:

| Registers | ABI names | Role |
|---|---|---|
| x0 | zero | Hardwired zero |
| x1 | ra | Return address |
| x2 | sp | Stack pointer |
| x3 | gp | Global pointer |
| x4 | tp | Thread pointer |
| x5–x7 | t0–t2 | Temporaries |
| x8–x9 | s0–s1 | Saved (s0 also frame pointer) |
| x10–x17 | a0–a7 | Function arguments / return values |
| x18–x27 | s2–s11 | Saved registers |
| x28–x31 | t3–t6 | Temporaries |

> **Interview answer:** "x0 is hardwired to zero. Function arguments go in a0–a7 (x10–x17); return values in a0–a1. Callee-saved registers are s0–s11; caller-saved are temporaries t0–t6."

## 3. Instruction Formats

Six formats, all 32 bits, with opcode always in bits [6:0]:

```
R:  funct7[31:25] | rs2[24:20] | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
I:  imm[31:20]                 | rs1[19:15] | funct3[14:12] | rd[11:7] | opcode[6:0]
S:  imm[31:25]   | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm[11:7] | opcode[6:0]
B:  imm[31:25]   | rs2[24:20] | rs1[19:15] | funct3[14:12] | imm[11:7] | opcode[6:0]
U:  imm[31:12]                                              | rd[11:7]  | opcode[6:0]
J:  imm[31:12]  (scrambled)                                 | rd[11:7]  | opcode[6:0]
```

The immediate bits are scattered across B and J formats to keep rd and rs1 at fixed positions — this reduces decode hardware.

## 4. Load-Store Architecture

RISC-V is a load/store architecture: arithmetic operates only on registers; memory is accessed only via load (`LW`, `LH`, `LB`, `LHU`, `LBU`) and store (`SW`, `SH`, `SB`) instructions. No memory-to-memory operations.

```asm
lw   a0, 0(a1)       # Load word from address a1+0 into a0
addi a0, a0, 1       # Increment
sw   a0, 0(a1)       # Store result back
```

> **Interview answer:** "RISC-V is load/store: the only instructions that access memory are loads and stores. All arithmetic operates on registers. This simplifies the pipeline and enables forwarding because the ALU inputs are always registers."

## 5. Compressed Instructions (C Extension)

The C extension adds 16-bit encodings for common operations, reducing code size by ~25-30%. Common examples:

| 16-bit instruction | 32-bit equivalent |
|---|---|
| `c.li a0, 5` | `addi a0, x0, 5` |
| `c.mv a1, a2` | `add a1, x0, a2` |
| `c.lw a0, 0(a1)` | `lw a0, 0(a1)` |
| `c.j label` | `jal x0, label` |

The C extension restricts compressed register operands to x8–x15 (CIW/CS formats).

## 6. Privileged Architecture: CSRs and Trap Model

**CSRs** (Control and Status Registers) are accessed by `CSRRW`, `CSRRS`, `CSRRC` and their immediate variants. Key CSRs:

| CSR | Purpose |
|---|---|
| `mstatus` | Global interrupt enable, privilege modes |
| `mtvec` | Trap vector base address |
| `mepc` | Exception Program Counter (address to return to) |
| `mcause` | Cause of the most recent trap (exception code + interrupt bit) |
| `mie` / `mip` | Interrupt enable / interrupt pending |
| `mscratch` | Scratch register for M-mode trap handler |

Trap entry sequence: hardware saves PC to `mepc`, sets `mcause`, sets privilege to M-mode, jumps to `mtvec`.

> **Interview answer:** "On a trap, the hardware atomically saves the return address in `mepc`, records the cause in `mcause`, and jumps to the handler at `mtvec`. The handler uses `mret` to restore privilege and return to `mepc`."

## 7. Atomics (A Extension)

RISC-V atomics use **Load-Reserved / Store-Conditional (LR/SC)** and **Atomic Memory Operations (AMO)**:

```asm
# Spin-lock acquire using LR/SC
retry:
    lr.w  t0, (a0)       # Load-reserved from address a0
    bnez  t0, retry      # Spin if lock is held
    li    t1, 1
    sc.w  t1, t1, (a0)   # Store-conditional; t1=0 on success
    bnez  t1, retry      # Retry if SC failed (reservation lost)
```

`AMOADD.W`, `AMOSWAP.W`, `AMOAND.W`, `AMOOR.W` perform read-modify-write atomically without LR/SC overhead for simple operations.

## 8. Memory Ordering: FENCE

RISC-V has a relaxed memory model (RVWMO). Use `FENCE` to enforce ordering:

```asm
fence rw, rw    # Full barrier: all prior reads/writes complete before all subsequent ones
fence.i         # Instruction fence: ensure instruction cache is consistent with data cache
```

## 9. Common Interview Gotchas

- **No flags register** — RISC-V has no condition codes. Branches compare two registers directly (`BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU`).
- **No dedicated call/return instructions** — `JAL ra, target` is the call; `JALR x0, ra, 0` (aliased as `RET`) is the return.
- **AUIPC** builds PC-relative addresses — essential for position-independent code: `AUIPC rd, imm` loads `PC + (imm << 12)` into rd.
- **Endianness** — RISC-V is **little-endian** by default (big-endian is an optional non-ratified extension).

## 10. Quick Encoding Examples

```asm
# addi x10, x0, 42
# I-type: imm=42=0x02A, rs1=0, funct3=0, rd=10, opcode=0x13
# 0000 0010 1010 | 00000 | 000 | 01010 | 001 0011
# = 0x02A00513

# add x12, x10, x11
# R-type: funct7=0, rs2=11, rs1=10, funct3=0, rd=12, opcode=0x33
# 0000000 | 01011 | 01010 | 000 | 01100 | 011 0011
# = 0x00B50633
```
