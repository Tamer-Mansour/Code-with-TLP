# The UART Register Interface

The register interface is the contract between the UART hardware and its software driver. Getting it right is the single most important step in building a useful virtual UART, because every line of driver code ultimately reduces to reads and writes of these registers.

## The 16550-Compatible Register Map

The 16550 UART (and its descendants) is the industry reference. All registers are accessed through a handful of offsets from the UART base address. Several registers share an offset but are selected by the Divisor Latch Access Bit (DLAB) in LCR or by the direction of the transaction.

| Offset | DLAB | R/W | Name | Purpose |
|--------|------|-----|------|---------|
| 0 | 0 | W | THR | Transmit Holding Register — write a byte to send |
| 0 | 0 | R | RHR/RBR | Receive Holding Register — read a received byte |
| 0 | 1 | R/W | DLL | Baud-rate divisor low byte |
| 1 | 0 | R/W | IER | Interrupt Enable Register |
| 1 | 1 | R/W | DLM | Baud-rate divisor high byte |
| 2 | — | W | FCR | FIFO Control Register (write-only) |
| 2 | — | R | IIR | Interrupt Identification Register (read-only) |
| 3 | — | R/W | LCR | Line Control Register (bit 7 = DLAB) |
| 4 | — | R/W | MCR | Modem Control Register |
| 5 | — | R | LSR | Line Status Register |
| 6 | — | R | MSR | Modem Status Register |
| 7 | — | R/W | SCR | Scratch Register |

## Decoding a TLM Transaction

In SystemC TLM-2.0, incoming bus transactions arrive as `tlm_generic_payload` objects. The register decode looks like this:

```cpp
void UartModel::b_transport(tlm::tlm_generic_payload &trans, sc_core::sc_time &delay) {
    uint64_t addr   = trans.get_address();
    uint8_t *data   = reinterpret_cast<uint8_t *>(trans.get_data_ptr());
    bool     is_wr  = (trans.get_command() == tlm::TLM_WRITE_COMMAND);

    uint8_t  reg    = static_cast<uint8_t>(addr & 0x7); // 3 address bits
    bool     dlab   = (lcr_ >> 7) & 1;

    if (is_wr) handle_write(reg, dlab, *data);
    else        *data = handle_read(reg, dlab);

    trans.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

## Key Register Semantics

### THR — Transmit Holding Register (write, DLAB=0, offset 0)

Writing a byte here enqueues it into the TX FIFO. The model should:

1. Push the byte onto the TX FIFO.
2. Clear LSR bit 5 (THRE) if the FIFO was empty and is now non-empty.
3. Trigger the TX-path coroutine or call `forward_tx()` directly.

### RHR — Receive Holding Register (read, DLAB=0, offset 0)

Reading here pops one byte from the RX FIFO. If the FIFO becomes empty, clear LSR bit 0 (DR — Data Ready).

### LSR — Line Status Register (read-only, offset 5)

```
Bit 7: Error in receiver FIFO
Bit 6: Transmitter Empty (TEMT) — TX FIFO and shift register both empty
Bit 5: Transmitter Holding Register Empty (THRE)
Bit 4: Break Interrupt
Bit 3: Framing Error
Bit 2: Parity Error
Bit 1: Overrun Error (OE)
Bit 0: Data Ready (DR) — at least one byte in RX FIFO
```

Most drivers poll bits 0 and 5 in a tight loop. Keep LSR always up-to-date.

### IER — Interrupt Enable Register (offset 1, DLAB=0)

```
Bit 0: Enable Received Data Available interrupt (RDAI)
Bit 1: Enable Transmitter Holding Register Empty interrupt (THREI)
Bit 2: Enable Receiver Line Status interrupt
Bit 3: Enable Modem Status interrupt
```

### FCR — FIFO Control Register (write-only, offset 2)

```
Bit 0: FIFO Enable
Bit 1: RX FIFO Reset
Bit 2: TX FIFO Reset
Bits 6-7: RX FIFO trigger level (00=1, 01=4, 10=8, 11=14 bytes)
```

## Implementing the Write Handler

```cpp
void UartModel::handle_write(uint8_t reg, bool dlab, uint8_t val) {
    switch (reg) {
    case 0:
        if (dlab) { dll_ = val; }
        else      { tx_fifo_.push(val); update_lsr(); trigger_tx(); }
        break;
    case 1:
        if (dlab) { dlm_ = val; }
        else      { ier_ = val & 0x0F; update_irq(); }
        break;
    case 2: /* FCR */
        if (val & 0x02) { while (!rx_fifo_.empty()) rx_fifo_.pop(); }
        if (val & 0x04) { while (!tx_fifo_.empty()) tx_fifo_.pop(); }
        fcr_ = val;
        break;
    case 3: lcr_ = val; break;
    case 4: mcr_ = val; break;
    case 7: scr_ = val; break;
    }
}
```

**Interview answer:** The 16550 UART uses a 3-bit offset to address eight register positions; several share an offset and are disambiguated by the DLAB bit in LCR (for DLL/DLM vs THR/IER) or by read-vs-write direction (FCR vs IIR). The virtual model decodes these in `b_transport` and maintains shadow copies in member variables.

## Common Pitfalls

- **Forgetting DLAB** — if the model ignores the DLAB bit, writes to THR silently corrupt the baud divisor and vice versa.
- **FCR is write-only** — reading offset 2 returns IIR, not FCR. Models that return `fcr_` on a read break the IIR query the driver uses to identify pending interrupts.
- **Scratch register (SCR)** — some boot loaders write a canary to SCR and read it back to confirm the UART is present. If SCR is not a simple latch the boot loader may abort initialization.
