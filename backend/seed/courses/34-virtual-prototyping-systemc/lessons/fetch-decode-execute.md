# The Fetch-Decode-Execute Cycle

The **Fetch-Decode-Execute (FDE) cycle** is the fundamental operational loop of every stored-program processor. Whether you are studying a classic 8-bit microprocessor or modeling a modern 64-bit core in SystemC, all CPU behavior reduces to this repeating sequence.

## The Three Stages

### 1. Fetch

The CPU reads the instruction at the address held in the **Program Counter (PC)**.

- The PC is placed on the address bus.
- The memory system returns the instruction word.
- The instruction is latched into the **Instruction Register (IR)**.
- The PC is incremented (speculatively) to point to the next sequential instruction.

```
PC → Memory → IR
PC ← PC + instruction_size
```

### 2. Decode

The control unit interprets the binary fields of the instruction:

- The **opcode** field selects the operation.
- **Register index** fields are sent to the register file to read operand values.
- **Immediate** fields are sign-extended and prepared for the ALU.
- The instruction format (R, I, S, B, U, J in RISC-V) determines which fields carry which meaning.

### 3. Execute

The ALU or other functional unit performs the operation:

- **ALU instructions** — compute result, optionally update flags.
- **Load** — compute effective address, issue memory read, write result to destination register.
- **Store** — compute effective address, issue memory write.
- **Branch** — evaluate condition, update PC if taken.

## Pipeline Overlap

In a real processor these stages overlap across multiple instructions simultaneously. While instruction N is executing, instruction N+1 is being decoded and instruction N+2 is being fetched.

```
Cycle:       1   2   3   4   5   6
Instr N      F   D   E
Instr N+1        F   D   E
Instr N+2            F   D   E
Instr N+3                F   D   E
```

This pipeline parallelism means data **hazards** (an instruction needs a result not yet written by the previous one) and control **hazards** (a branch changes PC before the fetched instruction is correct) must be handled explicitly.

## SystemC Functional Model

A purely functional (untimed) model collapses all three stages into a single C++ loop:

```cpp
void cpu_thread() {
    pc = RESET_VECTOR;

    while (true) {
        // --- FETCH ---
        uint32_t instr = mem_read_word(pc);

        // --- DECODE ---
        uint32_t opcode = instr & 0x7F;
        uint32_t rd     = (instr >> 7)  & 0x1F;
        uint32_t funct3 = (instr >> 12) & 0x07;
        uint32_t rs1    = (instr >> 15) & 0x1F;
        uint32_t rs2    = (instr >> 20) & 0x1F;

        // --- EXECUTE ---
        switch (opcode) {
            case 0x33: execute_alu_r(rd, rs1, rs2, funct3);  break;
            case 0x13: execute_alu_i(rd, rs1, instr, funct3); break;
            case 0x03: execute_load(rd, rs1, instr, funct3);  break;
            case 0x23: execute_store(rs1, rs2, instr, funct3); break;
            case 0x63: execute_branch(rs1, rs2, instr, funct3); break;
            // ...
            default:   throw std::runtime_error("Illegal instruction");
        }

        wait(cycle_time);  // advance simulation time
    }
}
```

## Timed Model Considerations

When adding timing, each stage takes one or more clock cycles. Use SystemC `wait()` calls or pipeline stages modeled with `sc_fifo` channels to represent:

- **Fetch latency** — memory access time (cache hit vs miss).
- **Decode latency** — typically 1 cycle for a simple in-order core.
- **Execute latency** — 1 cycle for ALU, multiple cycles for multiply/divide, variable for load (cache-dependent).

## Common Pitfalls

- **PC update order** — in a branch-on-execute model the PC must be set to either the branch target or PC+4, not the PC value from before the increment.
- **Conflating functional and timing correctness** — get functional behavior correct first (all instructions produce the right register and memory values), then add timing.
- **Missing wait() call** — in a SystemC model without a `wait()` the simulation time never advances, causing an infinite loop at time zero.

## Interview Answer

> "Fetch reads the instruction at the current PC; Decode extracts opcode, register indices, and immediates; Execute performs the operation and updates registers, memory, or the PC. A pipelined processor overlaps these stages across consecutive instructions, introducing hazards that require forwarding, stalling, or flushing to resolve."
