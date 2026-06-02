# Abstraction Levels: Functional to Cycle-Accurate

Choosing the right abstraction level is the single most important architectural decision in a virtual prototyping project. Too abstract and timing bugs slip through to silicon; too detailed and simulation speed collapses. The TLM-2.0 standard formalises the spectrum with defined coding styles.

## The Abstraction Spectrum

```
High abstraction (fast)
        |
        v
  Functional / Untimed (UT)
  Loosely Timed (LT)
  Approximately Timed (AT)
  Cycle-Accurate (CA) / RTL
        |
        v
Low abstraction (accurate)
```

Each level trades simulation speed for timing fidelity.

## Untimed / Functional Models

The model computes correct data output but carries no concept of time. A function call returns a result immediately with zero simulated time passing.

```cpp
// Untimed AES block — correct data, zero timing
void aes_encrypt_ut(const uint8_t* in, uint8_t* out, const uint8_t* key) {
    // ... correct AES logic ...
    // no wait(), no sc_time annotation
}
```

**Use case:** Early algorithm validation, software development where only correctness matters.

## Loosely Timed (LT) — The TLM-2.0 Sweet Spot

Each transaction carries a `sc_time` annotation. The initiator (ISS) adds the transport delay before calling `b_transport()`. The target does not block; simulation time advances in large chunks, keeping simulation fast.

```cpp
// Initiator side: LT style
void do_read(uint64_t addr, uint8_t* data) {
    tlm::tlm_generic_payload trans;
    sc_core::sc_time delay = sc_core::sc_time(10, sc_core::SC_NS); // annotate
    trans.set_address(addr);
    trans.set_command(tlm::TLM_READ_COMMAND);
    trans.set_data_ptr(data);
    socket->b_transport(trans, delay); // non-blocking in simulation time
    wait(delay);                       // consume annotated time
}
```

LT models typically achieve 100 MIPS–1000 MIPS simulation throughput, fast enough to boot Linux.

## Approximately Timed (AT)

AT models use the four-phase `nb_transport` protocol to model pipelined buses accurately. Requests and responses are separate events, allowing back-pressure and out-of-order completion.

| Phase | Meaning |
|---|---|
| `BEGIN_REQ` | Initiator puts request on bus |
| `END_REQ` | Target accepts request (bus is free) |
| `BEGIN_RESP` | Target sends response |
| `END_RESP` | Initiator accepts response |

**Use case:** Bus contention analysis, DMA performance, memory controller tuning.

## Cycle-Accurate (CA) and RTL

Every operation takes an exact integer number of clock cycles. Usually implies RTL (VHDL/Verilog/SystemVerilog) or pin-accurate SystemC. Simulation speed: single-digit MIPS or slower.

**Use case:** Pre-silicon sign-off, gate-level simulation, timing closure.

## Mixing Levels in One Platform

A real SoC virtual platform typically mixes levels:

| Subsystem | Abstraction | Reason |
|---|---|---|
| Main CPU ISS | LT | Boot Linux quickly |
| DMA controller | AT | Model bandwidth contention |
| Custom accelerator | CA or RTL | Validate micro-architecture |
| UART / GPIO | UT | SW doesn't care about UART timing |

The TLM-2.0 `tlm_quantumkeeper` and temporal decoupling helpers let LT and AT models share the same `sc_start()` loop without explicit barriers at every transaction.

## Worked Example: Moving from UT to LT

```cpp
// UT version — instant response
void Memory::b_transport_ut(tlm_generic_payload& t, sc_time& delay) {
    do_mem_op(t);
    delay = SC_ZERO_TIME;  // no timing
}

// LT version — annotated latency
void Memory::b_transport_lt(tlm_generic_payload& t, sc_time& delay) {
    do_mem_op(t);
    delay += sc_time(DRAM_LATENCY_NS, SC_NS); // caller waits after return
}
```

The only change is the `delay` annotation. The data path is identical; the timing model is now present.

## Common Pitfalls

- **Mixed LT/AT without adapters** — Connecting an LT initiator directly to an AT target requires a `tlm_bus_width_adapter` or protocol converter; otherwise simulation hangs waiting for a `BEGIN_REQ` that never arrives.
- **Ignoring quantum** — In LT models, the quantum (time slice) must be smaller than the shortest observable hardware event, or SW misses interrupts.

## Interview Answer

> "TLM-2.0 defines a spectrum from untimed functional models (fast, no timing) through loosely timed (annotated delays, 100–1000 MIPS) and approximately timed (4-phase pipelined bus) to cycle-accurate RTL (exact cycles, slow). A virtual platform typically mixes levels, using LT for the CPU and more accurate models only for the subsystems being validated."
