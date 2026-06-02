# Peripheral Internal State Machines

Most non-trivial peripherals are not simple register files. They have **internal state machines** (FSMs) that govern their behavior over time: a UART goes from IDLE to TRANSMITTING to DONE; a DMA controller cycles through REQUEST, ARBITRATION, BURST, and IDLE. Modeling these state machines correctly is essential for firmware that polls status registers or waits for interrupts.

## Why Peripherals Need State Machines

A register can tell you the *current status*, but it cannot tell you *why* a transition happened or *what comes next* without an FSM. Consider a simplified SPI controller:

- In IDLE, writing CTRL.START=1 initiates a transfer.
- During BUSY, writes to the data register are ignored.
- When DONE, the status register asserts XFER_DONE and an interrupt fires.
- Firmware acknowledging the interrupt (W1C on XFER_DONE) returns the controller to IDLE.

Without an FSM, there is no way to enforce these ordering constraints.

## Representing the FSM in SystemC

`SC_THREAD` is the natural construct for sequential state machine logic because it can `wait()` for events or time without blocking the entire simulation:

```cpp
SC_MODULE(SpiController) {
    enum State { IDLE, BUSY, DONE };
    State state_ = IDLE;

    sc_event start_event_;
    sc_event ack_event_;

    void fsm_thread() {
        while (true) {
            // IDLE: wait for firmware to assert START
            state_ = IDLE;
            status_reg_ &= ~STATUS_BUSY;
            wait(start_event_);

            // BUSY: transfer in progress
            state_ = BUSY;
            status_reg_ |= STATUS_BUSY;
            sc_time xfer_time(transfer_bits_ * bit_period_ns_, SC_NS);
            wait(xfer_time);

            // DONE: assert interrupt, wait for firmware ACK
            state_ = DONE;
            status_reg_ |= STATUS_XFER_DONE;
            status_reg_ &= ~STATUS_BUSY;
            irq_.write(true);
            wait(ack_event_);
            irq_.write(false);
        }
    }
};
```

## State Validation in Register Callbacks

Callbacks should check the current FSM state before accepting a write. Firmware writing START=1 while a transfer is already in progress should be rejected or flagged as an error:

```cpp
void SpiController::on_ctrl_write(uint32_t val) {
    if ((val & CTRL_START) && state_ != IDLE) {
        // Log error: firmware attempted to start while BUSY
        SC_REPORT_WARNING("SpiController", "START written while BUSY — ignored");
        return;
    }
    ctrl_reg_ = val;
    if (val & CTRL_START) {
        start_event_.notify(SC_ZERO_TIME);
    }
}
```

## State Machine Diagram (Text Representation)

```
         FW writes START=1
IDLE ─────────────────────────► BUSY
 ▲                                │
 │    FW W1C on XFER_DONE         │  Transfer completes (time elapsed)
 └─────────────────────────── DONE ◄──────────────────────────────────
```

## Modeling Reset

The FSM must return to IDLE on a hardware reset. In SystemC, a reset port or signal is typically monitored:

```cpp
SC_THREAD(reset_thread);
sensitive << reset_n_.neg();

void reset_thread() {
    while (true) {
        wait();           // wait for falling edge of reset_n
        state_ = IDLE;
        ctrl_reg_  = CTRL_RESET_VAL;
        status_reg_ = STATUS_RESET_VAL;
        irq_.write(false);
        start_event_.cancel();
    }
}
```

## Common Pitfalls

- **Missing the DONE-to-IDLE transition.** If the FSM waits for an ACK event that never arrives (because firmware misses the interrupt), the model hangs. Add a timeout watchdog that asserts a simulation warning after a configurable number of nanoseconds.
- **Race between FSM thread and b_transport.** The TLM transport function runs in the initiator's thread context. If it directly modifies FSM state (e.g., writing `state_ = BUSY`), a data race can occur. Use `sc_event` notifications to decouple them.
- **Returning wrong status mid-transfer.** The status register must reflect the current FSM state, not a stale snapshot. Read the state variable in the register read callback, do not cache it separately.

## Worked Example: Timer FSM States

| State | STATUS_RUN | STATUS_OVF | On FW Action |
|-------|-----------|-----------|--------------|
| IDLE | 0 | 0 | Write CTRL.EN=1 → RUNNING |
| RUNNING | 1 | 0 | Reload elapsed → OVERFLOW, or FW write CTRL.EN=0 → IDLE |
| OVERFLOW | 1 | 1 | FW W1C on STATUS.OVF → RUNNING (auto-reload) |

> **Interview answer:** Peripheral FSMs encode the legal sequence of states a device moves through — a register alone cannot enforce ordering constraints such as "you cannot start a new transfer while one is in progress" without an FSM driving the status bits and gating further commands.
