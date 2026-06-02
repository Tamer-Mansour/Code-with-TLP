# Designing a Memory-Mapped Device Model

Memory-mapped I/O (MMIO) is how software talks to hardware in almost every modern system — from embedded microcontrollers to server-class SoCs. Instead of dedicated I/O instructions, the CPU reads and writes ordinary addresses that happen to route to peripheral registers rather than RAM.

## The Core Idea

A peripheral occupies a contiguous address window in the system bus. Each offset within that window maps to a specific register with defined semantics:

```
Base address 0x1000_0000
  +0x00  UART_DR    (data register — read returns rx byte, write sends tx byte)
  +0x04  UART_FR    (flags register — bit 5 = TX FIFO full, bit 4 = RX FIFO empty)
  +0x08  UART_IBRD  (integer baud rate divisor)
```

Firmware writes `*(volatile uint32_t*)0x10000000 = 'A'` to transmit a character. The VP must intercept that bus transaction and model the correct side effect.

## The Device Interface

Define an abstract base so any peripheral can be plugged into the bus:

```cpp
class Device {
public:
    virtual uint32_t read (uint32_t offset, unsigned size) = 0;
    virtual void     write(uint32_t offset, uint32_t val, unsigned size) = 0;
    virtual void     reset() = 0;
    virtual ~Device() = default;
};
```

`size` carries the access width (1, 2, or 4 bytes) because byte-lane logic matters for some registers.

## A Simple UART Model

```cpp
class UartModel : public Device {
public:
    uint32_t read(uint32_t offset, unsigned /*size*/) override {
        switch (offset) {
        case 0x00: return rx_fifo_.empty() ? 0 : pop_rx();  // DR
        case 0x04: {                                          // FR
            uint32_t fr = 0;
            if (rx_fifo_.empty()) fr |= (1 << 4);  // RXFE
            // TX is always "not full" in our model
            return fr;
        }
        default: return 0;
        }
    }

    void write(uint32_t offset, uint32_t val, unsigned /*size*/) override {
        if (offset == 0x00) {
            // "transmit" — just print to host stdout for now
            std::putchar(static_cast<char>(val & 0xFF));
        }
    }

    void reset() override { rx_fifo_ = {}; }

    // Inject a byte (called by test harness to simulate received data)
    void inject(uint8_t b) { rx_fifo_.push(b); }

private:
    std::queue<uint8_t> rx_fifo_;
    uint8_t pop_rx() { auto b = rx_fifo_.front(); rx_fifo_.pop(); return b; }
};
```

## Side-Effect Registers

Some registers have write-to-clear or read-to-clear semantics. A status register might clear its interrupt flag on read:

```cpp
uint32_t read(uint32_t offset, unsigned /*size*/) override {
    if (offset == STATUS_REG) {
        uint32_t val = status_;
        status_ &= ~IRQ_FLAG;   // reading clears the interrupt flag
        return val;
    }
    // ...
}
```

Document these semantics explicitly — they are the source of most MMIO driver bugs.

## Wiring the Device into the Bus

```cpp
Bus bus;
Memory ram(64 * 1024);
UartModel uart;

bus.map(0x0000'0000, 64 * 1024, &ram);   // RAM at 0x0
bus.map(0x1000'0000,       0x100, &uart); // UART at 0x1000_0000

// Bus dispatch (device variant):
uint32_t Bus::read32(uint32_t addr) {
    for (auto& r : regions_)
        if (addr >= r.base && addr < r.base + r.size)
            return r.dev->read(addr - r.base, 4);
    throw std::runtime_error("unmapped");
}
```

## Testing the Model

Write a tiny test program in the simulated address space:

```cpp
// Inject test bytes into the UART RX FIFO
uart.inject('H'); uart.inject('i');

// Now run firmware that reads UART DR and echoes to TX
// The VP loop will call uart.read(0, 4) and uart.write(0, val, 4)
```

This pattern — **inject stimulus, run ISS, observe output** — is the canonical VP test methodology.

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Treating all registers as plain RAM | Use a `Device` virtual interface |
| Missing byte-lane logic | Pass `size` to `read`/`write` |
| Forgetting `volatile` in firmware (not the VP) | VP models side effects; firmware must use `volatile` pointers |
| No interrupt modeling | Add a `bool has_pending_irq()` to `Device`; poll it each CPU step |

## Interview Answer

> **Interview answer:** "Memory-mapped devices implement a `Device` interface with `read` and `write` methods that capture offset and access size. The bus dispatches transactions to the correct device based on address ranges. Side-effect registers — like those that clear on read — are handled directly in the `read` override, not as plain array lookups."
