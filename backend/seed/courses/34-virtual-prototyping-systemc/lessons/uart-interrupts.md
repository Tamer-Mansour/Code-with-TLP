# UART Interrupts and Status Flags

Interrupts are what transform a UART from a polled peripheral into an efficient I/O device. A virtual UART that generates interrupts incorrectly will either stall the simulated driver (missed interrupt) or flood the interrupt controller (spurious interrupt), both of which are hard to debug without understanding the underlying mechanism.

## The Interrupt Sources

The 16550 defines four interrupt causes, prioritized from highest to lowest:

| Priority | IIR code | Source | Cleared by |
|---|---|---|---|
| 1 (highest) | 0x06 | Receiver Line Status (OE, PE, FE, BI) | Reading LSR |
| 2 | 0x04 | Received Data Available (RX FIFO ≥ trigger) | Reading RHR until below trigger |
| 2 | 0x0C | Character Timeout (RX data stale, FIFO mode) | Reading RHR |
| 3 | 0x02 | Transmitter Holding Register Empty | Writing THR or reading IIR |
| 4 (lowest) | 0x00 | Modem Status Change | Reading MSR |

The **Interrupt Identification Register (IIR)** at offset 2 reports the highest-priority pending interrupt. Bit 0 is 0 when an interrupt is active, 1 when no interrupt is pending. Bits [3:1] encode the cause.

## Interrupt Enable Register (IER)

Each interrupt source has a corresponding enable bit in IER. If the bit is 0, that source cannot generate an interrupt even if the condition is met.

```
IER bit 0: RDAI  — Receive Data Available Interrupt
IER bit 1: THREI — Transmit Holding Register Empty Interrupt
IER bit 2: RLSI  — Receiver Line Status Interrupt
IER bit 3: MSI   — Modem Status Interrupt
```

## Modeling the IRQ Line in SystemC

The UART drives a single active-high interrupt signal. In SystemC:

```cpp
sc_core::sc_out<bool> irq_out;

void UartModel::update_irq() {
    bool pending = compute_iir() != 0x01; // 0x01 = no interrupt pending
    irq_out.write(pending);
}

uint8_t UartModel::compute_iir() {
    // Check in priority order
    if ((ier_ & 0x04) && (lsr_ & 0x1E))           return 0x06; // Line status
    if ((ier_ & 0x01) && (rx_fifo_.size() >= rx_trigger_level()))
                                                    return 0x04; // RX data
    if ((ier_ & 0x01) && rx_timeout_pending_)       return 0x0C; // Char timeout
    if ((ier_ & 0x02) && tx_fifo_.empty())          return 0x02; // TX empty
    if ((ier_ & 0x08) && msr_changed_)              return 0x00; // Modem status
    return 0x01; // No interrupt pending (bit 0 = 1)
}
```

Call `update_irq()` after every state change: FIFO push/pop, LSR update, or IER write.

## The THREI Subtlety

The THREI interrupt fires when the TX FIFO becomes empty (or the TX holding register is empty in non-FIFO mode). It is **level-sensitive**: as long as the TX FIFO is empty AND THREI is enabled, the interrupt remains asserted.

This means the driver's ISR must either:
- Write at least one byte to THR (filling the FIFO, lowering the interrupt), or
- Disable THREI in IER (if there is nothing left to send).

A common driver bug is to enable THREI before sending the first byte. The interrupt fires immediately because the TX FIFO starts empty, causing the ISR to run before any data is queued. The model must reproduce this behavior faithfully.

```cpp
// Correct driver sequence:
uart_write(THR, first_byte);  // fills FIFO, THREI won't fire immediately
uart_write(IER, IER_THREI | IER_RDAI); // enable now — FIFO not empty yet
```

## Character Timeout

In FIFO mode, if RX data has been sitting in the FIFO for 4 character times without being read, the UART fires a Character Timeout interrupt (IIR 0x0C). This ensures that a short message that never reaches the trigger level is still delivered to the driver.

In simulation, implement this with a delayed SC_THREAD:

```cpp
void UartModel::rx_timeout_thread() {
    while (true) {
        wait(rx_push_event_);
        wait(char_timeout_period_);          // 4 × baud period
        if (!rx_fifo_.empty() && (ier_ & 0x01)) {
            rx_timeout_pending_ = true;
            update_irq();
        }
    }
}
```

## Clearing Interrupts

| Interrupt | How it clears |
|---|---|
| RLS | Read LSR |
| RDAI | Read RHR until FIFO below trigger |
| Char Timeout | Read RHR (any read) |
| THREI | Write THR OR read IIR |
| MSI | Read MSR |

The model must clear the flag and call `update_irq()` in the handler for each register read.

**Interview answer:** The virtual UART drives a single IRQ line whose state is recomputed after every state change using a priority-ordered IIR calculation. THREI is level-sensitive and stays asserted as long as the TX FIFO is empty and THREI is enabled; the driver must write data or disable the bit to deassert it.

## Common Pitfalls

- **Pulse instead of level** — driving the IRQ line high for one delta cycle and immediately lowering it will miss the interrupt at the controller. The IRQ must remain high until the cause is cleared.
- **Not calling `update_irq()` after IER write** — enabling THREI when the TX FIFO is already empty must fire immediately.
- **Forgetting character timeout** — drivers that use small messages never reach the FIFO trigger level and will block waiting for a timeout interrupt the model never generates.
