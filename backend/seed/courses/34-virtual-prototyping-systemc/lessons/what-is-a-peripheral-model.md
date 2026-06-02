# What Is a Peripheral Model?

A **peripheral model** is a software representation of a hardware device — such as a UART, timer, GPIO controller, or DMA engine — that captures the device's observable behavior without necessarily implementing every transistor. In virtual prototyping with SystemC, peripheral models let software teams develop and test firmware before silicon is available.

## Why Model Peripherals?

Real hardware takes months to fabricate. A peripheral model running in a SystemC simulation gives firmware engineers a "virtual board" they can boot, debug, and stress-test from day one of a project. The key goals are:

- **Functional correctness** — the model responds to register reads and writes exactly as the datasheet specifies.
- **Timing accuracy** — latencies, interrupt delays, and DMA burst widths match silicon close enough for software to trust.
- **Testability** — the model can inject faults, log all accesses, and expose internal state that real hardware hides behind pins.

## Levels of Abstraction

Peripheral models are not one-size-fits-all. The right level depends on the simulation goal:

| Level | Detail | Speed | Use Case |
|-------|--------|-------|----------|
| Pin-accurate | Every signal toggled | Slowest | RTL co-simulation |
| Cycle-accurate | Clocked FSM | Slow | Hardware/software integration |
| Transaction-accurate (TLM) | Register read/write only | Fast | Firmware bring-up |
| Functional | Behavior only, no timing | Fastest | Algorithm validation |

TLM-2.0 peripheral models are the most common in early-stage virtual prototyping because they run orders of magnitude faster than RTL while still exposing a correct register interface.

## Anatomy of a TLM Peripheral Model

A typical SystemC/TLM peripheral module contains:

```cpp
SC_MODULE(UartModel) {
    // TLM target socket — receives reads/writes from the bus
    tlm_utils::simple_target_socket<UartModel> socket;

    // Internal register bank
    uint32_t regs[NUM_REGS];

    // Interrupt output port
    sc_out<bool> irq;

    SC_CTOR(UartModel) : socket("socket") {
        socket.register_b_transport(this, &UartModel::b_transport);
        SC_THREAD(tx_thread);  // models UART transmit behavior
    }

    void b_transport(tlm::tlm_generic_payload& trans, sc_time& delay);
    void tx_thread();
};
```

Key elements:

- **Target socket** — the bus-facing port that accepts TLM transactions.
- **Register array or struct** — holds the device's internal state.
- **SC_THREAD or SC_METHOD** — models asynchronous hardware behavior such as DMA completion or FIFO draining.
- **Interrupt port** — signals the processor when the device needs attention.

## Common Pitfalls

- **Ignoring reset state.** Every register has a documented reset value. If the model powers up with zeros when the datasheet says a control register defaults to `0x0001`, firmware that checks the reset value will fail silently.
- **Missing side effects.** Writing to a control register often starts a DMA, clears an interrupt, or changes baud rate. A model that only stores the written value without triggering the side effect is incomplete.
- **Wrong address decode.** Off-by-one in the base address or register offset is one of the most common bugs in peripheral models. Always cross-check against the memory map in the SoC spec.

## Worked Example: Minimal Status Register

```cpp
void UartModel::b_transport(tlm::tlm_generic_payload& trans, sc_time& delay) {
    sc_dt::uint64 addr = trans.get_address();
    uint8_t* data      = trans.get_data_ptr();
    unsigned int len   = trans.get_data_length();

    if (trans.get_command() == tlm::TLM_READ_COMMAND) {
        if (addr == STATUS_REG_OFFSET) {
            uint32_t status = tx_ready ? STATUS_TX_EMPTY : 0u;
            memcpy(data, &status, len);
        }
    }
    trans.set_response_status(tlm::TLM_OK_RESPONSE);
    delay += sc_time(10, SC_NS);  // model access latency
}
```

> **Interview answer:** A peripheral model is a software component that faithfully reproduces a hardware device's register interface and behavioral side effects so that firmware can be developed and validated before real silicon exists.
