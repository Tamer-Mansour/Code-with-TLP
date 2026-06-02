# How Interrupts Are Modeled in a VP

Interrupts are the primary mechanism by which hardware peripherals signal the CPU that they need attention. In a virtual prototype (VP), faithfully modeling interrupts is critical — software running on the VP expects the same interrupt behavior it would experience on real silicon.

## What an Interrupt Is (from the VP's Perspective)

An interrupt is an asynchronous event that causes the CPU to suspend its current execution, save state, and jump to a designated handler (the Interrupt Service Routine, or ISR). In a VP built with SystemC and TLM, interrupts are modeled as **signal-level side-channel communications** alongside the main TLM memory-mapped bus.

Because SystemC is an event-driven simulation, interrupts map naturally to **sc_signal<bool>** or **sc_out<bool>** ports that change value when a peripheral asserts or de-asserts its interrupt line.

## The Signal-Based Interrupt Model

The simplest and most common approach uses `sc_signal<bool>`:

```cpp
// Peripheral side — asserts the IRQ line
sc_out<bool> irq_out;   // driven by the peripheral

// Interrupt controller side — receives the IRQ
sc_in<bool>  irq_in;    // connected to the PLIC/GIC model
```

When a peripheral completes an operation (e.g., a UART finishes receiving a byte), it drives `irq_out.write(true)`. The signal propagates in zero simulation time within the same delta cycle, waking up any `sc_method` or `sc_thread` that is sensitive to that signal.

```cpp
// Inside the peripheral's process
void uart_rx_done() {
    rx_data_reg = received_byte;
    irq_out.write(true);   // assert interrupt
}
```

## Three Layers of Interrupt Modeling

| Layer | What It Models | SystemC Mechanism |
|---|---|---|
| Peripheral | Asserts/de-asserts IRQ line | `sc_out<bool>` driven in a process |
| Interrupt Controller | Prioritizes, masks, routes IRQs | `sc_method` sensitive to IRQ signals |
| CPU Model | Checks for pending IRQ, vectors to ISR | Checked at each instruction decode or via `sc_event` |

## Why Signal-Based Works for VPs

- **Zero-overhead assertion:** Writing to an `sc_signal` costs one delta cycle — negligible for software development.
- **Visibility:** SystemC waveform dumps (VCD/GTKWave) capture signal transitions, giving you a free interrupt timeline.
- **Composability:** Multiple peripherals can connect to one interrupt controller using `sc_vector<sc_signal<bool>>`.

## Common Pitfalls

- **Missing delta cycle:** If a peripheral writes an IRQ and reads it back in the same process without yielding (`wait()`), the new value is not yet visible — always yield at least one delta cycle.
- **Forgetting to de-assert:** Level-triggered interrupts must be de-asserted by the peripheral (or cleared by software writing to a status register). Leaving the line high causes repeated spurious interrupts.
- **No sensitivity list:** An `sc_method` that handles IRQs but is not listed as `sensitive << irq_in` will never wake up.

## Worked Example: A Simple IRQ Line

```cpp
SC_MODULE(SimplePeripheral) {
    sc_in<bool>  clk;
    sc_out<bool> irq;

    void run() {
        irq.write(false);
        wait(100, SC_NS);   // simulate work
        irq.write(true);    // assert interrupt
        wait(SC_ZERO_TIME); // let signal propagate
        irq.write(false);   // de-assert (pulse)
    }

    SC_CTOR(SimplePeripheral) {
        SC_THREAD(run);
        sensitive << clk.pos();
    }
};
```

The CPU model wakes up on the rising edge of `irq`, saves PC and registers, and branches to the ISR address.

> **Interview answer:** In a SystemC VP, interrupts are modeled as `sc_signal<bool>` lines driven by peripheral models. The CPU model is sensitive to those signals and, when asserted, simulates the hardware interrupt entry sequence — saving context and jumping to the ISR — mirroring real silicon behavior.
