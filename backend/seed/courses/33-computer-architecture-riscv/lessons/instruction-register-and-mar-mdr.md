# Instruction Register, MAR, and MDR

To connect the CPU's internal logic to external memory, three staging registers do the heavy lifting: the **Instruction Register (IR)**, the **Memory Address Register (MAR)**, and the **Memory Data Register (MDR)**. These registers act as "waiting rooms" that hold data in transit between CPU and memory.

## Instruction Register (IR)

The IR holds the **currently executing instruction** after it has been fetched from memory. Once the instruction word lands in the IR, the decode logic reads it to identify:

- The opcode (what operation to perform)
- Source register numbers (RS1, RS2)
- Destination register number (RD)
- Immediate fields (constants embedded in the instruction)
- Function codes (funct3, funct7 in RISC-V)

```
Memory ──[32-bit instruction word]──► IR
                                       │
                     ┌─────────────────┼─────────────────┐
                     ▼                 ▼                  ▼
                  opcode [6:0]    rs1 [19:15]        rd [11:7]
                                  rs2 [24:20]       funct3 [14:12]
                                  imm [various]     funct7 [31:25]
```

The IR is transparent to the programmer — you never explicitly read or write it in user-mode code. It is an **internal** CPU register that exists to pipeline the fetch and decode stages without losing the instruction.

### Why Does the IR Exist?

Without an IR, the instruction memory output would need to stay stable throughout the entire execute phase. By latching the instruction into the IR, the memory bus is freed for other uses (e.g., a data memory access in the same cycle in a multi-cycle design).

## Memory Address Register (MAR)

The MAR holds the **address** that the CPU wants to send to memory — either for an instruction fetch or a data load/store.

```
MAR ──[address bus]──► Memory System
```

The MAR is loaded by the control unit:
- During **fetch**: MAR ← PC
- During **load/store execute**: MAR ← ALU result (effective address)

In a **multi-cycle** implementation, these two uses happen at different clock cycles, so one MAR suffices. In a fully pipelined design the instruction and data memory ports are separate (Harvard-style L1 caches), effectively giving two implicit MARs.

## Memory Data Register (MDR)

The MDR holds the **data** being transferred to or from memory.

- **On a load:** MDR ← Memory[MAR] — data read from memory waits here before being written to the register file.
- **On a store:** MDR ← register value — data to be written waits here while the address is being computed.

```
Read path:  Memory[MAR] ──► MDR ──► Register File (write port)
Write path: Register File ──► MDR ──► Memory[MAR]
```

## Multi-Cycle Execution Trace

Here is the step-by-step execution of `lw x5, 8(x2)` in a classic multi-cycle datapath:

| Cycle | Stage | What Happens |
|---|---|---|
| 1 | Fetch | MAR ← PC; IR ← Mem[MAR]; PC ← PC+4 |
| 2 | Decode | Decode IR; read x2 from register file |
| 3 | Execute | MAR ← x2 + sign_extend(8) (ALU computes address) |
| 4 | Memory | MDR ← Mem[MAR] (data read from memory) |
| 5 | Write-back | x5 ← MDR (result written to register file) |

Compare this to an R-type instruction like `add x3, x1, x2`:

| Cycle | Stage | What Happens |
|---|---|---|
| 1 | Fetch | MAR ← PC; IR ← Mem[MAR]; PC ← PC+4 |
| 2 | Decode | Decode IR; read x1, x2 from register file |
| 3 | Execute | ALU result ← x1 + x2 |
| 4 | Write-back | x3 ← ALU result (no memory access needed) |

R-type instructions finish in 4 cycles; load/store instructions need 5.

## RISC-V Context: Are MAR/MDR Visible?

In modern RISC-V implementations, the MAR and MDR are **micro-architectural** details — they are not part of the ISA and are not directly accessible to software. They exist in textbook multi-cycle descriptions and in many real implementations but are not named in the specification. The ISA only specifies observable state: registers and memory.

## Common Pitfalls

- **Confusing IR with the instruction cache.** The IR is a single register holding one instruction; the instruction cache holds many cached instructions.
- **Assuming MAR/MDR exist in all implementations.** A single-cycle or deeply pipelined design may not have explicit MAR/MDR registers — their functionality is performed by dedicated ports and pipeline registers instead.
- **Write-back timing.** In a multi-cycle machine, writing MDR to the register file happens one cycle *after* the memory read completes — failing to account for this in timing diagrams is a common exam mistake.

## Interview Answer

> "The IR latches the fetched instruction so the decode logic can read it stably; the MAR holds the memory address being accessed; and the MDR holds data in transit between the register file and memory — together they stage the flow of instructions and data across the CPU-memory boundary."
