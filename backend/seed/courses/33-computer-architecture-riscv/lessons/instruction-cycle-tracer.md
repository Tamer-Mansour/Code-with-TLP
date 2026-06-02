# Exercise: Trace a Simple Instruction Cycle

In this exercise you will write a program that simulates a minimal RISC-V instruction cycle tracer. Given a sequence of simplified instruction descriptors on standard input, your program must determine — for each instruction — which of the five pipeline stages are **active** (do real work) versus **idle** (no-op), and output the result.

## What You Will Implement

Your tracer reads a list of instruction types and, for each one, prints a five-character stage trace showing which stages perform real work (`*`) and which are idle (`-`):

```
Stages: IF  ID  EX  MEM  WB
```

Rules:
- **IF** is always active (`*`) — every instruction must be fetched.
- **ID** is always active (`*`) — every instruction must be decoded and registers read.
- **EX** is always active (`*`) — every instruction passes through the ALU (at minimum for address/branch computation).
- **MEM** is active (`*`) only for `LOAD` and `STORE` instructions.
- **WB** is active (`*`) for all instructions **except** `STORE` and `BRANCH`.

## Input / Output Format

Input: one instruction type per line. Valid types: `ADD`, `SUB`, `AND`, `OR`, `XOR`, `SLT`, `ADDI`, `LOAD`, `STORE`, `BRANCH`, `JAL`.

Output: for each instruction, one line in the format:
```
<TYPE>: IF=* ID=* EX=* MEM=<*|-> WB=<*|->
```

## Example

Input:
```
ADD
LOAD
STORE
BRANCH
JAL
```

Output:
```
ADD: IF=* ID=* EX=* MEM=- WB=*
LOAD: IF=* ID=* EX=* MEM=* WB=*
STORE: IF=* ID=* EX=* MEM=* WB=-
BRANCH: IF=* ID=* EX=* MEM=- WB=-
JAL: IF=* ID=* EX=* MEM=- WB=*
```

## Getting Started

Think of this as encoding the per-instruction datapath truth table from your reading. The key questions to ask for each instruction type are:

1. Does this instruction read or write data memory? → MEM stage
2. Does this instruction produce a value that goes into a register? → WB stage

Start by sketching the truth table on paper before writing code. Pay special attention to `STORE` (writes memory, does not write registers) and `BRANCH` (no memory access, no register write).
