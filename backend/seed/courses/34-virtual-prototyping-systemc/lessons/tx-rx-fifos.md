# Modeling TX/RX FIFOs

The TX and RX FIFOs are the heart of a UART model. Without them, every character transfer would stall the simulated CPU. With them, a driver can burst a string into the TX FIFO and return to other work while the model forwards bytes to the host asynchronously.

## Why Separate FIFOs Are Essential

Real UART hardware has two independent 16-byte (or 64-byte) FIFOs — one for transmission, one for reception. The separation is not cosmetic: the TX FIFO drains toward the wire while the RX FIFO fills from the wire. If you model both with a single buffer you will see data corruption the moment TX and RX overlap.

```
CPU Bus
  │
  ▼
┌─────────────────────────────────────┐
│  THR write ──► TX FIFO ──► host I/O │
│                                     │
│  host I/O ──► RX FIFO ──► RHR read │
└─────────────────────────────────────┘
```

## Choosing a Container

In SystemC, the FIFO is a plain `std::queue<uint8_t>` in practice. The 16550 standard specifies a depth of 16 bytes when FIFO mode is enabled (FCR bit 0 = 1) and an effective depth of 1 byte when FIFO mode is off.

```cpp
#include <queue>
#include <cstdint>

class UartFifo {
public:
    explicit UartFifo(size_t depth) : depth_(depth) {}

    bool push(uint8_t byte) {
        if (queue_.size() >= depth_) return false; // overflow
        queue_.push(byte);
        return true;
    }

    bool pop(uint8_t &byte) {
        if (queue_.empty()) return false;
        byte = queue_.front();
        queue_.pop();
        return true;
    }

    bool empty()  const { return queue_.empty(); }
    bool full()   const { return queue_.size() >= depth_; }
    size_t size() const { return queue_.size(); }
    void   reset()      { while (!queue_.empty()) queue_.pop(); }

private:
    std::queue<uint8_t> queue_;
    size_t              depth_;
};
```

## TX Path: Write to Transmit

When the driver writes to THR:

1. **FIFO not full** — push the byte and continue. If FIFO mode is disabled the depth is 1, so a second write before the first drains is an overrun.
2. **FIFO full** — in real hardware the write is silently lost (the driver is supposed to check LSR bit 5 first). In the model, set LSR bit 1 (OE) and optionally log a warning.
3. **Trigger transmission** — in SystemC use an `sc_event` to wake the TX thread, or call `flush_tx()` directly if your model is single-threaded.

```cpp
// TX thread — runs in a separate SC_THREAD
void UartModel::tx_thread() {
    while (true) {
        wait(tx_event_);
        uint8_t byte;
        while (tx_fifo_.pop(byte)) {
            host_write(byte);          // send to PTY / socket / stdout
            wait(tx_byte_time_);       // optional: model baud-rate delay
        }
        update_lsr();
        if (ier_ & 0x02) irq_line_.write(true); // THREI
    }
}
```

## RX Path: Fill from Host

Incoming bytes arrive from the host (a PTY, socket, or test bench) and must be pushed into the RX FIFO:

```cpp
void UartModel::rx_push(uint8_t byte) {
    if (!rx_fifo_.push(byte)) {
        lsr_ |= 0x02; // Overrun Error — existing data was lost
        return;
    }
    lsr_ |= 0x01;  // Data Ready
    check_rx_trigger();
}

void UartModel::check_rx_trigger() {
    size_t trigger = rx_trigger_level();   // 1, 4, 8, or 14 from FCR bits 6-7
    if (rx_fifo_.size() >= trigger && (ier_ & 0x01)) {
        irq_line_.write(true);             // Received Data Available Interrupt
    }
}
```

## Trigger Levels and Interrupt Latency

The RX trigger level controls when the RDAI interrupt fires. A trigger of 1 gives the lowest latency (interrupt on every received byte) while 14 maximizes throughput by batching interrupts. Most embedded drivers set trigger=1 for simplicity.

| FCR bits [7:6] | Trigger level |
|---|---|
| 00 | 1 byte |
| 01 | 4 bytes |
| 10 | 8 bytes |
| 11 | 14 bytes |

## LSR Updates After Every FIFO Change

The LSR must always reflect the current FIFO state. Centralizing this in one function prevents bugs:

```cpp
void UartModel::update_lsr() {
    // Bit 0: Data Ready
    if (rx_fifo_.empty()) lsr_ &= ~0x01; else lsr_ |= 0x01;
    // Bit 5: TX Holding Register Empty
    if (tx_fifo_.empty()) lsr_ |= 0x20;  else lsr_ &= ~0x20;
    // Bit 6: TX Empty (both TX FIFO and shift register empty)
    if (tx_fifo_.empty()) lsr_ |= 0x40;  else lsr_ &= ~0x40;
}
```

**Interview answer:** A virtual UART needs two independent `std::queue<uint8_t>` FIFOs (TX and RX) each bounded by the FIFO depth from FCR. After every push or pop, the model updates the LSR and evaluates whether an interrupt should fire based on IER and the RX trigger level.

## Common Pitfalls

- **Single-buffer model** — sharing one buffer for TX and RX causes corruption under concurrent use.
- **Not resetting FIFOs on FCR write** — if FCR bits 1 and 2 are ignored, stale data persists after the driver resets the UART.
- **Trigger level computed once** — the trigger level can change at runtime; re-read FCR bits on every RX push.
- **Overrun silently dropped** — setting LSR OE but not notifying the driver (via the Line Status interrupt) hides a bug the driver is designed to handle.
