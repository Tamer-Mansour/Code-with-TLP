# What Is a CPU Model?

A CPU model is a software representation of a processor that simulates its observable behavior — reading instructions from memory, updating registers, and producing side effects like memory writes and interrupts. CPU models are the heart of every virtual prototype: without one, you have an interconnect with no traffic, peripherals with no master, and software with nowhere to run.

## Why Model a CPU at All?

Real silicon is expensive, late, and hard to debug. A CPU model lets teams:

- Boot and stress-test firmware months before the first chip sample arrives.
- Reproduce rare bugs deterministically — something nearly impossible on hardware.
- Measure performance and power at a higher level of abstraction than RTL simulation.
- Run a full OS and application stack to validate software/hardware co-design decisions.

## What a CPU Model Must Do

Every useful CPU model, regardless of accuracy level, must implement at least these responsibilities:

| Responsibility | Description |
|---|---|
| Instruction fetch | Read bytes from the memory map at the program counter (PC) address |
| Decode | Identify the instruction opcode and operands |
| Execute | Apply the operation — arithmetic, logical, branch, load/store |
| Register update | Write results back to the architectural register file |
| PC advance | Move the PC to the next instruction (or branch target) |
| Exception handling | Detect illegal instructions, alignment faults, traps |

The combination of these steps is called the **fetch-execute loop** — it runs indefinitely until the simulation ends or the CPU is reset or halted.

## Architectural State

A CPU model maintains **architectural state**: the set of registers and flags that software can observe. For a 32-bit RISC-V CPU this includes:

- 32 general-purpose integer registers (`x0`–`x31`)
- The program counter (`pc`)
- Control and status registers (CSRs) — `mstatus`, `mepc`, `mcause`, etc.

This state is what a debugger displays, what a checkpoint saves, and what an OS context-switch saves and restores. A correct model must keep this state identical to what real hardware would hold at every instruction boundary.

## CPU Model vs. Microarchitecture Model

It is critical to distinguish between two different things:

- **Architectural model (ISS)** — Simulates the instruction-set architecture. It does not care *how* the CPU executes — whether it pipelines, out-of-orders, or caches. It only guarantees that the architectural state after each instruction is correct.
- **Microarchitecture model** — Simulates pipeline stages, caches, branch predictors, and execution units. Much slower to simulate, but necessary for performance analysis.

Most virtual prototypes start with an ISS because it is fast enough to boot Linux in seconds and accurate enough for software development. Microarchitecture models come later, driven by performance-tuning requirements.

## A Minimal CPU Model in C (Conceptual Sketch)

```cpp
struct CPU {
    uint32_t reg[32]; // integer registers
    uint32_t pc;      // program counter
};

void step(CPU& cpu, Memory& mem) {
    uint32_t instr = mem.read32(cpu.pc); // fetch
    uint8_t opcode = instr & 0x7F;       // decode (RISC-V major opcode)

    switch (opcode) {
        case 0x13: execute_alu_immediate(cpu, instr); break;
        case 0x33: execute_alu_register(cpu, instr);  break;
        case 0x03: execute_load(cpu, mem, instr);     break;
        case 0x23: execute_store(cpu, mem, instr);    break;
        // ... more opcodes
        default: raise_illegal_instruction(cpu);
    }
    cpu.reg[0] = 0; // x0 is always 0 in RISC-V
}
```

This `step()` function is the atomic unit of simulation. The outer simulation loop calls it in a `while (!cpu.halted)` loop.

## Common Pitfalls

- **Forgetting x0 is hardwired to 0** (RISC-V): any write to register 0 must be silently discarded.
- **Sign-extension errors**: immediate values are sign-extended, not zero-extended, in most ISAs.
- **Misaligned PC**: branching to a non-aligned address must raise an exception, not silently continue.
- **Endianness**: the memory interface must match the CPU's native byte order.

## Interview Answer

> "A CPU model is a software implementation of an instruction-set architecture that correctly updates the architectural register file and program counter for every instruction fetched from the memory map — enabling software to run on a virtual prototype long before silicon is available."
