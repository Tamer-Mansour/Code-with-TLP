# The Control Unit and Fetch-Decode-Execute

The **control unit** reads each instruction and drives the correct control signals to every component of the datapath — multiplexers, register files, the ALU, and memory. This lesson walks through the complete instruction cycle in detail, including a full control signal table and a comparison of single-cycle vs. pipelined implementations.

## The RISC-V Instruction Format Refresher

A 32-bit RISC-V instruction encodes all needed information in fixed-width fields:

```
R-type (register-register):
 31      25 24  20 19  15 14  12 11   7 6        0
 [funct7  ][rs2  ][rs1  ][funct3][rd   ][opcode   ]

I-type (immediate / loads):
 31          20 19  15 14  12 11   7 6        0
 [imm[11:0]   ][rs1  ][funct3][rd   ][opcode   ]

S-type (stores):
 31      25 24  20 19  15 14  12 11    7 6        0
 [imm[11:5]][rs2  ][rs1  ][funct3][imm[4:0]][opcode]

B-type (branches):
 [imm[12,10:5]][rs2][rs1][funct3][imm[4:1,11]][opcode]
```

The opcode field (bits 6:0) is the primary dispatch selector. funct3 and funct7 distinguish operations within a group (e.g., ADD vs SUB, BEQ vs BNE).

## Phase 1: Instruction Fetch (IF)

```
IR  ← Memory[PC]          # load 32-bit instruction word from I-cache
PC  ← PC + 4              # advance to next instruction
```

The Program Counter is a 32-bit (or 64-bit) register that holds the address of the next instruction. In a normal sequential flow, it increments by 4 (4 bytes per instruction). A branch, jump, or exception can override this.

**Instruction cache (I$)**: In a pipelined CPU, the instruction fetch must complete in one cycle. Main memory takes 50+ cycles, so a **dedicated instruction cache** is consulted. On a hit, the instruction is available in 1–2 cycles. On a miss, the pipeline stalls while the cache line is fetched from L2.

## Phase 2: Instruction Decode (ID)

The **decoder** is a combinational circuit that dissects the instruction bits:

1. Extract opcode (bits 6:0).
2. Extract rs1 (bits 19:15), rs2 (bits 24:20), rd (bits 11:7).
3. Extract and sign-extend the immediate (varies by instruction type).
4. Assert control signals to the rest of the datapath.

### Complete Control Signal Table for RISC-V Core Instructions

| Instruction | RegWrite | ALUSrc | ALUOp | MemRead | MemWrite | MemToReg | Branch |
|-------------|----------|--------|-------|---------|----------|----------|--------|
| R-type (ADD,SUB…) | 1 | 0 (reg B) | from funct | 0 | 0 | 0 (ALU result) | 0 |
| I-type (ADDI) | 1 | 1 (immediate) | ADD | 0 | 0 | 0 | 0 |
| LW (load word) | 1 | 1 (immediate) | ADD | 1 | 0 | 1 (memory) | 0 |
| SW (store word) | 0 | 1 (immediate) | ADD | 0 | 1 | X | 0 |
| BEQ (branch) | 0 | 0 | SUB | 0 | 0 | X | 1 |
| JAL (jump & link) | 1 | 1 | ADD | 0 | 0 | 0 (PC+4) | 0 |

### Sign Extension

Immediates in RISC-V are sign-extended from their encoded width (12 bits for I/S-type) to 32 bits before being used:

```
12-bit immediate: 111111111110  (= -2 in two's complement)
32-bit sign extended: 11111111111111111111111111111110  (= -2 in 32-bit)
```

The sign extender copies the MSB of the immediate into all upper bits.

## Phase 3: Execute (EX) and Beyond

### ALU Operation

The ALU receives two inputs:
- **A**: always from the first source register (`rs1`).
- **B**: selected by the `ALUSrc` MUX — either `rs2` (for R-type) or the sign-extended immediate (for I/S/B-type).

The ALU control unit maps (ALUOp, funct3, funct7) → a 4-bit ALU opcode. For example:

```
Instruction: ADD  → ALUOp=10, funct7=0000000, funct3=000 → ALU: 0010 (ADD)
Instruction: SUB  → ALUOp=10, funct7=0100000, funct3=000 → ALU: 0110 (SUB)
Instruction: AND  → ALUOp=10, funct3=111       → ALU: 0000 (AND)
Instruction: LW   → ALUOp=00  (always ADD, compute address)
Instruction: BEQ  → ALUOp=01  (always SUB, compare → check Zero flag)
```

### Memory Access (MEM stage)

For **loads** (`LW`, `LH`, `LB`): the ALU result is the memory address. The data memory is read, and the loaded word is available at the end of the MEM stage.

For **stores** (`SW`, `SH`, `SB`): the ALU result is the address, and `rs2` is the data to write. The memory write happens during MEM.

### Writeback (WB stage)

The `MemToReg` MUX selects which value is written back to the register file:
- `MemToReg = 0`: write ALU result (for R-type, I-type arithmetic, JAL).
- `MemToReg = 1`: write memory data (for loads).

## Detailed Example: Executing `LW x5, 8(x3)`

```
Fetch:
  IR ← Memory[PC]
  PC ← PC + 4

Decode:
  opcode = 0000011 (load)
  funct3 = 010 (LW = 32-bit)
  rs1 = x3, rd = x5, imm = 8
  Control: RegWrite=1, ALUSrc=1, ALUOp=ADD, MemRead=1, MemToReg=1

Execute:
  ALU_A = Register[x3]           ← base address
  ALU_B = sign_extend(8) = 8     ← offset (ALUSrc=1 selects immediate)
  ALU_result = Register[x3] + 8  ← effective memory address

Memory:
  data = Memory[ ALU_result ]    ← 32-bit load from computed address

Writeback:
  Register[x5] ← data            ← MemToReg=1 selects memory data
```

## Single-Cycle Datapath

In a **single-cycle CPU**, all phases complete in one clock period. The clock period must accommodate the **worst-case instruction** — the load word, which traverses:

```
I-cache (fetch) → decode → register read → ALU add → D-cache → MUX → register write
~200 ps         + 100 ps + 200 ps        + 200 ps  + 200 ps  + 50 ps + 50 ps
= ~1000 ps → max clock ≈ 1 GHz (with ideal cache hits)
```

The limitation: a simple `AND` instruction finishes in ~500 ps but must still wait out the full 1000 ps clock period.

## Multi-Cycle Datapath

Split the execution into smaller, equal-length steps. Each step uses one cycle:

```
LW: IF → ID → EX → MEM → WB = 5 cycles
ADD:IF → ID → EX → WB      = 4 cycles
```

The clock period is the length of one step (~200 ps), so the clock can run 5× faster. Shared resources (the ALU, memory) are reused across cycles with the help of internal registers.

Multi-cycle CPUs were common in the 1980s and 1990s (early MIPS). The penalty: LW still takes 5 steps × 200 ps = 1000 ps (same latency), but the throughput improves when multiple instructions are in flight via pipelining.

## The Role of Microcode

Complex CISC instructions (e.g., x86 `REP MOVS` — move a block of memory — or `ENTER` — set up a stack frame) are too complex to decode in one cycle with combinational logic. These are implemented in **microcode**: a stored table of micro-operations (µops) inside the CPU.

Modern x86 CPUs:
1. Decode each x86 instruction into 1–4 RISC-like µops.
2. Execute the µops through a RISC-style pipelined execution engine.

This is why modern x86 CPUs can achieve CPI close to 1 despite the irregular CISC ISA: the front-end translates to µops, and the back-end is essentially RISC.

## Control Unit Implementation Options

### Hardwired Control

The decoder is a fixed combinational logic circuit (ROM + gates). Fast (one clock-cycle decode) but inflexible — changing the ISA means redesigning gates. Used in RISC designs.

### Microcoded Control

Instruction opcodes index into a ROM (microprogram store). Each ROM entry drives the control signals for one micro-step. Flexible (patch microcode in firmware) but slower. Used for complex instructions in CISC CPUs.

### Hybrid

Modern x86: hardwired decode for common simple instructions (the fast path), microcoded decode for complex instructions (the slow path). Over 95% of instructions hit the fast path.
