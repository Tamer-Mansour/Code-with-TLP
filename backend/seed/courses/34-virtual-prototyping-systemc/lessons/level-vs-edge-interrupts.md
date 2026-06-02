# Level vs Edge-Triggered Interrupts

The distinction between level-triggered and edge-triggered interrupts is one of the most common sources of bugs in embedded software and VP modeling. Getting it wrong causes missed interrupts, infinite ISR loops, or spurious interrupt storms.

## Level-Triggered Interrupts

A **level-triggered** interrupt is asserted as long as the triggering condition is true. The interrupt line remains HIGH (or LOW for active-low) until the software acknowledges and clears the source.

### Behavior

- If the CPU exits the ISR but the peripheral has not cleared its status, the interrupt fires again immediately.
- The CPU can sample the line at any time and determine whether service is still required.
- Robust against missed edges — if the system was busy when the line was asserted, it will still see the level when it checks.

### SystemC Model

```cpp
// Peripheral drives the line high while data is available
void uart_process() {
    while (rx_fifo.size() > 0) {
        irq_out.write(true);   // line stays HIGH
        wait(SC_ZERO_TIME);
    }
    irq_out.write(false);      // de-assert when FIFO empty
}

// ISR (software) clears by reading the FIFO
void uart_isr() {
    uint8_t byte = mmio_read(UART_DATA);   // drains one entry
    // if FIFO still non-empty, peripheral re-asserts IRQ after ISR returns
}
```

Level triggering is the natural fit for **FIFO-based peripherals** (UART, Ethernet, USB) where "there is still data" is a persistent condition.

## Edge-Triggered Interrupts

An **edge-triggered** interrupt fires on the transition of the interrupt line — either rising edge (0→1), falling edge (1→0), or both. Once the controller latches the edge, the interrupt is pending regardless of the current line level.

### Behavior

- The peripheral can de-assert the line immediately after asserting it (a pulse).
- The interrupt controller must latch the edge internally; if it misses the edge the interrupt is lost.
- Software can clear the pending state in the interrupt controller without requiring the peripheral to lower its line.

### SystemC Model

```cpp
// Peripheral pulses the line
void timer_overflow() {
    irq_out.write(true);
    wait(SC_ZERO_TIME);     // one delta-cycle pulse
    irq_out.write(false);
}

// Interrupt controller latches the edge
void PLIC::irq_monitor() {
    bool prev = false;
    while (true) {
        wait(irq_src[n].value_changed_event());
        bool curr = irq_src[n].read();
        if (curr && !prev) {                    // rising edge
            pending[n/32] |= (1u << (n%32));    // latch
        }
        prev = curr;
    }
}
```

Edge triggering suits **event-driven peripherals** (timers, GPIO buttons, completion signals) where the event itself is transient.

## Comparison Table

| Characteristic | Level-Triggered | Edge-Triggered |
|---|---|---|
| IRQ line state | Held until SW clears source | Pulsed; controller latches edge |
| Missed event risk | None (line stays asserted) | High (pulse can be missed) |
| Spurious ISR risk | Yes (if SW doesn't clear) | Low |
| Typical use | FIFO peripherals, SPI, I2C | Timers, GPIO, completion |
| Controller requirement | Simple level detector | Edge-detect latch |
| Noise sensitivity | Less sensitive | More sensitive (glitch = IRQ) |

## Mixed Systems

ARM GIC and many PLIC implementations allow each source to be individually configured as level or edge. The VP model must read the configuration register and apply the correct detection logic:

```cpp
bool is_edge_triggered(int source_id) {
    return (trigger_config[source_id / 32] >> (source_id % 32)) & 1;
}

void update_pending(int id, bool prev_level, bool curr_level) {
    if (is_edge_triggered(id)) {
        if (curr_level && !prev_level)   // rising edge only
            set_pending(id);
    } else {
        if (curr_level) set_pending(id); // level
        else            clear_pending(id);
    }
}
```

## Common Pitfalls

- **Pulsing a level-triggered input:** If the peripheral pulses but the controller expects a sustained level, the interrupt clears before the CPU services it — missed IRQ.
- **Forgetting to clear a level-triggered source:** The ISR reads data but does not clear the peripheral's status register — the interrupt fires again immediately on ISR return.
- **Glitch on edge-triggered lines:** A noisy GPIO can cause spurious interrupts. Real hardware uses debounce; VP models can add a minimum-width filter.
- **Using the wrong trigger type for the OS:** Linux device tree entries specify `IRQ_TYPE_LEVEL_HIGH` or `IRQ_TYPE_EDGE_RISING`. A VP that uses the wrong type causes the OS driver to misbehave.

> **Interview answer:** Level-triggered interrupts remain asserted while the condition is true — missing them is impossible but forgetting to clear the source causes an ISR loop. Edge-triggered interrupts are latched on a signal transition — they can be missed if the edge occurs while interrupts are disabled, but the line need not stay asserted.
