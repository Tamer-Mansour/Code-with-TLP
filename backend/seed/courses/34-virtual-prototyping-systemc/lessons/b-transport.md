# Blocking Transport: b_transport

`b_transport` is the simplest and most widely used TLM-2.0 transport interface. It models a complete bus transaction — from address phase through data phase — as a single blocking C++ function call. The caller (initiator) does not return until the transaction is complete or has failed.

## Signature

```cpp
virtual void b_transport(tlm::tlm_generic_payload& trans,
                         sc_core::sc_time& t) = 0;
```

Two parameters:

- **`trans`** — the generic payload, passed by reference. The target fills in the data (for reads) and sets `response_status`.
- **`t`** — a *time annotation* passed by reference. The target adds its access latency to this value. The initiator later calls `wait(t)` at a convenient point to advance simulation time.

## The Temporal Decoupling Pattern

`b_transport` does **not** advance the simulation clock by itself. Instead both initiator and target accumulate time in a local `sc_time` variable and periodically synchronize with the simulator:

```cpp
// Initiator thread
void Cpu::run() {
    sc_core::sc_time local_time = sc_core::SC_ZERO_TIME;

    for (int i = 0; i < 1000; i++) {
        tlm::tlm_generic_payload trans;
        // ... fill trans ...
        socket->b_transport(trans, local_time);  // target adds latency

        if (local_time > quantum) {
            wait(local_time);          // sync every quantum
            local_time = sc_core::SC_ZERO_TIME;
        }
    }
    wait(local_time);  // final sync
}
```

The quantum (commonly 1 µs or one bus cycle period) is the maximum amount a thread may run ahead of wall-clock simulation time. This is called **loosely-timed (LT)** modeling because threads decouple from each other over a quantum window, enabling massive parallelism and speed.

## Target Implementation

```cpp
void Ram::b_transport(tlm::tlm_generic_payload& trans,
                      sc_core::sc_time& delay) {
    tlm::tlm_command cmd = trans.get_command();
    sc_dt::uint64    adr = trans.get_address();
    unsigned char*   ptr = trans.get_data_ptr();
    unsigned int     len = trans.get_data_length();

    // Range check
    if (adr + len > MEM_SIZE) {
        trans.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
        return;
    }

    if (cmd == tlm::TLM_WRITE_COMMAND)
        memcpy(&mem[adr], ptr, len);
    else if (cmd == tlm::TLM_READ_COMMAND)
        memcpy(ptr, &mem[adr], len);

    delay += sc_core::sc_time(10, sc_core::SC_NS);  // add access latency
    trans.set_dmi_allowed(true);                     // hint to initiator
    trans.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

Key points in the target:

1. Do not call `wait()` inside `b_transport` — it violates the LT contract and causes the simulation to deadlock or slow down.
2. Always set `response_status` before returning.
3. Add (not assign) latency to `delay`; the initiator may have already accumulated time from earlier calls.

## Worked Example: Full LT Read-Write Pair

```cpp
void Cpu::run() {
    const uint32_t ADDR = 0x2000;
    uint32_t write_val = 0xCAFEBABE;
    uint32_t read_val  = 0;
    sc_core::sc_time delay = sc_core::SC_ZERO_TIME;
    tlm::tlm_generic_payload trans;

    // Write
    trans.set_command(tlm::TLM_WRITE_COMMAND);
    trans.set_address(ADDR);
    trans.set_data_ptr(reinterpret_cast<unsigned char*>(&write_val));
    trans.set_data_length(4);
    trans.set_streaming_width(4);
    trans.set_byte_enable_ptr(nullptr);
    trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
    socket->b_transport(trans, delay);
    assert(trans.is_response_ok());

    // Read back
    trans.set_command(tlm::TLM_READ_COMMAND);
    trans.set_data_ptr(reinterpret_cast<unsigned char*>(&read_val));
    trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
    socket->b_transport(trans, delay);
    assert(trans.is_response_ok());
    assert(read_val == write_val);

    wait(delay);  // synchronize after both transactions
}
```

## Rules and Restrictions

- `b_transport` must not be called from an SC_METHOD context (no blocking waits allowed in methods). Use an `SC_THREAD`.
- The generic payload pointer passed to the target is valid only for the duration of the call. Targets must not store `trans.get_data_ptr()` beyond `b_transport` return.
- Byte-enable and streaming fields must be consistent with `data_length` or the call is protocol-invalid.

## Common Pitfalls

- **Calling `wait()` inside the target's `b_transport`** — slows simulation and can cause starvation in multi-initiator setups.
- **Not calling `wait(delay)` in the initiator** — the model runs faster than real time, time annotations accumulate but never commit, and time-dependent peripherals (timers, UART baud rate) behave incorrectly.
- **Ignoring the response status** — silent data corruption if the target returns an error the initiator does not check.

> **Interview answer:** `b_transport` is a single blocking call that transfers a complete transaction; the target adds its latency to a reference `sc_time` parameter rather than calling `wait()`, so the initiator thread can batch thousands of transactions before synchronizing — achieving LT loosely-timed simulation performance.
