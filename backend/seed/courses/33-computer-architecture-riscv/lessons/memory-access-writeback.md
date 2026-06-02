# Memory Access and Write-Back Stages

After the execute stage has computed a result, two more stages complete the instruction's journey: **Memory Access (MEM)** reads or writes data memory, and **Write-Back (WB)** deposits the final result into the destination register. Together they close the loop between computation and persistent state.

## The Memory Access Stage

Most instructions produce their result entirely in the execute stage (ALU output) and pass through MEM as a no-op. The MEM stage is only active for **load** and **store** instructions, which must interact with the data memory system (or D-cache).

### Loads

A load instruction (`LW`, `LH`, `LB` and their unsigned variants in RISC-V) uses the address computed by the ALU in execute, then reads a value from data memory:

```asm
lw  x5, 8(x1)      # x5 ← MEM[x1 + 8]
```

During MEM:
1. The effective address from the execute stage is placed on the D-cache address bus.
2. The D-cache returns the value at that address (or stalls the pipeline on a miss).
3. For sub-word loads (`LH`, `LB`), the data is **sign-extended** or **zero-extended** to 32/64 bits here.

### Stores

A store instruction (`SW`, `SH`, `SB`) writes a register value to memory:

```asm
sw  x6, 12(x2)     # MEM[x2 + 12] ← x6
```

During MEM:
1. The effective address is placed on the D-cache address bus.
2. The value of `rs2` (forwarded from the pipeline) is written to that address.
3. Stores do **not** produce a value for write-back — the `RegWrite` control signal is 0.

### Data Cache and Stalls

Like the I-cache, the **D-cache** is on-chip SRAM. A D-cache miss can stall the pipeline for tens to hundreds of cycles. This is one of the most impactful performance bottlenecks in real systems.

```
ALU address ──► D-Cache ──► (hit) data value ──► WB stage
                    │
                    └── (miss) ──► L2/L3/DRAM (stall pipeline)
```

### Memory Alignment

RISC-V requires **natural alignment** for loads and stores in the base ISA:
- `LW`/`SW` address must be a multiple of 4
- `LH`/`SH` address must be a multiple of 2
- `LB`/`SB` has no alignment requirement

A misaligned access raises a **load-address-misaligned** or **store-address-misaligned** exception. The `Zicbo` and `Zam` extensions can relax this.

## The Write-Back Stage

Write-back is the final stage. It selects the correct result value and writes it into the destination register `rd` in the register file.

The multiplexer at write-back selects from two possible sources:

| `MemToReg` | Source written to rd |
|---|---|
| 0 | ALU result (from execute) |
| 1 | Data from memory (from MEM load) |

```
ALU result ──► MUX ──► Register File [rd]
               │ 0
D-Cache data ──► │ 1
          MemToReg─┘
```

For instructions that do not write a register (stores, branches), `RegWrite = 0` and the register file ignores the write entirely.

### Write-Back and Forwarding

In a pipelined processor, a register value written in the WB stage of instruction N is needed by the execute stage of instruction N+2 (or later). Forwarding paths route the WB result directly back to the EX stage mux, preventing a stall:

```
WB stage result ──────────────────────────────► EX stage A/B mux
                                                 (forwarding path)
```

Without forwarding, the pipeline would need to stall for two cycles after every instruction that produces a result.

## Worked Example: `LW x5, 4(x1)` End-to-End

Assume x1 = 0x1000:

| Stage | Action |
|---|---|
| IF | Fetch instruction word at PC |
| ID | Decode opcode as I-type LOAD; read x1 value; sign-extend imm = 4 |
| EX | ALU: 0x1000 + 4 = 0x1004 (effective address) |
| MEM | D-Cache read at 0x1004 → returns 0xDEADBEEF |
| WB | Write 0xDEADBEEF into register x5 |

## Worked Example: `SW x6, 8(x2)` End-to-End

Assume x2 = 0x2000, x6 = 42:

| Stage | Action |
|---|---|
| IF | Fetch instruction word |
| ID | Decode as S-type STORE; read x2 and x6; sign-extend imm = 8 |
| EX | ALU: 0x2000 + 8 = 0x2008 (effective address) |
| MEM | D-Cache write: MEM[0x2008] ← 42 |
| WB | No register write (`RegWrite = 0`) |

## Common Pitfalls

- **Forgetting to sign-extend on byte/halfword loads.** `LB` vs `LBU` is a common source of bugs: `LB` sign-extends the byte, `LBU` zero-extends it. Choosing the wrong one gives correct results for positive values but breaks for values ≥ 128.
- **Assuming stores write back.** Stores write to memory, not to a register. The write-back stage is a no-op for them.
- **Overlooking the D-cache miss penalty.** A single cache-missing load can stall the pipeline far longer than any ALU instruction, dominating overall runtime in memory-bound programs.
- **Structural hazard: register file read/write in same cycle.** Decode reads the register file; write-back writes it. In a single-ported register file, these cannot happen simultaneously — most RISC designs use a register file with separate read and write ports, or handle this with careful timing.

> **Interview answer:** The memory-access stage reads or writes the data cache at the address computed by the ALU (only for load/store instructions), while the write-back stage selects either the ALU result or the loaded memory value and writes it into the destination register — completing the instruction's effect on processor state.
