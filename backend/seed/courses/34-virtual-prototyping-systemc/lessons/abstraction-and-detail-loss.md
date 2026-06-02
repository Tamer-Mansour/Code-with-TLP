# What Detail TLM Abstracts Away

TLM's speed advantage is not magic — it is a deliberate trade. Every nanosecond saved in simulation corresponds to something the model stopped tracking. Knowing exactly what TLM hides is critical: it tells you when TLM is enough and when you must drop to RTL.

## The Four Categories of Hidden Detail

### 1. Protocol Handshake Signals

Bus protocols like AXI, AHB, and Wishbone use handshake signals (`valid`/`ready`, `req`/`ack`, `strobe`) to coordinate senders and receivers. In RTL, those signals are wires that toggle every clock cycle. In TLM, the entire handshake is compressed into a function call.

What disappears:
- Individual `AWVALID`, `AWREADY`, `WVALID`, `WREADY`, `BVALID`, `BREADY` transitions.
- Back-pressure events when a slave is busy.
- Per-beat strobes (byte-enable masks per data beat).

What survives:
- Transfer direction (read/write).
- Address.
- Data bytes.
- Burst length (as data buffer size).
- Error/okay response status.

### 2. Bus Arbitration and Bandwidth Contention

Real bus interconnects arbitrate between multiple masters. When the CPU and DMA both want the bus simultaneously, one must wait. That wait introduces latency that affects software timing.

TLM models typically:
- Process transactions sequentially (one at a time per target port).
- Approximate contention with static latency values.
- Miss dynamic effects like priority inversion or starvation.

A full interconnect model that accurately captures multi-master contention requires AT-style TLM or custom arbitration logic, and even then it is an approximation.

### 3. Sub-Cycle Timing

RTL can distinguish events that happen at nanosecond granularity within a clock cycle: setup time, hold time, clock-to-output delay, combinational path depth. These affect whether the design meets timing closure.

TLM knows nothing about sub-cycle timing. Its minimum time unit is whatever `sc_time` resolution is set to — typically 1 ps or 1 ns — but that resolution is not connected to any propagation delay model. There is no concept of a critical path in TLM.

```cpp
// RTL: this captures a propagation delay
sc_signal<bool> out;
// ... out changes 2 ns after in due to gate delay in SDF model ...

// TLM: delays are manually annotated, not computed from logic depth
sc_core::sc_time delay(2, SC_NS);  // you chose this; it was not computed
```

### 4. Power and Switching Activity

Dynamic power is proportional to switching activity — how often wires toggle. RTL simulators can dump a Value Change Dump (VCD) file that records every signal transition. Power analysis tools (e.g., Synopsys PrimeTime PX) read VCDs to compute switching power.

TLM never toggles individual wires, so:
- No VCD signal activity is generated for bus signals.
- Power estimation from TLM requires separate analytical models.
- Clock gating effectiveness cannot be verified at TLM level.

## Summary Table

| Detail | RTL | TLM-AT | TLM-LT |
|---|---|---|---|
| Data correctness | Yes | Yes | Yes |
| Transfer size/direction | Yes | Yes | Yes |
| Approximate latency | Yes | Yes | Yes |
| Exact handshake cycles | Yes | Partial | No |
| Back-pressure dynamics | Yes | Partial | No |
| Bus arbitration | Yes | Partial | No |
| Sub-cycle propagation | Yes | No | No |
| Switching power activity | Yes | No | No |
| Glitch propagation | Yes | No | No |
| Scan chain testability | Yes | No | No |

## When Abstraction Goes Too Far

TLM models break down for:

- **EMC analysis** — electromagnetic compatibility requires actual switching waveforms.
- **Signal integrity** — crosstalk and impedance effects need physical-level signals.
- **Security side-channels** — power analysis attacks (DEMA, SPA) need switching activity.
- **DFT validation** — scan insertion and boundary scan require RTL signal access.
- **Coverage closure** — structural RTL coverage (toggle, branch) cannot be measured in TLM.

## The "Good Enough" Principle

TLM models are designed to be good enough for a specific purpose, not universally accurate. A TLM memory model is good enough to develop and validate a device driver. It is not good enough to verify memory timing margins.

The discipline of TLM modeling is knowing the purpose of your model and abstracting exactly as much as that purpose allows — no more, no less.

## Interview Answer

> "TLM abstracts away protocol handshake signals, bus arbitration dynamics, sub-cycle propagation delays, and switching power activity. Data values and functional behavior are preserved. This makes TLM unsuitable for timing closure, DFT validation, or power analysis, but ideal for software bring-up and architectural exploration."
