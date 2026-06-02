# Modeling Registers and Memory Maps in a Prototype

Every peripheral in a System-on-Chip exposes behavior through memory-mapped registers. To boot an OS on a virtual prototype you must model these registers accurately — correct reset values, read/write side effects, and address decoding. This lesson covers the patterns used in production virtual prototypes.

## The Memory Map

A **memory map** describes which physical addresses correspond to which resources — DRAM, ROM, peripherals, configuration space. The OS and bootloader rely on this map (often described in a Device Tree or ACPI table) to know where to find each peripheral.

```
0x0000_0000 – 0x0000_FFFF   Boot ROM (read-only)
0x0200_0000 – 0x0200_000B   CLINT (timer, IPI)
0x0C00_0000 – 0x0FFF_FFFF   PLIC (interrupt controller)
0x1000_0000 – 0x1000_00FF   UART 16550
0x8000_0000 – 0xFFFF_FFFF   DRAM
```

Unimplemented regions must not silently return 0. A correct model returns a bus error (raises a fault) or logs a warning, because silent success masks firmware bugs.

## Modeling a Single Register

Each register has attributes:

| Attribute | Example |
|---|---|
| Reset value | `0x0000_0000` |
| Access type | RO, WO, RW, W1C, RC |
| Side effects | Write to TX_DATA triggers UART send |
| Sticky bits | Status bits cleared only by W1C (write-1-to-clear) |

```cpp
// C++ register model with W1C support
class StatusReg {
    uint32_t value_ = 0;
public:
    uint32_t read()  { uint32_t v = value_; return v; }
    void     write(uint32_t data) {
        // W1C bits: writing 1 clears the bit
        value_ &= ~data;
    }
    void set_bit(int bit) { value_ |= (1u << bit); } // called by HW model
};
```

A common mistake is modeling all registers as plain memory — this breaks any OS that depends on W1C semantics to acknowledge interrupts.

## TLM-2.0 Socket and Address Decoder

In SystemC/TLM, peripherals expose a **target socket**. The interconnect (bus fabric model) decodes the incoming address and routes the transaction to the correct peripheral.

```cpp
void BusFabric::b_transport(tlm::tlm_generic_payload &trans, sc_time &t) {
    sc_dt::uint64 addr = trans.get_address();
    if (addr >= 0x10000000 && addr < 0x10000100) {
        uart_->b_transport(trans, t);
    } else if (addr >= 0x80000000) {
        dram_->b_transport(trans, t);
    } else {
        trans.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
    }
}
```

## Device Tree and Register Offsets

Linux discovers peripheral locations from the **Device Tree Blob (DTB)**. Each node lists the base address and size:

```dts
uart0: serial@10000000 {
    compatible = "ns16550a";
    reg = <0x0 0x10000000 0x0 0x100>;
    clock-frequency = <3686400>;
    interrupts = <10>;
};
```

Your virtual prototype model must accept transactions at exactly the address range specified in the DTB — otherwise the driver will write to an unimplemented region and either hang or fault.

## Worked Example: UART TX Register

A 16550-compatible UART has THR (Transmit Holding Register) at offset 0x00 and LSR (Line Status Register) at offset 0x05.

```c
// Minimal 16550 model (C pseudocode)
void uart_write(uint32_t offset, uint8_t data) {
    switch (offset) {
        case 0x00:  // THR
            putchar(data);          // print to host console
            lsr |= (1 << 5);        // THRE: transmitter empty
            lsr |= (1 << 6);        // TEMT: transmitter idle
            break;
        case 0x01:  // IER
            ier = data;
            break;
        case 0x03:  // LCR
            lcr = data;
            break;
    }
}

uint8_t uart_read(uint32_t offset) {
    switch (offset) {
        case 0x05: return lsr;      // firmware polls bit 5 for TX ready
        default:   return 0;
    }
}
```

> **Interview answer:** A MMIO peripheral model routes bus transactions by address offset to per-register handlers that implement reset values, access-type semantics (RO/WO/W1C), and side effects like triggering an interrupt or DMA transfer.

## Common Pitfalls

- **Wrong reset values** — a peripheral whose control register resets to 0 but the spec says 0x1 will confuse drivers that skip initialization.
- **Missing read side effects** — reading UART RBR should consume the byte from the FIFO and potentially clear the Data Ready bit.
- **Address aliasing** — some peripherals mirror their register bank every N bytes; forgetting this breaks drivers that use non-canonical offsets.
- **Byte-lane enables** — a 32-bit bus may carry byte-enable signals; ignoring them causes incorrect partial writes.

Accurate register modeling is what separates a prototype that boots Linux from one that hangs at the console driver initialization.
