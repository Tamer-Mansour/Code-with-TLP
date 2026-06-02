# Interoperability and the Convenience Sockets

TLM-2.0 defines strict interoperability rules, but writing every module to the raw `tlm_fw_transport_if` and `tlm_bw_transport_if` is verbose. The `tlm_utils` library ships a set of ready-made socket adapters — commonly called convenience sockets — that handle the boilerplate so you can focus on model behavior.

## The Core Interoperability Problem

An LT initiator (using `b_transport`) cannot directly drive an AT target (using only `nb_transport_fw`), and vice versa. The standard solution is a protocol adapter placed between them, called a **converter** or **gasket**. TLM-2.0's design makes this adapter pluggable without modifying either model.

## Convenience Socket Variants

| Class | Header | Purpose |
|---|---|---|
| `simple_initiator_socket<M>` | `tlm_utils/simple_initiator_socket.h` | Single-bound initiator; registers callbacks on target |
| `simple_target_socket<M>` | `tlm_utils/simple_target_socket.h` | Single-bound target; dispatch callbacks to member functions |
| `multi_passthrough_initiator_socket<M>` | `tlm_utils/multi_passthrough_initiator_socket.h` | One initiator driving multiple targets |
| `multi_passthrough_target_socket<M>` | `tlm_utils/multi_passthrough_target_socket.h` | One target accepting multiple initiators; each has a unique `id` |

All four wrap the raw socket and add callback registration so you write one-liner bindings.

## simple_target_socket: Registering Callbacks

```cpp
#include "tlm_utils/simple_target_socket.h"

struct Peripheral : sc_core::sc_module {
    tlm_utils::simple_target_socket<Peripheral> socket;

    SC_CTOR(Peripheral) : socket("socket") {
        socket.register_b_transport(this, &Peripheral::b_transport);
        socket.register_transport_dbg(this, &Peripheral::transport_dbg);
        socket.register_get_direct_mem_ptr(this, &Peripheral::get_dmi_ptr);
    }

    void b_transport(tlm::tlm_generic_payload& t, sc_core::sc_time& delay) { /*...*/ }
    unsigned int transport_dbg(tlm::tlm_generic_payload& t) { return 0; }
    bool get_dmi_ptr(tlm::tlm_generic_payload& t, tlm::tlm_dmi& d) { return false; }
};
```

Only the callbacks you register are active. Unregistered interfaces return safe defaults (0 bytes transferred, DMI denied).

## Multi-Passthrough Target: Handling Multiple Masters

```cpp
struct Bus : sc_core::sc_module {
    tlm_utils::multi_passthrough_target_socket<Bus> target_socket;

    SC_CTOR(Bus) : target_socket("target_socket") {
        target_socket.register_b_transport(this, &Bus::b_transport);
    }

    // id identifies which initiator sent the transaction
    void b_transport(int id, tlm::tlm_generic_payload& trans,
                     sc_core::sc_time& delay) {
        // Route based on address, arbitrate on id ...
    }
};
```

## The LT-AT Adapter Pattern

When an LT initiator must talk to an AT target, insert a standard converter. `tlm_utils` provides `tlm_quantumkeeper` for managing the LT quantum, but for the LT→AT protocol conversion itself, you write a passthrough module:

```cpp
// Sketch: b_transport wraps a complete 4-phase AT handshake
void LtToAtAdapter::b_transport(tlm::tlm_generic_payload& trans,
                                 sc_core::sc_time& delay) {
    tlm::tlm_phase phase = tlm::BEGIN_REQ;
    sc_core::sc_time t = sc_core::SC_ZERO_TIME;

    auto status = at_socket->nb_transport_fw(trans, phase, t);

    if (status == tlm::TLM_COMPLETED) {
        delay += t;
        return;
    }
    // wait for response event set by nb_transport_bw ...
    wait(response_event);
    delay += response_time;
}
```

## The Quantum Keeper

`tlm_utils::tlm_quantumkeeper` centralizes temporal decoupling for LT models:

```cpp
#include "tlm_utils/tlm_quantumkeeper.h"

tlm_utils::tlm_quantumkeeper qk;

SC_CTOR(Cpu) {
    tlm_utils::tlm_quantumkeeper::set_global_quantum(
        sc_core::sc_time(1, sc_core::SC_US));  // 1 µs quantum
    qk.reset();
}

void Cpu::run() {
    while (true) {
        // ... fetch/decode/execute ...
        socket->b_transport(trans, qk.get_current_time());
        qk.inc(cycle_time);
        if (qk.need_sync()) qk.sync();  // advance wall-clock time
    }
}
```

`need_sync()` returns true when accumulated local time exceeds the global quantum. `sync()` calls `wait()` and resets the counter — a clean, centralized place to manage synchronization instead of scattering `wait()` calls through the model.

## Interoperability Checklist

A model is TLM-2.0 compliant (and hence reusable) when it:

- Uses `tlm_initiator_socket` or `tlm_target_socket` (or the convenience variants).
- Uses only standard GP fields for basic read/write.
- Makes extensions optional (null-checks before access).
- Returns a valid `response_status` in every `b_transport` call.
- Does not call `wait()` inside `b_transport` on the target side.
- Handles `invalidate_direct_mem_ptr` callbacks correctly.

## Common Pitfalls

- **Using `simple_initiator_socket` as a passthrough** — it allows only one binding; use `multi_passthrough_initiator_socket` for a router output with multiple destinations.
- **Forgetting to set the global quantum** — without it, `tlm_quantumkeeper::need_sync()` always returns true and every transaction synchronizes, destroying LT speed.
- **Mixing LT and AT without an adapter** — the calls resolve at compile time to different virtual functions; a direct binding silently ignores the AT path.

> **Interview answer:** Convenience sockets (`simple_initiator_socket`, `simple_target_socket`, `multi_passthrough_*_socket`) are `tlm_utils` wrappers that replace boilerplate callback registration; combined with `tlm_quantumkeeper` for temporal decoupling management, they form the practical interoperability layer that makes TLM-2.0 models reusable across projects without modification.
