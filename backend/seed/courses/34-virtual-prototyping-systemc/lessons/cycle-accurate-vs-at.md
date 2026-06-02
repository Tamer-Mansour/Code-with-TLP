# Cycle-Accurate vs Approximately-Timed

Both cycle-accurate (CA) and approximately-timed (AT) models claim to include timing, yet they serve very different purposes. Understanding where the boundary lies prevents costly misuse of each approach.

## What "Cycle-Accurate" Actually Means

A cycle-accurate model advances simulation time in clock-cycle steps. Every signal transition, pipeline register, and handshake is modeled at clock granularity. This is usually written as synthesizable RTL (Verilog/VHDL) or as a hand-crafted C++ model that calls `wait(CLK.posedge_event())`.

```cpp
// Cycle-accurate bus master (SystemC, clocked)
void bus_master_thread() {
    while (true) {
        wait(clk.posedge_event());   // cycle boundary

        if (req_valid && req_ready) {
            // latch address on this clock edge
            bus_addr.write(pending_addr);
            req_valid.write(false);
        }
        wait(clk.posedge_event());   // next cycle
        // ... process response
    }
}
```

```cpp
// Approximately-timed equivalent — no clock, only time annotations
void at_initiator_thread() {
    tlm::tlm_phase phase = tlm::BEGIN_REQ;
    sc_core::sc_time t   = sc_core::SC_ZERO_TIME;

    // No clock event — time is annotated, not clocked
    socket->nb_transport_fw(trans, phase, t);
}
```

## Side-by-Side Comparison

| Dimension | Cycle-Accurate | Approximately-Timed (AT) |
|---|---|---|
| Time granularity | 1 clock cycle (e.g., 1 ns) | Arbitrary (e.g., 20 ns per phase) |
| Signal visibility | Every wire every cycle | None — only transaction events |
| Pipeline stages | Explicit (IF/ID/EX/MEM/WB) | Implicit (latency annotation) |
| Back-pressure | Signal-level (VALID/READY) | Phase-level (END_REQ timing) |
| Simulation speed | Slowest | Moderate |
| Verification use | RTL sign-off, gate-level timing | Perf estimation, SW/HW co-design |
| Typical abstraction | RTL or pin-accurate TLM | TLM-2.0 AT |

## What AT Captures That CA Does Not Simplify

AT deliberately hides signal-level detail. The four phases (BEGIN_REQ to END_RESP) correspond to events that span multiple clock cycles in real hardware. The annotated `sc_time` delay is an *estimate* of those cycles, not a cycle-by-cycle trace.

This is intentional: AT is tuned for **throughput and latency estimation**, not for verifying that a specific handshake pulse was two cycles wide.

## What CA Captures That AT Cannot

- **Bubble insertion** — a stall in pipeline stage 3 causes a two-cycle bubble; CA shows it, AT cannot.
- **Clock-domain crossings** — metastability windows and synchronizer latency are cycle-precise concepts.
- **Microarchitectural hazards** — data forwarding, load-use stalls, branch mis-prediction penalty.
- **Power-gating granularity** — a clock gate active for exactly three cycles saves a specific amount of energy; AT cannot model this.

## When to Use Which

```
Use cycle-accurate when:
  - RTL functional verification is the goal
  - Gate-level timing simulation (STA correlation)
  - Microarchitecture tuning (branch predictor, cache bank conflict)
  - Power estimation at switching-activity level

Use AT when:
  - System-level performance estimation early in design
  - Identifying memory subsystem bottlenecks before RTL exists
  - Running embedded software against a timed memory map
  - Architecture trade studies (cache size, bus width, frequency)
```

## The Bridge: Pin-Accurate TLM

Some projects use **pin-accurate TLM** — a TLM model that drives the same signal names as the RTL but uses the TLM scheduler instead of RTL simulation. This is faster than full RTL simulation but slower than pure AT. It enables mixed abstraction: an AT CPU talking to a pin-accurate memory controller.

## Cost vs. Benefit

Building a cycle-accurate model costs 5-10x more engineering effort than AT. RTL simulation runs 10-1000x slower than AT depending on design complexity. A practical flow is:

1. AT model for architecture exploration (weeks 1-12 of a project).
2. RTL delivered; pin-accurate or RTL model replaces AT subsystem.
3. Full RTL simulation for sign-off.

> **Interview answer:** "Cycle-accurate models advance simulation at every clock edge and capture individual pipeline stages and signal transitions. AT annotates transaction-level latencies without clock granularity — it estimates throughput and latency but cannot reproduce pipeline bubbles or signal-level timing."
