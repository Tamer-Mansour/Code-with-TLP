# Loosely-Timed (LT) Coding Style

The **Loosely-Timed (LT)** coding style is the simplest and fastest TLM-2.0 style to simulate. It prioritizes simulation speed over timing accuracy, making it the preferred choice during early architecture exploration, software bring-up, and functional verification.

## Core Idea

In LT, a single blocking function call — `b_transport` — models an entire bus transaction from request to response. The initiator (e.g., a CPU model) calls `b_transport`, the target (e.g., a memory model) completes it, and control returns to the initiator in one step. There is no back-and-forth handshaking between phases.

```cpp
// Initiator side — LT b_transport call
void cpu_thread() {
    tlm::tlm_generic_payload trans;
    sc_core::sc_time delay = sc_core::SC_ZERO_TIME;

    trans.set_command(tlm::TLM_WRITE_COMMAND);
    trans.set_address(0x1000);
    trans.set_data_ptr(reinterpret_cast<unsigned char*>(&data));
    trans.set_data_length(4);
    trans.set_streaming_width(4);
    trans.set_byte_enable_ptr(nullptr);
    trans.set_dmi_allowed(false);
    trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);

    socket->b_transport(trans, delay);   // blocking call

    // Consume the annotated delay locally — do NOT wait yet
    // (temporal decoupling — covered in a later lesson)
    wait(delay);
}
```

```cpp
// Target side — LT b_transport implementation
void b_transport(tlm::tlm_generic_payload& trans, sc_core::sc_time& delay) {
    // Model bus latency by annotating the delay parameter
    delay += sc_core::sc_time(10, SC_NS);

    tlm::tlm_command cmd = trans.get_command();
    sc_dt::uint64    adr = trans.get_address();
    unsigned char*   ptr = trans.get_data_ptr();
    unsigned int     len = trans.get_data_length();

    if (cmd == tlm::TLM_READ_COMMAND)
        memcpy(ptr, mem + adr, len);
    else
        memcpy(mem + adr, ptr, len);

    trans.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

## Key Characteristics

| Feature | LT Behavior |
|---|---|
| Transport API | `b_transport` (blocking) |
| Timing | Annotated delay — not enforced by scheduler |
| Phase protocol | Not used (no `nb_transport`) |
| Simulation speed | Very fast (few context switches) |
| Timing accuracy | Low (transaction happens "instantly" from the scheduler's view) |
| Typical use | Software bring-up, functional verification |

## Delay Annotation vs. Wait

A subtle but important distinction: in LT, the target **annotates** a delay value by adding to the `sc_time& delay` argument rather than calling `wait()` directly. The initiator then decides when (and whether) to call `wait(delay)`. This is the foundation of **temporal decoupling** — the initiator runs ahead of simulated time up to a quantum limit.

## Common Pitfalls

- **Calling `wait()` inside `b_transport`** turns a non-blocking annotation into a real scheduler suspension, breaking the LT contract and causing unnecessary context switches.
- **Ignoring the response status** — always check `trans.get_response_status()` after the call; a target that cannot service a request should set `TLM_ADDRESS_ERROR_RESPONSE` or similar.
- **Thread-safety confusion** — `b_transport` is called in the initiator's thread context; targets must not store a reference to the payload beyond the call.

## Why LT Is Preferred for Software Development

Booting a full embedded OS on a virtual prototype can require simulating billions of instructions. Each `b_transport` call completes in a handful of C++ function calls with no scheduler overhead. The same scenario in a cycle-accurate RTL simulation might take hours; an LT model can finish in minutes.

> **Interview answer:** "LT uses a single blocking `b_transport` call per transaction and annotates latency as a delay parameter rather than advancing the simulator clock. This eliminates scheduler overhead, making it 10-100x faster than AT, at the cost of timing accuracy."
