# Von Neumann vs Harvard Architecture

Every processor design must answer a fundamental question: where do instructions and data live, and can they share the same memory bus? The two canonical answers define the Von Neumann and Harvard architectures — models that still shape every chip designed today.

## Von Neumann Architecture

Proposed in the 1945 EDVAC report (credited to John von Neumann), this model stores **instructions and data in the same memory**, accessed over a **single shared bus**.

```
+--------+       shared bus       +---------+
|  CPU   |<--------------------->| Memory  |
| (ALU + |   (instructions AND   | (RAM)   |
| Regs)  |      data together)   |         |
+--------+                       +---------+
       |                               |
       +----------- I/O ---------------+
```

Key properties:
- **Unified address space** — instructions and data share the same memory map.
- **Single bus** — in any given cycle the processor can fetch an instruction *or* read/write data, but not both simultaneously.
- **Von Neumann bottleneck** — the shared bus limits throughput; the CPU is often idle waiting for memory.
- **Flexibility** — programs can be loaded, modified, or generated at runtime (self-modifying code, JIT compilation, dynamic linking).

## Harvard Architecture

Developed for the Harvard Mark I (1944), this model uses **separate memories and separate buses** for instructions and data.

```
+--------+   instruction bus   +------------------+
|  CPU   |<------------------->| Instruction Mem  |
| (ALU + |                     +------------------+
| Regs)  |
|        |   data bus          +------------------+
|        |<------------------->|    Data Memory   |
+--------+                     +------------------+
```

Key properties:
- **Two simultaneous accesses** — the CPU can fetch the next instruction while reading or writing data in the same cycle.
- **Higher bandwidth** — eliminates the instruction/data bus contention.
- **Simpler pipeline** — instruction fetch and data memory access no longer compete; the pipeline can overlap them without stalls.
- **Less flexible** — code lives in a separate (often read-only) address space; runtime code generation is more complex.

## Side-by-Side Comparison

| Property | Von Neumann | Harvard |
|---|---|---|
| Memory spaces | Unified (one) | Separate (two) |
| Buses | Single shared bus | Dedicated instruction + data buses |
| Bandwidth | Lower (bottleneck) | Higher (parallel access) |
| Pipeline stalls | Structural hazards possible | Fewer structural hazards |
| Runtime code gen | Easy | Complex |
| Typical use | General-purpose CPUs | Microcontrollers, DSPs, GPUs |

## The Modified Harvard Architecture

Modern general-purpose CPUs use a **modified Harvard architecture**: a unified main memory (Von Neumann), but **separate L1 instruction and data caches** inside the chip.

```
Main Memory (Von Neumann, unified)
         |
    Memory Bus
         |
    +----+----+
    |  L2/L3  |   unified cache
    +----+----+
         |
   +-----+-----+
   |           |
 L1-I$       L1-D$    <-- Harvard split inside the CPU
(instruction) (data)
         |
        CPU
```

This gives you the best of both worlds:
- The **programming simplicity** of a single address space.
- The **pipeline bandwidth** advantage of separate instruction and data paths.

All modern x86, ARM, and RISC-V processors use this modified design. The ARM Cortex-M series microcontrollers use a pure Harvard design, keeping code in flash and data in SRAM.

## Worked Example: Pipeline Stall

In a Von Neumann pipeline, a `LOAD` instruction (data memory access) and an instruction fetch in the next cycle must share the memory bus. If the cache misses on both, one must wait:

```
Cycle:     1    2    3    4    5
Instr N:  IF   ID   EX  MEM   WB
Instr N+1: IF (stall — bus busy)  ID ...
```

In a Harvard (or modified Harvard) design, the instruction fetch for N+1 uses the instruction bus/cache while N's data access uses the data bus/cache — no stall.

## Common Pitfall

Saying "modern CPUs are Von Neumann" is only half-right. They use unified *main memory* (Von Neumann) but separate *caches* (Harvard). Interview questions often probe this nuance.

> **Interview answer:** "Von Neumann uses one memory and one bus for both instructions and data — simple but prone to a bandwidth bottleneck. Harvard uses separate memories and buses for each — faster pipelines but harder to support runtime code generation. Modern CPUs use a modified Harvard design: unified main memory with separate L1 instruction and data caches."
