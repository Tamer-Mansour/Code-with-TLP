# What Is a CPU? Core Responsibilities

A Central Processing Unit (CPU) is the primary component of a computer responsible for executing instructions. Every program you run — from a web browser to a database engine — ultimately becomes a stream of instructions that the CPU fetches, decodes, and executes one after another.

## The Three Core Responsibilities

The CPU has three fundamental jobs:

1. **Fetch** — retrieve the next instruction from memory.
2. **Decode** — interpret what that instruction means.
3. **Execute** — carry out the operation (arithmetic, memory access, branching, etc.).

This cycle repeats billions of times per second on a modern processor. Understanding it is the foundation for understanding everything else about computer architecture.

## What Lives Inside a CPU?

| Component | Role |
|---|---|
| Datapath | Wires, ALU, registers — the "muscles" that do the actual work |
| Control Unit | Generates control signals that tell the datapath what to do |
| Register File | Ultra-fast on-chip storage for operands and results |
| Program Counter (PC) | Holds the address of the next instruction |
| Instruction Register (IR) | Holds the currently executing instruction |
| Cache (L1/L2) | On-chip memory that hides the latency of main RAM |

## Why the CPU Is Not Just an ALU

A common beginner mistake is equating the CPU with the ALU (Arithmetic Logic Unit). The ALU is only one part of the datapath — it performs arithmetic and logic. But the CPU also needs to:

- Decide *which* operands to feed the ALU (register file + muxes).
- Route results back to registers or memory.
- Calculate the next PC value (sequential or branch target).
- Signal the memory system to load or store data.

All of that orchestration is the control unit's job.

## The Fetch-Decode-Execute Loop in Pseudocode

```python
while True:
    instruction = memory[PC]   # Fetch
    PC = PC + 4                # Advance PC (4 bytes for 32-bit ISA)
    opcode, operands = decode(instruction)  # Decode
    execute(opcode, operands)  # Execute (may update PC for branches)
```

This tight loop is the heartbeat of every stored-program computer, from an 8-bit microcontroller to a 128-core server chip.

## Performance Factors

Three quantities determine raw CPU throughput:

- **Clock frequency** — how many cycles per second (e.g., 3.5 GHz = 3.5 × 10⁹ cycles/s).
- **CPI (Cycles Per Instruction)** — average number of clock cycles each instruction takes.
- **Instruction count** — how many instructions the compiler emits for a given program.

> **CPU Time = Instruction Count × CPI × Clock Period**

Optimizing any one of these factors can improve performance, which is why chip designers, compiler writers, and ISA architects must all work together.

## Common Pitfalls

- **Confusing the CPU with the processor package.** A modern "processor" may contain multiple CPU cores plus GPU cores, a memory controller, and an I/O hub — all on one die.
- **Assuming higher clock speed = faster.** CPI and instruction count matter just as much.
- **Ignoring memory latency.** A 3 GHz CPU stalls for ~100 ns on a cache miss — that is ~300 wasted cycles.

## Interview Answer

> "A CPU fetches instructions from memory, decodes them to determine the operation and operands, then executes them using the datapath (ALU + registers) under the direction of the control unit — repeating this fetch-decode-execute cycle continuously."
