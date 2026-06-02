# The Fetch Stage in Detail

The **Fetch** stage is the very first thing a processor does in every instruction cycle. It sounds trivial — "just read an instruction from memory" — but it touches some of the most complex engineering in modern processor design. Getting this stage wrong, or slow, cascades into every stage that follows.

## What Happens During Fetch

At the start of every cycle, the Program Counter (PC) holds the address of the next instruction to execute. The fetch stage performs three actions:

1. **Send the PC to instruction memory (or I-cache).** The address is placed on the memory bus.
2. **Read the 32-bit instruction word.** In RISC-V, every base ISA instruction is exactly 4 bytes (32 bits), so the read is always aligned and fixed-width.
3. **Store the result in the Instruction Register (IR).** The IR holds the raw bit pattern until the decode stage can interpret it.
4. **Increment the PC.** PC ← PC + 4 (for the next sequential instruction).

```asm
# Conceptual micro-operations during fetch (RISC-V):
IR  ← MEM[PC]    ; load 32 bits from instruction memory
PC  ← PC + 4     ; advance to next sequential instruction
```

The PC increment and the memory read often happen in parallel to save time.

## The Role of the Instruction Cache

Main memory (DRAM) takes 50–300 clock cycles to respond. If the processor had to wait that long on every fetch, it would spend most of its time doing nothing. The **L1 instruction cache (I-cache)** solves this by keeping recently used instruction words in fast on-chip SRAM. A cache hit typically returns data in 1–4 cycles.

When the I-cache does not contain the requested address (a **cache miss**), the pipeline stalls — the fetch stage is frozen, issuing no new instruction, until the data arrives from a lower cache level or DRAM. This is called an **instruction fetch stall** or **I-cache miss penalty**.

```
PC address
    │
    ▼
┌─────────┐   Hit   ┌────────┐
│ I-Cache │ ──────► │   IR   │ ──► Decode
└─────────┘         └────────┘
    │ Miss
    ▼
  L2/L3/DRAM (stall pipeline until data arrives)
```

## Branch Prediction and Fetch

A major complication during fetch: **the processor does not yet know whether the current instruction is a branch**. That information lives in the decode stage. So the fetch stage blindly increments the PC and fetches the next sequential instruction.

If the current instruction turns out to be a taken branch, the speculatively fetched instruction is wrong. Modern processors use **branch predictors** to guess the branch outcome *before* decode completes:

- **Static prediction:** Always predict not-taken (or always taken). Simple but inaccurate.
- **Dynamic prediction:** Use a Branch Target Buffer (BTB) and a pattern history table to guess based on past behaviour. Modern predictors exceed 95% accuracy on typical workloads.
- **Return Address Stack (RAS):** A dedicated predictor for function-return instructions (`jalr` in RISC-V), which have unpredictable targets if treated generically.

A misprediction discovered later forces a **pipeline flush**: all instructions fetched after the branch must be discarded, costing several cycles of wasted work.

## The Program Counter in Detail

In RISC-V, the PC is a full XLEN-wide register (32 bits for RV32, 64 bits for RV64). It is updated by:

| Source | New PC Value |
|---|---|
| Normal sequential flow | PC + 4 |
| Unconditional jump (`JAL`) | PC + sign-extended immediate |
| Indirect jump (`JALR`) | (rs1 + sign-extended immediate) & ~1 |
| Conditional branch (taken) | PC + sign-extended immediate |
| Exception / interrupt | Trap vector address (e.g., `mtvec`) |

The fetch stage must capture *both* the current PC (needed by later stages for PC-relative addressing) and the incremented PC (needed for sequential fetch).

## Alignment and Compressed Instructions

The base RISC-V ISA (RV32I/RV64I) requires 4-byte alignment — the PC must always be a multiple of 4. Misaligned fetches cause an **instruction-address misaligned** exception.

The **C extension** (compressed instructions) allows 2-byte (16-bit) instructions, so the PC increments by 2 for those, and fetch must read 16 bits. This complicates fetch logic but reduces code size by up to 30%.

## Common Pitfalls

- **Assuming fetch is always one cycle.** Cache misses can stall it for dozens or hundreds of cycles.
- **Forgetting the PC holds the *current* instruction's address.** After increment, the old PC value must be preserved and forwarded to later stages (for JAL link address calculation, for instance).
- **Mixing up I-cache and D-cache.** Instruction fetch uses the I-cache; data load/store uses the D-cache. They are separate in most processors (Harvard-style internal caches, even in von Neumann architectures).

> **Interview answer:** The fetch stage reads the instruction word at the address stored in the PC from instruction memory (usually the I-cache), increments the PC by 4, and stores the raw instruction bits in the Instruction Register, ready for the decode stage. Cache misses and branch prediction are the two main performance challenges here.
