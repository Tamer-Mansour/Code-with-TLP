# What Are Registers and Why So Fast?

Registers are the fastest storage locations available to a CPU. They live inside the processor die itself, just a few hundred microns from the ALU, and can be read or written in a single clock cycle — or even within a single phase of a cycle.

## The Memory Hierarchy at a Glance

| Level | Location | Latency | Size (typical) |
|---|---|---|---|
| Registers | On-chip, next to ALU | ~0.3 ns (< 1 cycle) | 32 × 32-bit (RISC-V) |
| L1 Cache | On-chip | 1–4 cycles | 32–64 KB |
| L2 Cache | On-chip | 10–20 cycles | 256 KB – 4 MB |
| L3 Cache | On-chip / near-chip | 30–60 cycles | 8–64 MB |
| DRAM | Off-chip | 100–300 cycles | GBs |
| SSD/NVMe | Off-chip | Millions of cycles | TBs |

Registers win because:

1. **Distance** — they are physically adjacent to the ALU; signals travel almost no distance.
2. **No address decoding delay** — a 32-register file uses only a 5-bit select; a full DRAM address decode takes many more gate delays.
3. **Dedicated wires** — each read/write port has its own bus; no arbitration needed.
4. **Flip-flop storage** — built from high-speed SRAM cells (or even simple flip-flops), optimized for access speed rather than density.

## How a Register File Works

A **register file** is a small, multi-ported SRAM array. For RISC-V's 32 general-purpose registers:

- **Two read ports** — supply RS1 and RS2 operands to the ALU simultaneously.
- **One write port** — accepts the result from the ALU or data memory.

```
      5-bit RS1 ──► [Read Port A] ──► 32-bit data to ALU input A
      5-bit RS2 ──► [Read Port B] ──► 32-bit data to ALU input B
      5-bit RD  ──►
      32-bit WD ──► [Write Port ] (enabled by RegWrite control signal)
```

Reading is asynchronous (combinational); writing is clocked (happens on the rising edge).

## Why Not Just Use Cache?

Cache cells are designed for density — small, tightly packed, with shared bit-lines across many rows. They need complex address decoding and arbitration logic. A register file is designed for **speed**: each register has its own dedicated sense amplifiers and word lines, so access is nearly instantaneous compared to even L1 cache.

## RISC-V Register Count: Why 32?

RISC-V specifies 32 integer registers (x0–x31). The count is a hardware/software trade-off:

- **More registers** → fewer spills to memory, faster code — but larger instruction encoding (more bits for register fields) and larger, slower register file.
- **Fewer registers** → smaller encoding, faster file — but more spills.

32 is a sweet spot: `log₂(32) = 5` bits per register field, and three 5-bit fields fit comfortably in a 32-bit instruction word alongside an opcode and other fields.

## Worked Example: Register vs Memory Access Cost

Suppose a loop body reads variable `i` from memory 10,000 times at 100-cycle latency vs. keeping it in a register at 1-cycle access.

```python
# Cost if i is always in memory:
cost_memory = 10_000 * 100  # = 1,000,000 cycles

# Cost if i is kept in a register:
cost_register = 10_000 * 1  # = 10,000 cycles

speedup = cost_memory / cost_register  # = 100x
```

This is why compilers work hard to keep loop variables in registers — register allocation is one of the most impactful compiler optimizations.

## Common Pitfalls

- **Writing to x0 in RISC-V.** Register x0 is hardwired to zero. Writes to it are silently discarded. Reading it always returns 0.
- **Assuming registers persist across function calls.** Calling conventions distinguish caller-saved (volatile) from callee-saved (non-volatile) registers. Ignoring this causes subtle bugs.
- **Counting registers in bits vs. bytes.** A 32-register file of 64-bit registers holds 32 × 8 = 256 bytes total — tiny compared to any cache.

## Interview Answer

> "Registers are fast because they are on-chip flip-flop/SRAM cells physically adjacent to the ALU, accessible in under one clock cycle through dedicated read/write ports — unlike cache or DRAM, which require address decoding, shared buses, and longer signal paths."
