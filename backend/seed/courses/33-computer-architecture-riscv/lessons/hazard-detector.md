# Exercise: Detect Data Hazards in an Instruction Stream

In this exercise you will implement a **data hazard detector** for a simplified RISC-V five-stage pipeline (IF → ID → EX → MEM → WB). Given a sequence of RISC-V instructions, your program must identify every RAW (Read After Write) data hazard pair and determine whether each hazard can be resolved by forwarding alone or requires a stall.

## Background

A RAW hazard exists between instruction **I** (producer) at position `i` and instruction **J** (consumer) at position `j > i` when:

- I writes a register `rd`.
- J reads that same register as `rs1` or `rs2`.
- The gap between them is small enough that J's EX stage arrives before I's result is committed to the register file.

With full forwarding hardware:

- **ALU-to-ALU, gap = 0** (back-to-back): forwarding resolves it, **0 stalls**.
- **Load-to-use, gap = 0** (back-to-back): forwarding cannot resolve it, **1 stall**.
- **Gap >= 2**: no hazard at all — the result is ready in time.

## What You Will Implement

Write a Python program that:

1. Reads a list of RISC-V-style instructions from stdin.
2. Detects all RAW hazard pairs within a window of the two immediately following instructions.
3. For each hazard, reports whether it needs a stall or is resolved by forwarding.
4. Prints the total number of stall cycles required.

Each instruction is given as a simplified assembly string. Your program only needs to handle the formats described in the prompt file.

## Skills Practiced

- Dependency analysis on instruction streams
- Understanding forwarding paths and their limitations
- Identifying the load-use hazard pattern
- Computing CPI overhead from stalls
