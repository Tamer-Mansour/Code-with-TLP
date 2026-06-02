# Modeling Other I/O Devices

The UART is one of many character-oriented I/O devices you will encounter in virtual platforms. The design patterns you applied to the UART — register decode, FIFO modeling, interrupt generation, and backend abstraction — generalize directly to other peripheral models.

## The General Pattern for Any Peripheral

Every memory-mapped peripheral in a virtual platform follows the same structure:

```
1. TLM target socket → b_transport() → register decode
2. Internal state (shadow registers, FIFOs, state machines)
3. Interrupt output line (sc_out<bool>)
4. Backend or stimulus interface (what the peripheral "does" externally)
```

Mastering this pattern means you can model any peripheral, not just a UART.

## GPIO Controller

A GPIO controller maps each pin to a bit in a data register and a direction register:

| Register | Purpose |
|---|---|
| DATA | Read current pin state / write output value |
| DIR | 1 = output, 0 = input |
| IE | Interrupt enable per pin |
| IS | Interrupt status (write 1 to clear) |

The "backend" for GPIO is either a test bench signal or an external device model (e.g., a button, LED, or SPI device).

```cpp
void GpioModel::b_transport(tlm::tlm_generic_payload &t, sc_core::sc_time &d) {
    uint32_t offset = t.get_address() & 0xF;
    uint32_t *data  = reinterpret_cast<uint32_t*>(t.get_data_ptr());
    if (t.get_command() == tlm::TLM_WRITE_COMMAND) {
        if (offset == 0) { data_reg_ = *data & ~dir_reg_; apply_outputs(); }
        if (offset == 4) { dir_reg_ = *data; }
    } else {
        if (offset == 0) *data = sample_inputs() | (data_reg_ & dir_reg_);
    }
}
```

## SPI Controller

SPI has four signals (MOSI, MISO, SCK, CS). The virtual model:

1. Accumulates bits in a shift register when CS is asserted.
2. Completes a byte (or word) transfer after N clock cycles.
3. Places the received byte in an RX FIFO and signals an interrupt.

The SPI model's backend is typically a slave device model (SPI flash, SPI sensor). The backend implements a simple `transfer(uint8_t mosi) -> uint8_t miso` function.

```cpp
uint8_t SpiModel::do_transfer(uint8_t tx_byte) {
    if (slave_) return slave_->transfer(tx_byte);
    return 0xFF;   // no slave → all ones (bus idle state)
}
```

## I2C Controller

I2C is more complex because it has a state machine (IDLE → START → ADDRESS → ACK → DATA → STOP). The virtual model must track the phase:

```
States: IDLE, START, ADDR, ADDR_ACK, DATA_W, DATA_ACK, DATA_R, STOP
```

The backend is an I2C slave device (sensor, EEPROM). Most virtual platform teams implement a small I2C bus fabric that routes transactions to the correct slave based on the 7-bit address.

## Timer / Counter

A timer is one of the simplest peripherals to model:

```cpp
SC_HAS_PROCESS(TimerModel);
TimerModel::TimerModel(sc_core::sc_module_name n) : sc_core::sc_module(n) {
    SC_THREAD(tick_thread);
}
void TimerModel::tick_thread() {
    while (true) {
        wait(period_);              // sc_time derived from prescaler register
        if (--counter_ == 0) {
            if (ie_) irq_.write(true);
            if (mode_ == AUTO_RELOAD) counter_ = reload_;
        }
    }
}
```

The period is recalculated whenever the prescaler or reload registers are written.

## DMA Controller

A DMA model reads from a source address and writes to a destination address using TLM initiator transactions — the UART model is often the DMA destination:

```cpp
void DmaModel::dma_thread() {
    while (true) {
        wait(trigger_event_);
        for (uint32_t i = 0; i < count_; ++i) {
            uint8_t byte = mem_read(src_addr_ + i);
            mem_write(dst_addr_ + i, byte);    // dst might be UART THR
        }
        irq_.write(true);                      // DMA complete interrupt
    }
}
```

## Reuse Through Composition

Complex SoC peripherals are composed from simpler ones:

- **USB serial** = UART-like character interface + USB PHY model + descriptor ROM
- **SD card controller** = SPI-like shift register + block-level storage backend
- **CAN controller** = shift register + arbitration state machine + message FIFO

Each layer adds only the state and logic unique to that protocol, reusing the FIFO and interrupt patterns from below.

## Side-by-Side Comparison

| Peripheral | Primary FIFO | Interrupt Trigger | Backend |
|---|---|---|---|
| UART | RX/TX byte FIFO | RX threshold, TX empty | Console, PTY, socket |
| SPI | Word FIFO | Transfer complete | Slave device model |
| I2C | Byte FIFO | ACK/NACK, stop | Slave device model |
| GPIO | 1-bit per pin (no FIFO) | Edge or level per pin | Test bench signal |
| Timer | N/A | Counter underflow | N/A |

**Interview answer:** Every memory-mapped I/O device follows the same virtual platform pattern: a TLM target socket decodes register accesses into internal state, a FIFO buffers data, an interrupt line reflects status, and a backend interface connects to whatever the device "talks to" externally. Once you understand the UART model, you can build any peripheral by adapting these four elements.

## Common Pitfalls

- **Assuming all peripherals are byte-wide** — SPI may transfer 8 or 16 bits; I2C transfers 8 bits plus an ACK; DMA may copy 32-bit words. Use the `get_data_length()` field of the TLM payload to handle variable-width accesses.
- **Hardcoded interrupt number** — connect IRQ lines through a platform-level interrupt map so the same peripheral model can be reused at different addresses and interrupt numbers in different SoC configurations.
- **Missing reset logic** — every model needs an explicit `reset()` method that returns all registers and FIFOs to power-on defaults, so test benches can reset and re-run without restarting the simulation.
