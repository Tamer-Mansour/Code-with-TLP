# The Speed vs Accuracy Tradeoff

Every virtual prototyping project lives on a curve: the more faithfully the model replicates hardware timing, the slower the simulation runs. Understanding this tradeoff — and knowing how to position your platform on the curve — separates good virtual-platform architects from great ones.

## The Fundamental Tension

A cycle-accurate model must track every clock edge, every pipeline stage, every bus arbitration cycle. That is potentially billions of state updates per simulated second. A functional model just needs to produce the right answer and can skip all that bookkeeping.

Typical simulation speeds by abstraction level:

| Abstraction | Simulation speed | Can boot Linux? |
|---|---|---|
| Untimed functional | 1 000 – 10 000 MIPS | Yes (seconds) |
| Loosely Timed (LT) | 100 – 1 000 MIPS | Yes (minutes) |
| Approximately Timed (AT) | 10 – 100 MIPS | Possible (hours) |
| Cycle-Accurate (CA) | 0.1 – 10 MIPS | Rarely practical |
| RTL gate-level | 0.001 – 0.1 MIPS | No |

MIPS = million target instructions simulated per host second.

## What You Actually Need

Ask these three questions before choosing a level:

1. **What bug are you hunting?** A timing-dependent DMA race needs AT. A driver correctness issue only needs UT or LT.
2. **How long can a simulation run take?** A CI regression suite that must finish overnight cannot use RTL.
3. **Who writes the model?** A cycle-accurate model takes 10–100× longer to develop than an LT model.

## Worked Example: Choosing the Right Level

Imagine you are validating a JPEG encoder accelerator peripheral and its firmware driver.

| Validation goal | Chosen level | Reasoning |
|---|---|---|
| Driver reads/writes correct registers | UT | No timing needed |
| DMA burst does not starve CPU | AT | Need bus bandwidth model |
| Accelerator pipeline produces correct output | CA | Pixel-level correctness at cycle boundary |

A single platform can include all three: the CPU runs LT while the accelerator uses CA with a protocol adapter in between.

## Temporal Decoupling

Temporal decoupling is the primary technique that keeps LT models fast. Instead of advancing simulation time after every instruction, the ISS runs a quantum of instructions (e.g., 1000 cycles) before calling `wait()`. This dramatically reduces context-switch overhead in the SystemC scheduler.

```cpp
// ISS inner loop with temporal decoupling
void Cpu::run() {
    tlm::tlm_quantumkeeper qk;
    qk.set_global_quantum(sc_time(1000, SC_NS)); // 1 µs quantum
    while (true) {
        execute_instruction(); // no wait() here
        qk.inc(sc_time(1, SC_NS)); // annotate time
        if (qk.need_sync()) {
            qk.sync(); // wait() only once per quantum
        }
    }
}
```

The cost: any event that happens within a quantum is not visible until the next sync point. This is acceptable if the quantum is shorter than the interrupt response time your SW cares about.

## The Accuracy Cliff

There is a non-linear accuracy drop as you loosen timing:

- Going from CA to AT loses pipeline-level detail but preserves bus-level contention — acceptable for most SW validation.
- Going from AT to LT loses back-pressure information — problematic if the SW relies on polling bus-busy status.
- Going from LT to UT loses all timing — fatal if any SW behaviour depends on timeouts or performance counters.

## Common Pitfalls

- **Premature accuracy** — Teams model peripherals at CA before the register interface is even stable. LT is almost always the right starting point.
- **Ignoring host machine speed** — A simulation that takes 48 hours defeats the purpose. Budget simulation time as carefully as hardware area.
- **Single quantum for the whole platform** — The global quantum must be small enough for the fastest interrupt service time, which can force a tight quantum even for slow peripherals.

## Interview Answer

> "The speed-vs-accuracy tradeoff is governed by how much timing bookkeeping the model must do. LT models annotate delays without blocking, achieving hundreds of MIPS; CA or RTL models track every cycle, collapsing to less than 10 MIPS. The right choice is the minimum accuracy needed to catch the bugs you care about — starting with LT and adding accuracy only where measurements show it is necessary."
