# Cycle-Accurate Models Revisited

A **cycle-accurate model** advances simulation time in steps equal to one clock cycle and captures the exact microarchitectural state (pipeline registers, stall signals, bypass muxes) at every edge. This section revisits the concept with fresh eyes now that you have full TLM and VP context, so you can explain the trade-offs sharply in an interview.

## What "Cycle-Accurate" Really Means

Cycle accuracy has two orthogonal axes:

| Axis | What it guarantees | What it does NOT guarantee |
|------|-------------------|---------------------------|
| **Timing** | Correct behavior at every clock edge | Correct gate delay within the cycle |
| **Microarchitecture** | Every pipeline state matches RTL | Transistor-level currents |

A model can be cycle-accurate in timing but still behavioral (no gate-level detail). RTL simulation in Verilog/VHDL is the canonical cycle-accurate reference; a hand-written C++ ISS can also be cycle-accurate without being RTL.

## Why Cycle Accuracy Was Invented

Early processor architects needed to count stalls, branch penalties, and cache misses before tape-out. Functional simulation was too abstract (no timing), and gate-level simulation was too slow. Cycle-accurate C++ models (e.g., SimpleScalar in the 1990s) filled the gap.

## The Spectrum from Functional to Cycle-Accurate

```
Functional ISS        Approximately-timed TLM      Cycle-accurate RTL
     |                          |                          |
  No timing              Loosely timed             Exact edge timing
  Max speed             10–100× faster than RTL    Ground truth
  SW dev only           SW + perf. estimation      Signoff, DV
```

At the left end, an ISS like QEMU executes billions of instructions per second. At the right end, RTL simulation in ModelSim runs perhaps 1–10 MHz of simulated clock. Cycle-accurate C++ ISS models sit in between, giving accurate stall counts at speeds 10–100× faster than RTL.

## A Minimal Cycle-Accurate Pipeline Skeleton

```cpp
// Simplified 5-stage in-order pipeline tick
void Pipeline::tick() {
    writeback();   // WB reads from MEM output latch
    memory();      // MEM reads from EX output latch
    execute();     // EX reads from ID output latch
    decode();      // ID reads from IF output latch
    fetch();       // IF updates IF output latch
    // Advance simulation time by one clock cycle
    sc_core::wait(CLK_PERIOD, sc_core::SC_NS);
}
```

The key discipline: each stage reads from the **previous** cycle's latch and writes to its **own** latch. Stalls are modelled by suppressing latch updates and inserting bubbles.

## Pitfalls Engineers Miss

- **Data hazard vs. control hazard stalls** — missing one category makes IPC estimates wrong.
- **Memory latency mismatch** — using a fixed 1-cycle DRAM model inflates performance; parameterize it.
- **Forgetting branch misprediction flush** — functional models often skip the flush, but performance models must count it.

## Cycle Accuracy in the Context of VPs

Virtual Prototypes are almost never cycle-accurate for the full SoC. A typical mixed-fidelity VP is:

- **Approximately-timed TLM** for interconnect and peripherals (fast, good enough for SW)
- **Cycle-accurate submodel** for a single IP (e.g., GPU shader core) where perf. sensitivity matters

This hybrid lets architects make informed trade-offs without paying the full RTL simulation cost.

## Interview Answer

> "A cycle-accurate model captures the exact microarchitectural state at every clock edge — pipeline latches, stalls, and bypasses — matching RTL behavior. VPs usually use approximately-timed TLM instead, accepting some timing imprecision for 10–100× simulation speed gain. Cycle-accurate submodels are added only where performance sensitivity justifies the cost."
