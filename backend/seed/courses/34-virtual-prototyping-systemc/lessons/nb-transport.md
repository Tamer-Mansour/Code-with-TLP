# Non-Blocking Transport: nb_transport

Where `b_transport` completes a transaction in a single call, `nb_transport` breaks it into asynchronous phases. This models the pipelined, overlapping nature of real buses — an initiator can issue a new address phase while the data phase of the previous transaction is still in flight. This is the Approximately-Timed (AT) modeling style.

## The Two Directions

```cpp
// Forward path: initiator → target
virtual tlm_sync_enum nb_transport_fw(tlm_generic_payload& trans,
                                      tlm_phase&           phase,
                                      sc_core::sc_time&    t) = 0;

// Backward path: target → initiator
virtual tlm_sync_enum nb_transport_bw(tlm_generic_payload& trans,
                                      tlm_phase&           phase,
                                      sc_core::sc_time&    t) = 0;
```

- **`nb_transport_fw`** is called by the initiator to push a transaction forward (begin request, data phase, etc.).
- **`nb_transport_bw`** is called by the target to push a response backward (begin response, end response).

## Phases

TLM-2.0 defines four standard phases:

| Phase Constant | Meaning |
|---|---|
| `BEGIN_REQ` | Initiator starts a new request |
| `END_REQ` | Target signals it has accepted the request (address sampled) |
| `BEGIN_RESP` | Target starts the response (data valid) |
| `END_RESP` | Initiator acknowledges end of response |

Custom phases can be added for protocol extensions, but compliant AT models must handle the four standard ones.

## Return Values: `tlm_sync_enum`

| Value | Meaning |
|---|---|
| `TLM_ACCEPTED` | Callee accepts the phase; nothing more happens until the next call |
| `TLM_UPDATED` | Callee has already advanced the phase; no separate callback needed |
| `TLM_COMPLETED` | Transaction is fully done; no further phases |

## A Minimal 4-Phase AT Handshake

```
Initiator                        Target
   |-- nb_transport_fw(BEGIN_REQ) -->|
   |<-- TLM_ACCEPTED                 |
   |                                 | (target processes request)
   |<-- nb_transport_bw(END_REQ)  ---|
   |-- TLM_ACCEPTED ->               |
   |                                 | (target prepares data)
   |<-- nb_transport_bw(BEGIN_RESP) -|
   |-- TLM_ACCEPTED ->               |
   | (initiator consumes data)       |
   |-- nb_transport_fw(END_RESP)  -->|
   |<-- TLM_COMPLETED                |
```

## Initiator Code Sketch

```cpp
void Cpu::thread() {
    tlm::tlm_generic_payload* trans = new tlm::tlm_generic_payload;
    tlm::tlm_phase  phase = tlm::BEGIN_REQ;
    sc_core::sc_time t = sc_core::SC_ZERO_TIME;

    // ... fill trans fields ...

    tlm::tlm_sync_enum status = socket->nb_transport_fw(*trans, phase, t);

    if (status == tlm::TLM_UPDATED) {
        // Target already advanced phase; handle inline
    } else if (status == tlm::TLM_COMPLETED) {
        // Transaction done immediately (single-cycle target)
    } else {
        // TLM_ACCEPTED: wait for backward callback
        wait(response_event);
    }
}

// Backward path callback (called by target when response is ready)
tlm::tlm_sync_enum Cpu::nb_transport_bw(tlm::tlm_generic_payload& trans,
                                         tlm::tlm_phase& phase,
                                         sc_core::sc_time& t) {
    if (phase == tlm::BEGIN_RESP) {
        // Consume data
        phase = tlm::END_RESP;
        return tlm::TLM_UPDATED;  // tell target we're done
    }
    return tlm::TLM_ACCEPTED;
}
```

## Target Code Sketch

```cpp
tlm::tlm_sync_enum Ram::nb_transport_fw(tlm::tlm_generic_payload& trans,
                                         tlm::tlm_phase& phase,
                                         sc_core::sc_time& t) {
    if (phase == tlm::BEGIN_REQ) {
        // Schedule response after latency using a SC_THREAD or event
        pending = &trans;
        phase = tlm::END_REQ;
        t    += sc_core::sc_time(5, sc_core::SC_NS);
        return tlm::TLM_UPDATED;
    }
    if (phase == tlm::END_RESP) {
        return tlm::TLM_COMPLETED;
    }
    SC_REPORT_ERROR("RAM", "Unexpected phase");
    return tlm::TLM_ACCEPTED;
}
```

## LT vs AT Trade-offs

| Dimension | LT (`b_transport`) | AT (`nb_transport`) |
|---|---|---|
| Code complexity | Low | High |
| Simulation speed | Faster | Slower |
| Bus contention modeled | No | Yes |
| Pipelining modeled | No | Yes |
| Typical use | SW bring-up | Perf analysis |

## Common Pitfalls

- **Phase state machine violations** — calling `nb_transport_fw` with a phase that does not follow from the current state causes target assertions or silent corruption.
- **Memory ownership confusion** — both sides hold a pointer to the same GP; the owner must not delete it while the other side still references it.
- **Returning `TLM_COMPLETED` prematurely** — any future calls on the same transaction are illegal after `TLM_COMPLETED`.

> **Interview answer:** `nb_transport` splits a bus transaction into BEGIN_REQ/END_REQ/BEGIN_RESP/END_RESP phases exchanged over forward and backward paths, allowing the initiator and target to model pipelined bus behavior and contention — the Approximately-Timed (AT) abstraction level in TLM-2.0.
