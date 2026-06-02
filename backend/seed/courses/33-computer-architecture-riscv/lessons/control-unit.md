# The Control Unit: Orchestrating the CPU

The **control unit (CU)** is the part of the CPU that generates all the control signals that tell the datapath what to do with data. If the datapath is the muscles and bones of the CPU, the control unit is the nervous system — it reads the instruction and fires signals to every datapath component in the right sequence.

## What the Control Unit Does NOT Do

A common misconception is that the control unit processes data. It does not. The control unit:

- Reads the **opcode** (and sometimes funct3/funct7) from the instruction register.
- Produces **control signals** (1-bit or few-bit values) that configure muxes, enable register writes, select ALU operations, and control memory read/write.

Data itself — integers, addresses, floats — flows only through the datapath.

## Control Signals in a RISC-V Single-Cycle Datapath

| Signal | Width | Function |
|---|---|---|
| `RegWrite` | 1 bit | Enable write to destination register |
| `ALUSrc` | 1 bit | ALU input B: 0 = RS2, 1 = sign-extended immediate |
| `ALUOp` | 2 bits | Hint to ALU control: 00=add, 01=sub, 10=use funct |
| `MemRead` | 1 bit | Trigger a data memory read (load) |
| `MemWrite` | 1 bit | Trigger a data memory write (store) |
| `MemToReg` | 1 bit | Register write data: 0 = ALU result, 1 = MDR |
| `Branch` | 1 bit | Enable branch mux if ALU zero flag is set |
| `Jump` | 1 bit | Unconditional jump (overrides Branch mux) |

These signals are combinational outputs of a logic block that takes the opcode as input.

## Truth Table (Partial) for RISC-V Instructions

| Instruction | RegWrite | ALUSrc | ALUOp | MemRead | MemWrite | MemToReg | Branch |
|---|---|---|---|---|---|---|---|
| R-type (add, sub…) | 1 | 0 | 10 | 0 | 0 | 0 | 0 |
| I-type ALU (addi…) | 1 | 1 | 10 | 0 | 0 | 0 | 0 |
| Load (lw) | 1 | 1 | 00 | 1 | 0 | 1 | 0 |
| Store (sw) | 0 | 1 | 00 | 0 | 1 | X | 0 |
| Branch (beq) | 0 | 0 | 01 | 0 | 0 | X | 1 |
| Jump (jal) | 1 | X | X | 0 | 0 | 0 | 0 |

`X` = don't-care; the value does not affect correctness for that instruction.

## ALU Control: A Two-Level Decode

The main control unit emits a coarse `ALUOp` signal. A separate **ALU control** block combines `ALUOp` with `funct3` and `funct7` to produce the final 4-bit ALU operation code:

```
Main Control ──► ALUOp (2 bits) ──┐
                                   ├──► ALU Control ──► ALUControl (4 bits) ──► ALU
Instruction IR funct3/funct7 ─────┘
```

This two-level approach keeps the main control unit small and its truth table simple.

## Example: Control Signal Flow for `addi x3, x1, 5`

1. IR = `0x00508193` (addi, rs1=x1, rd=x3, imm=5)
2. Opcode = `0010011` (I-type ALU)
3. Control unit asserts: `RegWrite=1`, `ALUSrc=1`, `ALUOp=10`, `MemRead=0`, `MemWrite=0`, `MemToReg=0`, `Branch=0`
4. Datapath: ALU reads x1 from register file, immediate (5) from sign-extender; adds them; result (x1+5) written to x3.

```asm
addi x3, x1, 5    # x3 = x1 + 5
# Control signals configure:
# - Mux B to immediate (ALUSrc=1)
# - ALU to ADD (ALUControl=0010)
# - Write result to register file (RegWrite=1)
# - Skip memory (MemRead=0, MemWrite=0)
```

## Multi-Cycle Control: A Finite State Machine

In a multi-cycle implementation, the control unit is a **finite state machine (FSM)** that moves through states (Fetch, Decode, Execute, Memory, Write-back) and asserts different signals in each state. The next state depends on the current state and the instruction opcode.

```
     ┌─────────────────────────────────────────┐
     │               Fetch (S0)                 │
     └──────────────────┬──────────────────────┘
                        │ (always)
     ┌──────────────────▼──────────────────────┐
     │               Decode (S1)                │
     └───┬──────────────┬──────────────────┬───┘
         │R-type        │Load/Store         │Branch
    ┌────▼────┐    ┌────▼────┐         ┌───▼───┐
    │Execute  │    │Execute  │         │Branch │
    │ (ALU)   │    │ (Addr)  │         │Compl. │
    └────┬────┘    └────┬────┘         └───────┘
         │              │ Load  Store
    ┌────▼────┐    ┌────▼────┬────▼────┐
    │Write-   │    │Memory   │ Memory  │
    │back     │    │Read(S4) │ Write   │
    └─────────┘    └────┬────┘         │
                        │              │
                   ┌────▼────┐         │
                   │Write-   │         │ (done)
                   │back(S5) │         │
                   └─────────┘         │
```

## Common Pitfalls

- **Asserting MemWrite and MemRead simultaneously.** This is a design error — most memory systems do not support simultaneous read and write to the same port.
- **Forgetting to gate RegWrite for store/branch instructions.** These instructions have no destination register; accidentally enabling `RegWrite` corrupts an arbitrary register.
- **Treating ALUOp as the final ALU select.** ALUOp is just a hint to a second-level ALU control block that uses funct3/funct7 to make the final decision.

## Interview Answer

> "The control unit decodes the instruction opcode and generates binary control signals that configure muxes, enable register writes, select ALU operations, and control memory access — it orchestrates *what* the datapath does without touching the data itself."
