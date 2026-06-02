# ISA Simulators vs Cycle-Accurate Models

Two families of simulation dominate the virtual prototyping world: **ISA simulators** (also called functional simulators or emulators) and **cycle-accurate models**. Choosing between them — or knowing when to use both — is a core skill for any architecture or platform software engineer.

## ISA Simulators

An ISA simulator implements only the **programmer-visible state** defined by the architecture specification:

- General-purpose registers and CSRs
- Program counter
- Memory contents
- Exception and interrupt model

It executes one instruction at a time: fetch → decode → update registers/memory → advance PC. No pipeline stages, no cache model, no branch predictor. The result is extremely high simulation speed.

```python
# Simplified ISA simulator loop (RV32I)
def run(mem, regs, pc):
    while True:
        word = mem_read32(mem, pc)
        opcode = word & 0x7F
        if opcode == 0x33:          # R-type
            pc = exec_r_type(word, regs, pc)
        elif opcode == 0x03:        # Load
            pc = exec_load(word, regs, mem, pc)
        elif opcode == 0x6F:        # JAL
            pc = exec_jal(word, regs, pc)
        elif opcode == 0x73 and word == 0x00100073:  # EBREAK
            break
```

### Strengths of ISA simulators

- Simulation speed: hundreds of millions of instructions per second (MIPS).
- Fast bring-up: implement a new ISA extension in hours, not days.
- Ideal for running OS boots, running test suites, and generating golden reference traces.

### Weaknesses

- No timing information — cannot predict performance.
- Cache effects, pipeline stalls, and branch misprediction costs are invisible.
- DMA and device interaction may need special-casing because real timing does not apply.

## Cycle-Accurate Models

A cycle-accurate model advances simulation **one clock cycle at a time**. Every pipeline stage is modelled explicitly: fetch, decode, issue, execute, memory, write-back. Stalls, forwarding, speculative execution, and cache misses all affect the cycle count.

| Feature | ISA Simulator | Cycle-Accurate |
|---|---|---|
| Speed | 100-1000 MIPS | 1-10 MIPS |
| Timing accuracy | None | Exact |
| Cache model | Optional (functional) | Full (hit/miss/evict) |
| Branch predictor | Optional | Full (BTB, history) |
| Use case | SW dev, regression, golden ref | Perf analysis, micro-arch tuning |

### When cycle accuracy matters

- Measuring IPC (instructions per cycle) for a workload.
- Validating that a cache hierarchy meets latency targets.
- Tuning compiler flags for a specific pipeline.
- Comparing two micro-architecture configurations before committing to RTL.

## Execution-Driven vs. Trace-Driven

Both simulator types can be driven in two ways:

**Execution-driven**: the simulator fetches and executes instructions dynamically. This correctly models branch behaviour and data-dependent memory access patterns.

**Trace-driven**: a pre-recorded instruction trace is fed into the model. Faster and reproducible, but misses interactions between instructions because branches were already resolved when the trace was captured.

Most production simulators (gem5, Spike, QEMU) are execution-driven. Trace-driven is useful for cache and memory system studies.

## Mixed-Mode Simulation

Real-world flows often combine both. A common pattern:

1. Run a fast ISA simulator to boot Linux and reach the workload of interest (warm-up phase, billions of instructions).
2. Checkpoint the architectural state (register file, memory image).
3. Restore the checkpoint in a cycle-accurate model and simulate only the region of interest (millions of instructions).

This gives the accuracy of a cycle-accurate model at a fraction of the simulation time.

## Pitfall: Timing Assumptions in Firmware

Firmware that polls a timer or uses a busy-wait loop may behave differently on an ISA simulator (which runs at "infinite speed") versus real hardware. Always model peripheral timing even if you use a functional CPU model.

## Interview Answer

> "An ISA simulator implements only the architectural state and runs at hundreds of MIPS but gives no timing information. A cycle-accurate model clocks every pipeline stage and gives exact cycle counts at 1-10 MIPS. In practice, teams use ISA simulators for software development and regression testing, and cycle-accurate models for performance analysis."
