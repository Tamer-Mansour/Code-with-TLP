# Micro-Operations Behind Each Step

The five stages of the instruction cycle — Fetch, Decode, Execute, Memory Access, Write-Back — are useful abstractions, but each stage is itself composed of smaller atomic data transfers called **micro-operations** (micro-ops, or µops). Understanding micro-ops reveals what the hardware is *actually* doing at the register-transfer level and is essential for low-level performance analysis and processor design.

## What Is a Micro-Operation?

A micro-operation is a single, atomic data transfer or computation that can be performed by the hardware in one control step. It is expressed at the **Register Transfer Level (RTL)**:

```
destination ← source_or_operation
```

Examples:
- `IR ← MEM[PC]` — copy memory content at address PC into the Instruction Register
- `A ← R[rs1]` — copy register file entry rs1 into internal register A
- `ALUout ← A + B` — compute A + B and place result in ALUout
- `R[rd] ← ALUout` — write ALUout into the destination register

A "stage" in the pipeline corresponds to one clock cycle's worth of micro-ops executed in parallel.

## Micro-Ops for Each Stage (Multi-Cycle Model)

Using RISC-V as the reference and a multi-cycle (FSM-controlled) implementation, the micro-ops for each stage are:

### Stage 1: Instruction Fetch

```
IR   ← MEM[PC]         ; fetch 32-bit instruction word
NPC  ← PC + 4          ; compute next sequential PC
```

These two micro-ops happen in parallel: the memory read and the adder operate simultaneously.

### Stage 2: Instruction Decode / Register Fetch

```
A    ← R[IR[19:15]]    ; read rs1 into temp register A
B    ← R[IR[24:20]]    ; read rs2 into temp register B
IMM  ← sign_extend(IR) ; reconstruct and sign-extend immediate
```

The register file is read using the fixed bit-position rs1 and rs2 fields. The immediate extractor also runs in parallel.

### Stage 3: Execute (ALU)

For R-type instructions:
```
ALUout ← A op B        ; op determined by funct3, funct7
```

For I-type (ADDI, LW address, etc.):
```
ALUout ← A + IMM       ; addition with sign-extended immediate
```

For branches:
```
cond   ← compare(A, B) ; e.g., A == B for BEQ
target ← PC + (IMM<<1) ; branch target address
```

For JAL:
```
ALUout ← PC + IMM      ; jump target
link   ← NPC           ; return address = PC + 4
```

### Stage 4: Memory Access

For loads:
```
MDR ← MEM[ALUout]      ; read data memory at effective address
```

For stores:
```
MEM[ALUout] ← B        ; write rs2 value to memory
```

For non-memory instructions:
```
(no micro-ops; stage is a pass-through)
```

MDR stands for **Memory Data Register** — the staging register between memory and write-back.

### Stage 5: Write-Back

For ALU instructions:
```
R[IR[11:7]] ← ALUout   ; write ALU result to rd
PC          ← NPC      ; commit the new PC
```

For loads:
```
R[IR[11:7]] ← MDR      ; write loaded data to rd
PC          ← NPC
```

For branches (taken):
```
PC ← target            ; redirect to branch target
```

## Micro-Ops in Modern Out-of-Order Processors

Modern x86 processors (Intel Core, AMD Zen) translate complex x86 instructions into simpler internal micro-ops before execution. A single x86 `PUSH` instruction expands into two micro-ops:

```
RSP ← RSP - 8          ; decrement stack pointer
MEM[RSP] ← src         ; store register value
```

This translation happens in the frontend decoder and allows the **out-of-order execution engine** to schedule individual micro-ops independently. RISC-V's simpler ISA means most RISC-V instructions map one-to-one to a single micro-op, which simplifies frontend design.

## Worked Example: Micro-Ops for `LW x5, 8(x1)` Across All 5 Stages

```
Stage 1 (Fetch):
  IR  ← MEM[PC]              ; e.g., IR = 0x00808283
  NPC ← PC + 4

Stage 2 (Decode):
  A   ← R[1]                 ; read x1 (rs1 = bits [19:15] = 00001)
  IMM ← sign_extend(8)       ; immediate = 0x00000008

Stage 3 (Execute):
  ALUout ← A + IMM           ; effective address = x1 + 8

Stage 4 (Memory):
  MDR ← MEM[ALUout]          ; load word from computed address

Stage 5 (Write-Back):
  R[5] ← MDR                 ; x5 ← loaded value
  PC   ← NPC                 ; advance to next instruction
```

## Control Signals as Micro-Op Selectors

Every micro-op is gated by a **control signal**. The processor's control unit (a ROM lookup table or hardwired FSM) asserts exactly the right signals each cycle:

| Control Signal | Enables Micro-Op |
|---|---|
| `IRWrite` | `IR ← MEM[PC]` |
| `RegRead` | `A ← R[rs1]`, `B ← R[rs2]` |
| `ALUOp` | `ALUout ← A op B` |
| `MemRead` | `MDR ← MEM[ALUout]` |
| `MemWrite` | `MEM[ALUout] ← B` |
| `RegWrite` | `R[rd] ← ALUout` or `R[rd] ← MDR` |
| `PCWrite` | `PC ← NPC` or `PC ← target` |

## Common Pitfalls

- **Confusing internal registers (A, B, MDR, ALUout) with architectural registers.** Temp registers like A and ALUout are invisible to the programmer — they hold intermediate values between stages.
- **Thinking micro-ops are microcode.** Micro-ops at the RTL level are a design abstraction. Microcode (used in CISC CPUs like early x86) is a stored program in a ROM that sequences micro-ops for complex instructions — a different (higher-level) concept.
- **Assuming all micro-ops take the same time.** A memory micro-op (`MDR ← MEM[...]`) takes far longer than a register-file read if it misses the cache.

> **Interview answer:** Micro-operations are the atomic register-transfer-level steps within each pipeline stage — things like "copy register rs1 into temp register A" or "write ALU output to memory." They are the lowest level of instruction execution visible to the hardware's control unit, and understanding them explains exactly what the processor is doing on every clock edge.
