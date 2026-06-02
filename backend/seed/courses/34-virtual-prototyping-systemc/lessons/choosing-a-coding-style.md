# Choosing a Coding Style for a Use Case

Selecting the right TLM coding style at the start of a project determines simulation speed, modeling effort, and the quality of insights you can extract. This lesson provides a practical decision framework.

## The Three-Question Filter

Answer these three questions in order:

1. **Do I need timing at all?** If the goal is purely functional verification (does the software produce correct outputs?), use LT with zero-delay targets. Timing can always be added later.
2. **Do I need pipeline overlap?** If the bus or memory controller uses pipelining (multiple outstanding transactions), LT cannot represent this — choose AT.
3. **Do I need clock-cycle accuracy?** If the answer is yes (RTL sign-off, DFT, power grid analysis), TLM is the wrong abstraction entirely — use RTL simulation.

## Decision Table

| Use Case | Recommended Style | Reason |
|---|---|---|
| OS boot / software bring-up | LT (zero-delay or minimal annotation) | 10M+ transactions; speed is critical |
| Functional regression testing | LT | Binary pass/fail; no timing needed |
| Cache performance analysis | AT | Outstanding misses overlap; pipeline matters |
| DRAM controller bandwidth study | AT | Many outstanding transactions, back-pressure |
| Interrupt latency measurement | LT with small quantum | End-to-end latency, not pipeline detail |
| SoC architecture trade study | AT (key paths) + LT (peripherals) | Accuracy where needed, speed elsewhere |
| RTL integration testing | Pin-accurate / RTL co-sim | Must match real waveforms |
| Power estimation | Cycle-accurate or annotated RTL | Need switching activity counts |

## Mixed-Style Systems

Real SoC virtual prototypes almost always combine styles:
- **CPU cores** — LT with temporal decoupling (fastest for instruction-fetch and data-access)
- **High-bandwidth interconnect (NOC, AXI)** — AT to capture pipeline and routing latency
- **Slow peripherals (UART, SPI, GPIO)** — LT zero-delay or simple wait-state model
- **Memory controllers (DDR, HBM)** — AT or a dedicated timing model

Protocol adapters bridge the styles at boundary sockets.

## Time-to-Model Estimates

| Style | Lines of code (simple target) | Engineer-days (subsystem) |
|---|---|---|
| LT zero-delay | ~30 | 0.5 |
| LT with annotation | ~50 | 1 |
| AT (collapsed protocol) | ~80 | 2 |
| AT (full four-phase) | ~150 | 5 |
| Cycle-accurate TLM | ~500+ | 15+ |

These estimates highlight the productivity advantage of LT. Starting with LT and incrementally adding AT where measurements demand it is the standard industrial practice.

## Pitfall: Over-Engineering Early

A common mistake is building a full AT model — including pipelined outstanding transactions and back-pressure — before there is any evidence that pipeline timing matters for the software being developed. The result is a slow, complex model that answers a question nobody has asked yet.

**Start simple, profile, then add fidelity where the numbers show it matters.**

## Pitfall: Under-Engineering Late

Equally common is keeping a zero-delay LT model too long. When the SoC team needs to tune DDR rank interleaving or measure the effect of adding a second memory channel, a zero-delay LT model gives the same answer for every configuration — useless for architectural comparison.

## Practical Checklist

- [ ] Identify the primary consumer of the virtual prototype (software team vs. hardware performance team).
- [ ] List the bus and memory interfaces that dominate bandwidth.
- [ ] Prototype with LT first; measure simulation speed.
- [ ] Replace bottleneck interfaces with AT only if performance results are needed.
- [ ] Set the global quantum based on the smallest interrupt latency requirement.
- [ ] Document the chosen style per module in the platform specification.

> **Interview answer:** "The choice depends on whether pipeline overlap matters and whether timing accuracy affects the answer. LT is correct for software bring-up where speed dominates; AT is correct when pipelined buses or bandwidth bottlenecks must be captured. Start with LT, add AT where profiling shows it matters."
