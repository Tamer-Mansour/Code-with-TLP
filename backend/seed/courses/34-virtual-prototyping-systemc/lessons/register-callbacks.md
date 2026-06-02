# Read/Write Callbacks and Side Effects

Storing a value in a register is rarely the end of the story. Real hardware reacts: a write to a control register starts a DMA transfer, reading a status register clears a pending interrupt, and toggling an enable bit powers up an analog block. **Callbacks** are the mechanism that peripheral models use to trigger these side effects at the right moment.

## The Problem with Passive Storage

A naive register model that only stores and returns values will satisfy a unit test that checks the stored value — but it will fail any firmware test that depends on hardware reacting. Consider a timer:

```cpp
// Naive — stores value, does nothing else
void TimerModel::on_write(uint32_t offset, uint32_t val) {
    regs_[offset] = val;
}
```

Firmware that writes the reload value and then enables the timer expects the countdown to begin. The naive model never starts it.

## Pre- and Post-Access Callbacks

A clean pattern is to split every register access into three phases:

1. **Pre-access callback** — runs before the default read/write logic. Can veto or transform the access.
2. **Default access logic** — applies standard field semantics (RW store, W1C clear, RO ignore, etc.).
3. **Post-access callback** — runs after storage is updated. Triggers side effects.

```cpp
struct Register {
    uint32_t value;
    std::function<void(uint32_t)> post_write_cb;
    std::function<uint32_t()>     pre_read_cb;

    void write(uint32_t val) {
        value = apply_field_rules(value, val);
        if (post_write_cb) post_write_cb(value);
    }

    uint32_t read() {
        if (pre_read_cb) pre_read_cb(); // e.g., clear RC fields
        return value;
    }
};
```

## Registering Callbacks in a Peripheral

In a SystemC peripheral model, the callback usually invokes an `SC_THREAD` or posts an event:

```cpp
SC_MODULE(TimerModel) {
    sc_event start_event_;

    void setup_registers() {
        ctrl_reg_.post_write_cb = [this](uint32_t v) {
            if (v & CTRL_EN_BIT) {
                start_event_.notify(SC_ZERO_TIME);
            }
        };
    }

    void timer_thread() {
        while (true) {
            wait(start_event_);
            sc_time period(reload_reg_.value, SC_NS);
            wait(period);
            // Set overflow flag, assert IRQ
            status_reg_.value |= STATUS_OVF;
            irq_.write(true);
        }
    }
};
```

## RC Register: Side Effect on Read

A Read-to-Clear register clears itself as a side effect of being read. The pre-read callback is the natural place to implement this:

```cpp
void setup_fifo_data_register() {
    fifo_data_reg_.pre_read_cb = [this]() {
        // After this read, the register clears itself
        sc_spawn([this]() {
            wait(SC_ZERO_TIME);
            fifo_data_reg_.value = 0;
        });
    };
}
```

Using `SC_ZERO_TIME` ensures the value is returned first, then cleared on the next delta cycle — matching real hardware behaviour.

## Interrupt Generation as a Post-Write Side Effect

Interrupt generation is the most common side effect. A W1C interrupt status register should de-assert the interrupt line when all flags are cleared:

```cpp
void IrqController::isr_post_write(uint32_t new_val) {
    // Re-evaluate interrupt line
    bool any_active = (new_val & ier_reg_.value) != 0;
    irq_.write(any_active);
}
```

This keeps interrupt logic centralized in one callback rather than scattered through the register write path.

## Ordering Guarantees and Reentrancy

A pitfall with synchronous callbacks is reentrancy: if a callback writes another register, that write may trigger another callback, and so on. Strategies to handle this:

- **Defer callbacks to the next delta cycle** using `notify(SC_ZERO_TIME)` — the safest approach.
- **Maintain a dirty-register queue** and process it at the end of the `b_transport` call.
- **Document and enforce a no-reentrant-write policy** in the model API.

## Common Pitfalls

- **Callback fires on reset.** If `register.reset()` calls `write()`, every post-write callback runs during reset — potentially starting peripherals before the simulation is ready. Bypass callbacks during reset.
- **Forgetting the "interrupt mask" register.** An interrupt status flag that is set but masked should not assert the IRQ line. The callback must check the interrupt enable register too.
- **Logging inside callbacks.** Verbose logging inside callbacks that fire on every access dramatically slows simulation. Use conditional compilation or verbosity levels.

> **Interview answer:** Callbacks are functions attached to register read/write events that trigger hardware side effects — such as starting a DMA, asserting an interrupt, or clearing a latch — so the model reacts exactly as real hardware would rather than acting as passive storage.
