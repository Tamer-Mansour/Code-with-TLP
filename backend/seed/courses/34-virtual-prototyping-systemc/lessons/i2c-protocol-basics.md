# I2C: Two-Wire Addressed Bus

I2C (Inter-Integrated Circuit, pronounced "I-squared-C") is a two-wire multi-master bus designed by Philips in 1982. It trades raw speed for simplicity of wiring: dozens of devices share the same two lines, each identified by a 7-bit (or 10-bit) address baked into the chip at manufacture.

## The Two Wires

| Signal | Type | Purpose |
|---|---|---|
| `SCL` | Clock | Driven by master; slaves can stretch it (clock stretching) |
| `SDA` | Data | Bidirectional — master or slave drives it depending on direction |

Both lines are **open-drain with pull-up resistors**. Any device can pull a line low; the pull-up pulls it high when nobody is driving. This enables multi-master arbitration and clock stretching without bus fights.

## Standard Speeds

| Mode | Max Speed |
|---|---|
| Standard (Sm) | 100 kHz |
| Fast (Fm) | 400 kHz |
| Fast-Plus (Fm+) | 1 MHz |
| High-Speed (Hs) | 3.4 MHz |

## Protocol Structure

A complete I2C transfer follows this pattern:

```
START | ADDRESS (7 bit) | R/W | ACK | DATA_BYTE | ACK | ... | STOP
```

- **START condition**: SDA falls while SCL is high.
- **Address phase**: master sends 7-bit address + 1 R/W bit; slave with matching address pulls SDA low to ACK.
- **Data phase**: one or more bytes transferred, each acknowledged.
- **STOP condition**: SDA rises while SCL is high.
- **Repeated START (Sr)**: another START without a STOP — changes direction or addresses a new slave without releasing the bus.

## Writing to a Register (e.g., an I2C sensor)

```c
// Write value 0x40 to register 0x1C of device at address 0x68
i2c_start();
i2c_write_byte((0x68 << 1) | 0);   // address + WRITE
i2c_write_byte(0x1C);               // register address
i2c_write_byte(0x40);               // register value
i2c_stop();
```

## Reading from a Register

```c
// Read 2 bytes from register 0x3B of device 0x68
i2c_start();
i2c_write_byte((0x68 << 1) | 0);   // address + WRITE (send reg pointer)
i2c_write_byte(0x3B);
i2c_repeated_start();
i2c_write_byte((0x68 << 1) | 1);   // address + READ
uint8_t hi = i2c_read_byte(ACK);
uint8_t lo = i2c_read_byte(NACK);  // NACK on last byte signals end
i2c_stop();
```

The repeated start + direction change is essential — many I2C slaves only accept register-read this way.

## Key Registers (typical I2C controller)

| Register | Purpose |
|---|---|
| `CCR` | Clock control — sets SCL frequency |
| `CR1` | Enable, START, STOP, ACK, SWRST |
| `CR2` | Peripheral frequency, interrupt enables |
| `SR1` | SB (start sent), ADDR (address matched), TXE, RXNE, AF (ACK failure) |
| `DR` | Data register |

## SystemC Model Sketch

```cpp
SC_MODULE(I2CMaster) {
    sc_inout<bool> scl, sda;

    void send_start() {
        sda.write(false); wait(5, SC_NS);
        scl.write(false); wait(5, SC_NS);
    }

    bool send_byte(uint8_t byte) {
        for (int i = 7; i >= 0; --i) {
            sda.write((byte >> i) & 1);
            scl.write(true);  wait(5, SC_NS);
            scl.write(false); wait(5, SC_NS);
        }
        // Read ACK bit
        sda.write(true);          // release SDA
        scl.write(true);  wait(5, SC_NS);
        bool ack = !sda.read();   // slave pulls low for ACK
        scl.write(false); wait(5, SC_NS);
        return ack;
    }

    SC_CTOR(I2CMaster) { }
};
```

## Clock Stretching

A slow slave can hold `SCL` low after the master releases it, buying time to prepare data. The master must check that SCL has actually gone high before sampling. If the master ignores clock stretching, it will read stale or invalid data.

## Multi-Master Arbitration

Two masters can attempt to transmit simultaneously. Arbitration works because both drive open-drain SDA. If a master drives SDA high but detects SDA low, another master is winning — it backs off immediately. The winning master continues unaware; no data is corrupted.

## Common Pitfalls

- **Missing pull-up resistors** — without them, SDA/SCL can never go high; the bus is stuck low.
- **Address collision** — two devices with the same address on the same bus; behavior is undefined.
- **NACK on last read byte** — the master must NACK the final byte to signal it wants no more data; failing to do so can hang some slaves.
- **ACK failure (AF bit)** — device not present or powered down; software must detect AF and abort.
- **Bus stuck low** — a slave clock-stretching indefinitely after a reset; most I2C controllers have a bus-free timeout to recover.

> **Interview answer:** I2C is a two-wire (SCL + SDA), open-drain, multi-master bus. Each slave has a unique 7-bit address. A transaction is START, address+R/W, ACK, data bytes with ACKs, STOP. Key concerns are pull-up sizing, clock stretching support, and NACK handling for the final read byte.
