# Register Access Types: RO, RW, W1C, RC

Hardware registers are not uniform storage cells. Every bit field carries an **access type** that defines what happens when software reads or writes it. Getting these semantics wrong in a peripheral model produces subtle firmware bugs that are nearly impossible to reproduce on real hardware.

## The Four Core Access Types

### RO — Read Only

The field is driven by hardware logic and cannot be changed by software writes.

- A write is silently ignored (the field retains its hardware-driven value).
- Typical use: status bits such as "TX FIFO empty", "PLL locked", "overrun error".

```cpp
uint32_t on_write_ro_field(uint32_t reg_val, uint32_t written, uint32_t mask) {
    // Mask out the RO field — software write has no effect
    return (reg_val & mask) | (written & ~mask);
}
```

### RW — Read/Write

The most common type. Software can freely read and write the field; the stored value is what is read back.

- Typical use: configuration fields such as baud rate divisor, DMA burst size, interrupt enable.

```cpp
// Store verbatim, read back verbatim
uint32_t on_write_rw_field(uint32_t reg_val, uint32_t written, uint32_t mask) {
    return (reg_val & ~mask) | (written & mask);
}
```

### W1C — Write 1 to Clear

Writing a **1** to a W1C bit **clears** it (sets it to 0). Writing a **0** has no effect. The bit is still readable.

- Typical use: interrupt status / event flags that hardware sets and software acknowledges.

```cpp
uint32_t on_write_w1c_field(uint32_t reg_val, uint32_t written, uint32_t mask) {
    // Bits set in 'written' AND covered by 'mask' are cleared in reg_val
    return reg_val & ~(written & mask);
}
```

**Common pitfall:** Software doing `reg->ISR = ~0u` to clear all flags is correct for W1C. A model that treats the ISR as plain RW would instead set all bits to 1, inverting the intended behaviour.

### RC — Read to Clear

Reading the register (or the field) automatically clears it. The cleared value (usually 0) is returned on the next read.

- Typical use: FIFO data registers, latched error counts, event capture registers.

```cpp
uint32_t on_read_rc_field(uint32_t& reg_val, uint32_t mask) {
    uint32_t captured = reg_val & mask;
    reg_val &= ~mask;   // clear on read
    return captured;
}
```

## Access Type Summary Table

| Type | Write Effect | Read Effect | Hardware Can Set? | Typical Use |
|------|-------------|-------------|------------------|-------------|
| RO   | Ignored | Returns HW value | Yes | Status, flags |
| RW   | Stores value | Returns stored value | Sometimes | Config |
| W1C  | Clears bits where 1 written | Returns current value | Yes | IRQ status |
| RC   | No effect | Returns value, then clears | Yes | FIFO data, latched errors |

## Additional Access Types (Reference)

Real datasheets sometimes define more:

- **WO (Write Only)** — reads return 0 or undefined; used for command trigger registers.
- **W1S (Write 1 to Set)** — writing 1 forces the bit high (less common, seen in set/clear register pairs).
- **RW1C** — firmware read/write, but writing 1 clears; equivalent to W1C from software perspective.
- **RWSC (Read/Write, Self-Clearing)** — the bit clears itself one cycle after being written.

## Mixed Access in One Register

A single 32-bit register often contains fields with different access types:

```
UART Interrupt Status Register (ISR) — offset 0x14
  [31:5]  Reserved (RO, reads 0)
  [4]     RXFIFO_OVF — RX FIFO Overflow  (W1C)
  [3]     PARITY_ERR — Parity Error       (W1C)
  [2]     FRAME_ERR  — Frame Error        (W1C)
  [1]     TX_EMPTY   — TX buffer empty    (RO)
  [0]     RX_AVAIL   — RX data available  (RO)
```

The model must apply the correct rule per field, not per register:

```cpp
void UartIsr::on_write(uint32_t val) {
    // W1C fields [4:2]: clear where software writes 1
    uint32_t w1c_mask = 0x1C;
    value_ &= ~(val & w1c_mask);
    // RO fields [1:0] and [31:5]: ignore write entirely
}
```

> **Interview answer:** RO ignores writes, RW stores verbatim, W1C clears bits where software writes 1 (used for interrupt flags), and RC clears the field automatically on each read — getting these right is essential because firmware uses the semantics to acknowledge events and configure hardware correctly.
