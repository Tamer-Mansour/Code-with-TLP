# Approximately-Timed (AT) Coding Style

The **Approximately-Timed (AT)** coding style is TLM-2.0's middle ground between the simplicity of LT and the full accuracy of RTL simulation. It models bus protocol phases explicitly, allowing the initiator and target to overlap work — just as real hardware pipelines transactions.

## The Phase-Based Protocol

AT uses `nb_transport_fw` (initiator-to-target) and `nb_transport_bw` (target-to-initiator) — the non-blocking transport interface. A transaction progresses through four standard phases:

```
BEGIN_REQ  →  END_REQ  →  BEGIN_RESP  →  END_RESP
```

Each side calls its transport function and returns a **return status** that tells the other side what to do next:

| Return Value | Meaning |
|---|---|
| `TLM_ACCEPTED` | Handshake continues; expect a callback |
| `TLM_UPDATED` | Phase and/or delay modified; act on them |
| `TLM_COMPLETED` | Transaction done; no callback needed |

## Initiator Example

```cpp
// Initiator nb_transport_fw call
tlm::tlm_sync_enum status;
tlm::tlm_phase phase = tlm::BEGIN_REQ;
sc_core::sc_time  t   = sc_core::SC_ZERO_TIME;

status = socket->nb_transport_fw(trans, phase, t);

if (status == tlm::TLM_UPDATED) {
    // Target advanced the phase — check what changed
    if (phase == tlm::END_REQ) {
        // Request accepted; wait for response via nb_transport_bw callback
    }
} else if (status == tlm::TLM_COMPLETED) {
    // Target collapsed the protocol — transaction done in one call
    wait(t);   // honor annotated completion time
}
```

## Target Example

```cpp
tlm::tlm_sync_enum nb_transport_fw(tlm::tlm_generic_payload& trans,
                                   tlm::tlm_phase& phase,
                                   sc_core::sc_time& t) {
    if (phase == tlm::BEGIN_REQ) {
        // Accept request; schedule response after 20 ns
        phase = tlm::END_REQ;
        t     = sc_core::sc_time(20, SC_NS);

        // Queue the transaction internally for later response
        pending_trans = &trans;

        // Spawn a thread or use an event to send the response
        response_event.notify(t);

        return tlm::TLM_UPDATED;   // tell initiator: phase changed
    }
    // Handle END_RESP acknowledgment from initiator
    if (phase == tlm::END_RESP) {
        return tlm::TLM_COMPLETED;
    }
    SC_REPORT_FATAL("AT target", "Unexpected phase");
    return tlm::TLM_ACCEPTED;
}
```

## Key Characteristics

| Feature | AT Behavior |
|---|---|
| Transport API | `nb_transport_fw` / `nb_transport_bw` |
| Timing | Explicit annotated delays per phase |
| Phase protocol | BEGIN_REQ, END_REQ, BEGIN_RESP, END_RESP |
| Simulation speed | Moderate (more context switches than LT) |
| Timing accuracy | Moderate — captures pipeline overlap |
| Typical use | Performance analysis, interconnect modeling |

## Why AT Matters for Performance Modeling

In AT, the initiator can issue the next request as soon as `END_REQ` is received, without waiting for the response. This models **pipelined buses** (like AXI) where outstanding transactions overlap. A memory controller with four outstanding reads will show different throughput in AT vs LT — AT captures the pipeline, LT cannot.

## Common Pitfalls

- **Storing the payload pointer beyond its lifetime** — in AT, the initiator owns the payload until `END_RESP`; the target must not delete or reuse it.
- **Forgetting the backward path** — the initiator must implement `nb_transport_bw` to receive the response callback, or the simulation deadlocks.
- **Ignoring return values** — discarding `TLM_UPDATED` means the initiator misses a phase change and the protocol stalls.

## Collapsed Protocol (Fast AT)

When a target can complete a transaction immediately (e.g., a small SRAM with zero wait), it returns `TLM_COMPLETED` from `BEGIN_REQ` without going through all four phases. This "collapsed AT" is faster than full AT while still using the non-blocking interface.

> **Interview answer:** "AT uses `nb_transport` with explicit phases (BEGIN_REQ to END_RESP) and return codes. It models pipelined bus behavior — the initiator can overlap requests and responses — giving better timing accuracy than LT with less overhead than RTL simulation."
