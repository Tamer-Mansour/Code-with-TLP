# ISS vs Cycle-Accurate CPU Models

Choosing the right level of CPU model accuracy is one of the most consequential decisions in virtual-prototype design. The trade-off is always the same: simulation speed vs. timing fidelity. Understanding where each model type belongs in a project saves months of wasted effort.

## Two Poles of the Accuracy Spectrum

### Instruction-Set Simulator (ISS)

An ISS models the **instruction-set architecture** — the contract between software and hardware. It executes one instruction at a time, updating the architectural state (registers, PC, flags) exactly as the ISA manual specifies. It makes no claims about *when* execution happens in real time or how many clock cycles an instruction consumes.

Typical ISS characteristics:

- Speed: **100–1000+ MIPS** (millions of simulated instructions per second) on a modern workstation.
- Accuracy: Functional only — correct register values, correct memory side effects.
- Use: Software development, firmware validation, OS bring-up, regression testing.
- Examples: QEMU, Spike (RISC-V), OVPsim, gem5 in fast-forward mode.

### Cycle-Accurate Model (CA Model)

A cycle-accurate model simulates the **microarchitecture** — pipeline stages, cache hierarchy, branch predictor, execution units, memory latencies — on a cycle-by-cycle basis. Every event is timestamped to a specific clock cycle.

Typical CA model characteristics:

- Speed: **1–10 MIPS** at best, often far slower for complex out-of-order cores.
- Accuracy: Timing-accurate — you can measure IPC (instructions per cycle), cache miss rates, pipeline stalls.
- Use: Performance analysis, cache sizing, power estimation, Design Space Exploration (DSE).
- Examples: gem5 with detailed CPU model, Synopsys Virtualizer with timing annotations, SystemC TLM-2.0 with temporal decoupling tuned to cycle level.

## Comparison Table

| Property | ISS | Cycle-Accurate |
|---|---|---|
| Simulation speed | Very high (100–1000 MIPS) | Low (0.1–10 MIPS) |
| Timing fidelity | None | Cycle-level |
| Memory latency modeled | No (or approximate) | Yes |
| Pipeline stalls | No | Yes |
| Cache effects | No (or statistical) | Yes |
| Interrupt timing | Approximate | Exact |
| Bring-up suitability | Excellent | Poor |
| Performance analysis | No | Yes |
| Model complexity | Low | Very high |

## Where Each Lives in a Project Timeline

```
[Early SW dev] --> ISS at MAX speed
[Platform integration] --> ISS + approximate bus timing (LT TLM)
[Performance budgeting] --> ISS + cache model (loosely-timed)
[Microarch DSE] --> Cycle-accurate or RTL co-sim
[Tape-out sign-off] --> RTL simulation
```

A common pattern in industrial platforms is to start with a **loosely-timed (LT) ISS** wrapped in TLM-2.0, then replace it with a **ca-ISS** (a hybrid that is cycle-approximate, not cycle-accurate) once enough software is running to drive meaningful performance scenarios.

## Temporal Decoupling and Quantum

Even within the ISS world, simulation speed is tuned with **temporal decoupling**: the ISS runs ahead of SystemC simulation time by a fixed quantum (e.g., 1 ms of simulated time). It only synchronizes with the bus at quantum boundaries. Larger quanta = faster simulation, less accurate interrupt timing.

```cpp
// Loosely-timed ISS main loop (conceptual)
while (!done) {
    sc_time quantum = tlm_global_quantum::instance().get();
    sc_time local_time = SC_ZERO_TIME;

    while (local_time < quantum) {
        uint32_t instr = fetch_and_execute(); // fast path
        local_time += sc_time(CYCLE_NS, SC_NS); // notional time
    }
    wait(quantum); // yield to SystemC scheduler
}
```

## The "ca-ISS" Middle Ground

Many modern tools offer a **ca-ISS** (cycle-approximate ISS): it is still instruction-accurate but annotates each instruction with an approximate cycle count drawn from a timing model or a lookup table. This gives 5–20x the performance of a full cycle-accurate model while capturing first-order pipeline and memory-latency effects.

## Common Pitfalls

- **Choosing CA too early**: Brings the whole team to a halt waiting for simulations that take hours. Always start with an ISS.
- **Treating ISS timing as real**: An ISS that completes in 10 ms of simulation time tells you nothing about whether your RTOS deadline will be met on the real chip.
- **Forgetting interrupt latency**: An ISS may deliver interrupts between any two instructions; a CA model must deliver them at the correct pipeline stage.

## Interview Answer

> "An ISS executes instructions functionally — it is fast enough to boot Linux in seconds but carries no cycle timing. A cycle-accurate model simulates every pipeline stage and cache access, so it can measure IPC and memory latency but runs 100x–1000x slower. In practice you use an ISS for software bring-up and switch to a cycle-accurate model only when you need performance data."
