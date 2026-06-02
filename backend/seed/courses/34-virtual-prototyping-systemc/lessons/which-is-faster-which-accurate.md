# Which Is Faster, Which Is More Accurate?

The RTL vs TLM question is almost always framed as a trade-off between speed and accuracy. But this framing is subtly wrong. Speed and accuracy are not single dimensions — they have multiple facets, and RTL beats TLM on some while TLM beats RTL on others.

## Unpacking "Speed"

Speed has two meanings in simulation:

1. **Simulation throughput** — how many simulated clock cycles or nanoseconds per second of wall-clock time.
2. **Model development time** — how long it takes to write and debug the model.

TLM wins on simulation throughput by 10x–1000x. TLM also wins on development time: a TLM peripheral model takes days; its RTL equivalent takes weeks.

RTL wins on something simulation-adjacent: **design maturity speed**. An RTL implementation is closer to actual hardware, so discoveries made during RTL simulation are more actionable for physical design.

## Unpacking "Accuracy"

Accuracy also has multiple dimensions:

| Accuracy Type | RTL | TLM-AT | TLM-LT |
|---|---|---|---|
| Functional (does the right thing) | Yes | Yes | Yes |
| Cycle-accurate timing | Yes | Partial | No |
| Bus-pipeline behavior | Yes | Yes | No |
| Latency ordering | Yes | Yes | Approximate |
| Bit-width precision | Yes | Yes (payload) | Yes (payload) |
| Protocol compliance | Yes | Partial | No |
| Power switching | Yes | No | No |
| Timing margin analysis | Yes | No | No |

RTL is the only model type that is both **functionally and structurally** accurate. TLM is only **functionally** accurate. However, for the specific purpose of software development, functional accuracy is all that matters — the firmware does not care about switching activity.

## The Right Question

Instead of asking "which is more accurate?" ask: **"accurate enough for what purpose?"**

| Purpose | Minimum Accuracy Needed | Use |
|---|---|---|
| Boot firmware on a virtual platform | Functional + approximate latency | TLM-LT |
| Validate DMA interrupt timing | Functional + bus pipelining | TLM-AT |
| Find timing violations | Cycle-accurate | RTL |
| Run static timing analysis | Gate-level with SDF | Gate netlist |
| Estimate leakage power | Full transistor | SPICE |

Choosing a more accurate model than your purpose requires wastes simulation time. Choosing a less accurate model than your purpose requires produces wrong results.

## A Concrete Worked Example

**Scenario:** You are validating an SPI flash driver on a virtual platform.

The driver:
1. Sends a READ command byte.
2. Sends a 3-byte address.
3. Reads 256 data bytes.

**Using TLM-LT (Loosely Timed):**
- The SPI model accepts the command and address in one `b_transport()` call.
- Returns 256 bytes with a 200 µs annotated delay (approximated from datasheet).
- The driver's read loop runs correctly.
- Simulation time: milliseconds.

**Using RTL SPI:**
- 32 SPI clock edges per byte × 260 bytes = 8320 clock edges.
- Plus MOSI/MISO signal transitions, CS assertion, etc.
- The driver's read loop still runs correctly.
- Simulation time: seconds to minutes for this one transfer.

The driver is equally valid in both cases. The RTL simulation tells you clock-edge timing; the TLM simulation does not. For driver validation, you did not need that clock-edge timing.

## When RTL Is Definitively Better

There is no substitute for RTL when:

- You need to sign off on **functional coverage** at the signal level.
- You are running **formal equivalence checking** between RTL and a reference.
- You are debugging a **hardware race condition** that only manifests as specific signal overlap.
- You need to verify **reset behavior** at the bit level.

## When TLM Is Definitively Better

There is no substitute for TLM when:

- You need to boot a full **operating system** before RTL exists.
- You are exploring **10+ architectural configurations** in a week.
- You are running **software regression suites** daily against a platform model.
- The team writing the firmware is a different group from the hardware team and needs a stable API today.

## Speed-Accuracy Summary

```
Speed (simulation throughput)
High ──────────────────────────────── Low
TLM-LT  TLM-AT  RTL-behav  RTL-gate  SPICE

Accuracy (all dimensions combined)
Low ────────────────────────────────── High
TLM-LT  TLM-AT  RTL-behav  RTL-gate  SPICE
```

The curves are monotone: more accuracy costs more simulation time. The engineering challenge is picking the right point on this curve for each task.

## Interview Answer

> "TLM is faster by 10x–1000x in simulation throughput and also faster to write. RTL is more accurate for timing, power, and protocol compliance. The correct choice depends on purpose: TLM suffices for software development and architectural exploration; RTL is required for timing closure, formal verification, and power sign-off. Both are used in parallel during a real design flow."
