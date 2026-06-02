# SPI: Master/Slave Synchronous Bus

SPI (Serial Peripheral Interface) is a four-wire synchronous serial protocol designed for high-speed, short-distance communication between a microcontroller and peripherals such as flash memory, ADCs, DACs, display drivers, and IMUs.

## The Four Wires

| Signal | Direction | Purpose |
|---|---|---|
| `SCLK` | Master → Slave | Clock — master always generates it |
| `MOSI` | Master → Slave | Master Out Slave In |
| `MISO` | Slave → Master | Master In Slave Out |
| `CS` / `SS` | Master → Slave | Chip Select — active low selects one slave |

Because SPI is **full-duplex**, every clock cycle shifts one bit from master to slave on MOSI while simultaneously shifting one bit from slave to master on MISO. A transaction is always a byte-for-byte exchange.

## Clock Polarity and Phase (CPOL/CPHA)

SPI has four "modes" defined by two bits:

| Mode | CPOL | CPHA | Clock idle | Sample on |
|---|---|---|---|---|
| 0 | 0 | 0 | Low | Rising edge |
| 1 | 0 | 1 | Low | Falling edge |
| 2 | 1 | 0 | High | Falling edge |
| 3 | 1 | 1 | High | Rising edge |

Mode 0 is by far the most common. **Mismatching the mode between master and slave is the single most frequent SPI integration bug.**

## A Typical SPI Transaction

```c
// Assert chip select (active low)
GPIO_ODR &= ~(1u << CS_PIN);

// Exchange one byte
SPI1->DR = 0x9F;                        // Write starts the clock
while (!(SPI1->SR & SPI_SR_RXNE));      // Wait for transfer done
uint8_t rx = SPI1->DR;                  // Read received byte

// De-assert chip select
GPIO_ODR |= (1u << CS_PIN);
```

The chip select is **not** controlled by the SPI hardware automatically on most MCUs — you control it with a GPIO. This is intentional: multi-byte transactions must hold CS low across all bytes.

## Key Registers

| Register | Purpose |
|---|---|
| `CR1` | CPOL, CPHA, baud-rate prescaler, master/slave, enable |
| `CR2` | RXNE/TXE interrupt enable, DMA enable |
| `SR` | TXE, RXNE, BSY (bus busy), OVR (overrun) |
| `DR` | Read/write data — 8 or 16 bits depending on `DFF` bit |

## Baud Rate in SPI

SPI clock is derived from the peripheral bus clock divided by a prescaler. On STM32:

```
SCLK = f_PCLK / 2^(BR+1)   where BR ∈ {0..7}
```

For `f_PCLK = 48 MHz` and `BR = 2`: `SCLK = 48 / 8 = 6 MHz`.

## SystemC Model Sketch

```cpp
SC_MODULE(SPIMaster) {
    sc_out<bool> sclk, mosi, cs_n;
    sc_in<bool>  miso;

    // Transfer 8 bits, return received byte
    uint8_t transfer(uint8_t tx_byte) {
        uint8_t rx_byte = 0;
        cs_n.write(false);
        wait(10, SC_NS);

        for (int bit = 7; bit >= 0; --bit) {
            mosi.write((tx_byte >> bit) & 1);
            sclk.write(true);
            wait(half_period_ns, SC_NS);
            rx_byte |= (miso.read() << bit);
            sclk.write(false);
            wait(half_period_ns, SC_NS);
        }

        cs_n.write(true);
        return rx_byte;
    }

    double half_period_ns = 83.3;  // ~6 MHz

    SC_CTOR(SPIMaster) { /* ports already bound */ }
};
```

## Multi-Slave Topologies

Two wiring options exist for connecting multiple slaves:

1. **Independent CS lines** — each slave gets its own CS pin; only one is asserted at a time. Simple and most common.
2. **Daisy-chain** — MISO of one slave feeds MOSI of the next; a single long shift register. Used for LED driver chains, but error-prone because all slaves shift on every clock.

## Common Pitfalls

- **Wrong CPOL/CPHA mode** — signals look correct on a scope but bytes are garbage.
- **Releasing CS too early** — the slave has not finished latching the last bit.
- **Bus contention on MISO** — if two slaves both drive MISO (CS lines not exclusive), the bus is shorted. Always verify only one CS is asserted.
- **DFF (data frame format) mismatch** — master configured for 16-bit frames while software reads 8-bit `DR` — you get two bytes in one read, misaligning the stream.
- **BSY flag** — do not de-configure the SPI peripheral while BSY is set; the shift register is still active.

> **Interview answer:** SPI is a full-duplex, synchronous 4-wire bus (SCLK, MOSI, MISO, CS). Every transaction simultaneously shifts bits in both directions. The mode (CPOL/CPHA) must match between master and slave. CS is typically driven by GPIO, not the SPI hardware, so multi-byte bursts must hold CS low across all bytes.
