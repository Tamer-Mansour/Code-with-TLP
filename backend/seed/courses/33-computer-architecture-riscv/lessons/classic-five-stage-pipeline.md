# The Classic Five-Stage RISC Pipeline

The five-stage pipeline is the canonical design taught in every computer architecture course and is the direct ancestor of pipelines in production RISC-V, MIPS, and ARM processors. Understanding it in detail makes every more advanced topic — hazards, superscalar, out-of-order — immediately accessible.

## The Five Stages

### 1. IF — Instruction Fetch

The processor reads the instruction at the address in the **Program Counter (PC)** from instruction memory (or the L1 instruction cache). After the fetch, the PC is incremented by 4 (for 32-bit instructions) to point to the next sequential instruction.

### 2. ID — Instruction Decode / Register File Read

The fetched instruction bits are decoded to identify:
- The opcode (what operation to perform)
- Source register numbers (rs1, rs2 in RISC-V)
- Destination register number (rd)
- Immediate values (sign-extended)

The register file is read in parallel with decoding, so source operand values are available at the end of this stage.

### 3. EX — Execute / ALU

The Arithmetic Logic Unit (ALU) performs the operation:
- For R-type instructions: arithmetic or logic on two register values
- For I-type (load/store): adds the base register and sign-extended immediate to compute an effective address
- For branches: computes the branch target and evaluates the condition

### 4. MEM — Memory Access

Only load and store instructions do real work here:
- **Load** (`lw`, `lb`, etc.): reads data memory at the address computed in EX
- **Store** (`sw`, `sb`, etc.): writes a register value to data memory

All other instructions pass through this stage without a memory operation — their result just propagates forward.

### 5. WB — Write-Back

The result — either from the ALU (for R-type and I-type arithmetic) or from memory (for loads) — is written back into the destination register in the register file.

## Stage Summary Table

| Stage | Abbreviation | Key hardware used |
|-------|-------------|-------------------|
| Instruction Fetch | IF | PC, Instruction Memory |
| Instruction Decode | ID | Decoder, Register File (read) |
| Execute | EX | ALU, branch comparator |
| Memory Access | MEM | Data Memory / Cache |
| Write-Back | WB | Register File (write) |

## Timing Diagram

```
Cycle:  1    2    3    4    5    6    7    8    9
I1:     IF   ID   EX   MEM  WB
I2:          IF   ID   EX   MEM  WB
I3:               IF   ID   EX   MEM  WB
I4:                    IF   ID   EX   MEM  WB
I5:                         IF   ID   EX   MEM  WB
```

After cycle 5, the pipeline is full. From cycle 5 onward, one instruction completes every cycle.

## RISC-V Instruction Encoding in the Pipeline

```asm
# RISC-V: add t0, t1, t2
# IF:  fetch 0x00628233 from PC
# ID:  decode — R-type ADD, rs1=t1(x6), rs2=t2(x7), rd=t0(x5)
# EX:  ALU computes x6 + x7
# MEM: no memory operation (pass-through)
# WB:  write result to x5 (t0)
```

## Why Five Stages?

RISC ISAs are designed so that every instruction fits cleanly into exactly these five categories of work. No instruction requires a memory read AND a complex ALU computation in the same cycle. This regularity is what makes a clean five-stage pipeline possible — and it is intentional in RISC design philosophy.

## Common Pitfall: Confusing MEM and WB for Loads

A load instruction (`lw t0, 0(t1)`) computes the address in EX, reads memory in MEM, and then writes the loaded value to `t0` in WB. This means the value is not available until the end of WB — **two cycles after the instruction enters EX**. This creates the classic load-use data hazard requiring a one-cycle stall.

```asm
lw   t0, 0(t1)   # t0 not ready until end of WB
add  t2, t0, t3  # needs t0 at start of EX — one cycle too early!
# Compiler inserts a NOP or reorders code to avoid the stall
```

> **Interview answer:** The classic five-stage RISC pipeline — IF, ID, EX, MEM, WB — overlaps five instructions simultaneously, using separate hardware for each stage. Instructions complete at one per cycle once the pipeline is full, but load instructions create a one-cycle use hazard because their result is not available until the WB stage.
