# Limitations of Virtual Prototypes

Virtual prototypes are powerful, but they are not magic. Over-relying on a VP without understanding its limitations leads to false confidence and expensive late-stage surprises. A skilled embedded engineer knows exactly where the VP stops being trustworthy and real hardware becomes mandatory.

## 1. Timing Accuracy Is Approximate

TLM-2.0 models operate at the **loosely timed (LT)** or **approximately timed (AT)** abstraction level. Neither reproduces cycle-exact latencies.

| What the VP can tell you | What the VP cannot tell you |
|---|---|
| A DMA transfer moves 1 MB correctly | How many nanoseconds it takes on real silicon |
| An interrupt is routed to the CPU | Whether interrupt latency meets a hard real-time deadline |
| A peripheral responds to a register write | The exact propagation delay through the bus fabric |

**Pitfall:** A firmware engineer tunes a timing loop on the VP and assumes it will work on hardware. It does not — because the VP runs 10x slower than real silicon or uses a simplified timing model.

```cpp
// This delay is meaningless on a VP; calibrate only on real hardware
void delay_us(uint32_t us) {
    volatile uint32_t count = us * CYCLES_PER_US; // CYCLES_PER_US is hardware-specific
    while (count--) {}
}
```

## 2. No Analog or Mixed-Signal Modeling

Virtual prototypes model digital logic. Analog components — PLLs, ADCs, DACs, voltage regulators, RF front-ends — are either absent or replaced with simplified behavioral stubs.

- A PLL model might simply output a fixed frequency; it cannot model lock time, VCO noise, or supply sensitivity.
- An ADC model returns programmed values; it cannot model quantization noise, offset error, or gain drift.

Consequences: audio quality, RF sensitivity, power rail stability, and sensor accuracy must all be validated on real hardware or in dedicated analog simulation.

## 3. No Physical / Electrical Behavior

The VP cannot model:

- **EMC/EMI** — radiated or conducted emissions
- **Signal integrity** — ringing, crosstalk, impedance mismatches
- **Thermal behavior** — junction temperature, thermal throttling triggers
- **ESD events** — latch-up, breakdown
- **Mechanical stress** — vibration, shock, connector wear

Any hardware qualification that involves physical measurements is outside the VP's scope by definition.

## 4. Model Accuracy Depends on Model Quality

A VP is only as accurate as the model written for it. If the UART model has a bug where parity errors are never reported, firmware written on the VP will fail on real hardware where parity errors do occur.

**Model bugs are silent failures** — the VP appears to work, but it is modeling wrong behavior. Unlike RTL, VPs typically do not have the same level of hardware verification applied to them.

```
[Incorrect VP model] → [Firmware passes VP tests] → [Firmware fails on silicon]
                                                           ^
                                               Expensive and late to discover
```

## 5. Model Development Cost and Maintenance Burden

Building a high-quality VP is not free. For a complex SoC, the model development effort can be 6–18 months of dedicated engineering time. Keeping the VP synchronized with a rapidly evolving hardware specification requires ongoing investment.

| Risk | Impact |
|---|---|
| VP team is under-resourced | VP is late; software start is not shifted left |
| VP not updated when HW spec changes | Software written to wrong spec |
| VP accuracy not validated against RTL | Silent model bugs accumulate |

## 6. Cannot Replace Hardware Bring-Up

No matter how good the VP, the first time a new board powers on is always an adventure. Real bring-up involves:

- Power rail sequencing and margining
- Clock bring-up and PLL lock verification
- DDR calibration and training
- Thermal management and power validation

None of these are modeled in a typical VP.

## 7. Performance Numbers Are Not Transferable

Benchmarks run on the VP — DHRYSTONE, CoreMark, memory bandwidth — do not predict real-silicon performance. The VP's simulation speed depends on the host machine, not on the target chip's microarchitecture.

> **Interview Answer:** "The main limitations of VPs are: approximate timing (not cycle-accurate), no analog behavior, model accuracy depending on model quality, and the inability to replace physical bring-up and performance validation."

## 8. Software Written Only Against a VP May Have Hidden Assumptions

If a driver is developed exclusively on a VP and never tested on a real bus with real electrical characteristics, it may have:

- Assumptions about bus ordering that the VP enforces but real hardware does not
- Missing memory barriers (DMB/DSB instructions) that the VP ignores because it is single-threaded
- Polling loops that work on the VP's simplified timing but spin forever on real hardware

## Mitigation Strategies

- **Validate VP models against RTL or silicon early and often.** Run the same test suite on both and compare.
- **Use coverage-driven model testing** — treat VP models as software and test them.
- **Document what the VP does and does not model** clearly in the model README.
- **Run critical timing tests on real hardware** as soon as first silicon is available.
- **Use memory barrier analysis tools** (sanitizers, formal verification) to catch barrier bugs early.
