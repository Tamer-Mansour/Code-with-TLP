# RAM, ROM, and MMIO Regions

Every address map is divided into three conceptually distinct kinds of regions. Understanding what distinguishes them drives the correct model design.

## RAM — Read-Write Volatile Storage

RAM (Random-Access Memory) holds data that the CPU can both read and write, and whose contents are lost when power is removed. In a virtual prototype:

- Backed by a `std::vector<uint8_t>` initialised to zero (or a reset pattern).
- No side effects on access — a read never changes system state.
- Supports byte-enable masks for sub-word writes.
- May be initialised at elaboration time by loading an ELF data segment.

```cpp
// Write handler for RAM — simplest form
if (txn.get_command() == tlm::TLM_WRITE_COMMAND)
    std::memcpy(&ram[addr], txn.get_data_ptr(), txn.get_data_length());
```

**Common RAM regions on Cortex-M**: DTCM, SRAM1/SRAM2, CCM RAM.

## ROM / Flash — Read-Only or Write-Protected Storage

ROM holds code and const data that should never change at runtime. Flash is technically rewritable through a programming sequence, but behaves as read-only to ordinary load instructions.

Key differences from RAM in the model:

- Write transactions should return `TLM_COMMAND_ERROR_RESPONSE` (or be silently dropped with a warning — platform-dependent).
- The storage vector is initialised from a binary image or ELF file at elaboration.
- Some Flash models implement an erase/program state machine for Flash controller emulation.

```cpp
void b_transport(tlm::tlm_generic_payload& txn, sc_core::sc_time& delay) {
    if (txn.get_command() == tlm::TLM_WRITE_COMMAND) {
        SC_REPORT_WARNING("ROM", "Write to read-only region");
        txn.set_response_status(tlm::TLM_COMMAND_ERROR_RESPONSE);
        return;
    }
    uint64_t addr = txn.get_address();
    std::memcpy(txn.get_data_ptr(), &storage[addr], txn.get_data_length());
    txn.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

## MMIO — Memory-Mapped I/O

MMIO (Memory-Mapped I/O) regions are fundamentally different: **reading or writing an address triggers a hardware side effect**, not just a data transfer. Examples:

| Address | Peripheral | Read effect | Write effect |
|---|---|---|---|
| `0x4002_3814` | GPIOA ODR | Returns current output latch | Sets output pins |
| `0x4001_3008` | SPI1 DR | Reads RX FIFO, may clear RXNE | Loads TX FIFO |
| `0x4000_0000` | TIM2 CR1 | Returns timer config | Starts/stops counter |

### Modelling MMIO

Each peripheral register is best represented as a named field with read and write callbacks:

```cpp
// Simplified UART status register read
uint32_t read_SR() {
    uint32_t val = 0;
    if (!rx_fifo.empty())  val |= (1u << 5);   // RXNE
    if (tx_fifo_has_space()) val |= (1u << 7);  // TXE
    return val;
}

// Simplified UART data register read — side effect!
uint32_t read_DR() {
    uint8_t byte = rx_fifo.front();
    rx_fifo.pop();                               // consumes the byte
    return byte;
}
```

### MMIO Common Pitfalls

- **Caching MMIO**: If the compiler (or a CPU model) caches a read from an MMIO address, it misses state changes. Always declare MMIO pointers `volatile` in firmware, and never cache MMIO reads in the model.
- **Read clears (RC) bits**: Some status bits clear themselves on read. Returning the value before clearing is the correct order.
- **Write-only registers**: Reading a write-only register should return `0` or the reset value, not stored data.
- **Byte vs word access**: Some MMIO registers are only valid for 32-bit accesses. Return a bus error for narrower widths.

## Summary Table

| Property | RAM | ROM/Flash | MMIO |
|---|---|---|---|
| Write allowed | Yes | No (or special) | Yes (side effects) |
| Read side effect | None | None | Often yes |
| Volatile | Yes (power) | No | Yes (always) |
| Backed by | `vector<uint8_t>` | `vector<uint8_t>` | Register callbacks |

## Interview Answer

> "RAM is backed by a byte array with no side effects. ROM rejects writes and loads its image from an ELF or binary file. MMIO models registers as callbacks so that reads and writes trigger peripheral behavior — the storage is the peripheral state, not a flat byte array."
