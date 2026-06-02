# Why TLM Is Faster than RTL

The speed gap between TLM and RTL simulation is not a matter of degree — it is often a matter of kind. A TLM model can simulate a full second of system activity in minutes; the equivalent RTL might take weeks. Understanding the root cause of this difference makes you a better architect and a better debugger.

## Root Cause 1: Fewer Simulation Events

SystemC (and VHDL/Verilog) simulators are event-driven. Every signal change is an event. Every event triggers re-evaluation of all sensitive processes. More events mean more CPU work.

A single AXI4 memory read at 100 MHz might generate:

| Protocol Phase | Approximate Event Count (RTL) |
|---|---|
| Address channel handshake | 6–10 events |
| Per-beat data handshake (8 beats) | ~40 events |
| Response channel | 4–6 events |
| Clock edges sampled | 20–30 events |
| **Total** | **~70–90 events** |

The equivalent TLM `b_transport()` call: **1 event** (the process activation when the call returns and `wait(delay)` elapses).

At 10 million transactions per simulated second, that is 700–900 million events saved per second of simulated time.

## Root Cause 2: No Clock in the Hot Path

RTL simulators must process clock edges. A 1 GHz design has 10^9 clock events per simulated second. Even with techniques like cycle-skipping, the clock is the dominant event source in large RTL simulations.

TLM uses `sc_time` annotations rather than clocks. A 10 ns delay is stored as a number and consumed in one `wait()` call. There is no per-nanosecond event; the simulator jumps directly to the next event timestamp.

```cpp
// RTL: 1000 clock events to advance 1 µs at 1 GHz
for (int i = 0; i < 1000; ++i)
    wait(clk.posedge_event());

// TLM: 1 event to advance 1 µs
wait(sc_time(1, SC_US));
```

## Root Cause 3: Quantum-Based Time Advancement

TLM-2.0 Loosely Timed models use a **time quantum** (also called a global time quantum, GTQ). Instead of synchronizing simulation time after every transaction, initiators accumulate local time and only sync with the global simulation time at quantum boundaries.

```cpp
// Quantum keeper usage in an initiator
tlm_utils::tlm_quantumkeeper qk;
qk.set_global_quantum(sc_time(1, SC_US));  // 1 µs quantum

while (true) {
    socket->b_transport(trans, delay);
    qk.inc(delay);
    if (qk.need_sync()) qk.sync();  // only sync every ~1 µs
    // otherwise: keep running without touching global time
}
```

Without the quantum keeper, every transaction would require a `wait()` that suspends the current process and potentially activates others. With it, hundreds of transactions can execute in a single scheduling round.

## Root Cause 4: No Bit-Level Signal Evaluation

In RTL, signal widths matter. An `sc_uint<64>` changing value triggers evaluation of every process sensitive to that signal. The simulator must compare old and new values at the bit level, propagate the event, and schedule all sensitive processes.

In TLM, data lives in a byte-array buffer inside `tlm_generic_payload`. It is just memory. There are no sensitive processes watching individual bytes. The target reads the buffer when called, not when it changes.

## Quantitative Example

Consider simulating a simple CPU booting Linux:

| Model Type | Simulated Time | Wall-Clock Time |
|---|---|---|
| RTL (gate-level) | 1 second | ~3–6 months |
| RTL (register-transfer) | 1 second | ~1–4 weeks |
| TLM Approximately Timed | 1 second | ~2–8 hours |
| TLM Loosely Timed | 1 second | ~5–30 minutes |
| ISS (instruction set sim) | 1 second | ~1–10 minutes |

These are industry-typical figures. The improvement from RTL to TLM is 10x to 1000x depending on design complexity.

## What You Pay for This Speed

Speed comes from information loss. TLM cannot tell you:

- Exactly which cycle a signal glitched.
- Whether a bus pipeline stall actually occurred.
- The peak switching current of the bus.

Every optimization that makes TLM faster removes some observable detail. The art of TLM modeling is choosing which details to keep (delays, error responses, out-of-order responses) and which to discard (handshake signals, bus arbitration cycles, glitch propagation).

## Common Pitfall

Using `SC_ZERO_TIME` for all delays makes TLM faster still — but meaningless for performance analysis. A zero-delay model can tell you software is functionally correct, but it cannot tell you whether the design meets its throughput target.

## Interview Answer

> "TLM is faster because it replaces hundreds of clock-driven signal events per transaction with a single function call and a time annotation. Three mechanisms compound this speedup: fewer simulation events, quantum-based time advancement that avoids per-transaction scheduling, and the absence of bit-level signal evaluation. The tradeoff is that wire-level timing detail is lost."
