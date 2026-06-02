# UART: Asynchronous Serial Communication

UART (Universal Asynchronous Receiver/Transmitter) is one of the oldest and most widely used serial protocols in embedded systems. Its simplicity — just two wires — makes it the go-to choice for debug consoles, GPS modules, Bluetooth adapters, and countless other peripherals.

## How UART Works

UART is **asynchronous**: there is no shared clock line. Both ends agree on a **baud rate** (bits per second) in advance, and each side uses its own oscillator to clock data in and out. The receiver samples each incoming bit in the middle of its bit period to maximize noise margin.

A single UART **frame** looks like this:

```
IDLE  START  D0  D1  D2  D3  D4  D5  D6  D7  PARITY  STOP(S)
 1      0    ...data bits (LSB first)...   opt     1 or 2
```

Key parameters (must match on both ends):

| Parameter | Typical Values |
|---|---|
| Baud rate | 9600, 115200, 921600 |
| Data bits | 7 or 8 |
| Parity | None, Even, Odd |
| Stop bits | 1, 1.5, 2 |

The idle line sits at **logic 1**. A start bit is always **logic 0**, so the receiver detects the falling edge and starts its bit-period timer.

## Key Registers

A typical UART peripheral exposes:

| Register | Purpose |
|---|---|
| `BRD` / `BRR` | Baud-rate divisor — derived from system clock |
| `CR1` / `CTRL` | Control: enable TX/RX, parity, word length |
| `SR` / `STATUS` | Flags: TXE (TX empty), RXNE (RX not empty), ORE (overrun) |
| `DR` / `DATA` | Read to receive a byte, write to transmit a byte |

## Sending a Byte (Polling)

```c
// Wait until TX shift register is empty
while (!(UART0->SR & UART_SR_TXE));

// Write the byte — hardware begins shifting it out
UART0->DR = 'A';
```

## Receiving a Byte (Polling)

```c
// Wait until a byte has been received
while (!(UART0->SR & UART_SR_RXNE));

uint8_t ch = UART0->DR;   // Reading DR clears RXNE
```

**Overrun error (ORE)**: if the software does not read `DR` before the next byte arrives, the new byte overwrites the receive buffer and ORE is set. The previous byte is lost. This is the most common UART bug in polling code — the fix is to use interrupts or DMA.

## Baud-Rate Divisor

The divisor is calculated as:

```
BRD = f_clk / (16 * baud_rate)
```

For example, with `f_clk = 16 MHz` and `baud_rate = 115200`:

```
BRD = 16_000_000 / (16 * 115200) = 8.68
```

Most hardware splits this into integer and fractional parts (e.g., `IBRD = 8`, `FBRD = round(0.68 * 64) = 44` on ARM PL011).

## SystemC Model Sketch

```cpp
SC_MODULE(UARTModel) {
    sc_fifo<uint8_t> tx_fifo{"tx_fifo", 16};
    sc_fifo<uint8_t> rx_fifo{"rx_fifo", 16};

    uint32_t brd = 0;     // baud-rate divisor register
    uint8_t  ctrl = 0;    // control register
    uint8_t  status = 0;  // status register

    // Called by CPU model to write to DATA register
    void write_data(uint8_t byte) {
        if (!tx_fifo.nb_write(byte))
            status |= UART_STATUS_OVR;  // TX overflow
    }

    // Background process shifts bytes out at baud rate
    void tx_process() {
        while (true) {
            uint8_t b;
            tx_fifo.read(b);             // blocks until data available
            double bit_time_ns = 1e9 / (baud_rate());
            wait(10 * bit_time_ns, SC_NS);  // 1 start + 8 data + 1 stop
            // deliver to connected RX model...
        }
    }

    double baud_rate() { return 16e6 / (16.0 * (brd ? brd : 1)); }

    SC_CTOR(UARTModel) {
        SC_THREAD(tx_process);
    }
};
```

## Common Pitfalls

- **Baud-rate mismatch** — even a 2% error can cause framing errors at high baud rates. Always verify divisor calculation with the actual oscillator frequency.
- **Missing stop-bit check** — a framing error means the stop bit was not 1; the frame was corrupted or baud rates are mismatched.
- **Overrun in polling mode** — service the RX register fast enough or switch to interrupt/DMA.
- **RS-232 vs TTL levels** — UART logic is 0/3.3 V (TTL) but RS-232 uses ±12 V; connecting them without a level shifter destroys hardware.

> **Interview answer:** UART is a two-wire, asynchronous serial protocol where both sides pre-agree on baud rate, data bits, parity, and stop bits. The baud-rate divisor is `f_clk / (16 * baud)`. The most common bugs are overrun errors (from not reading the data register fast enough) and baud-rate mismatch causing framing errors.
