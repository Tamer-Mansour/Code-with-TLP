# From a Register Spec to a Working Model

A peripheral datasheet describes registers in natural language and tables. Turning that description into a running SystemC model is a systematic process. This lesson walks through that process end-to-end for a minimal UART peripheral.

## Step 1: Extract the Register Map

Read the datasheet and build a table. For every register record: name, offset, reset value, and brief description.

| Register | Offset | Reset | Description |
|----------|--------|-------|-------------|
| DR | 0x00 | 0x00000000 | Data register (TX write / RX read) |
| SR | 0x04 | 0x00000020 | Status register |
| CR | 0x08 | 0x00000000 | Control register |
| IBRD | 0x24 | 0x00000000 | Integer baud rate divisor |

## Step 2: Expand Each Register into Fields

For every register, extract the bit fields with their access types and reset values.

**SR (Status Register) at offset 0x04:**

| Bits | Field | Access | Reset | Description |
|------|-------|--------|-------|-------------|
| 31:6 | Reserved | RO | 0 | — |
| 5 | TXFE | RO | 1 | TX FIFO empty |
| 4 | RXFF | RO | 0 | RX FIFO full |
| 3 | TXFF | RO | 0 | TX FIFO full |
| 2 | RXFE | RO | 1 | RX FIFO empty |
| 1 | TXBUSY | RO | 0 | TX in progress |
| 0 | OE | W1C | 0 | Overrun error |

## Step 3: Choose a Register Representation

For each register, create a descriptor object. Parameterize it from the table data, not by hand-coding magic numbers throughout the model:

```cpp
Register build_sr_register() {
    Register sr;
    sr.name      = "SR";
    sr.offset    = 0x04;
    sr.reset_val = 0x00000024; // TXFE=1, RXFE=1 at reset

    sr.fields = {
        {"OE",     0, 1, AccessType::W1C, 0},
        {"TXBUSY", 1, 1, AccessType::RO,  0},
        {"RXFE",   2, 1, AccessType::RO,  1},
        {"TXFF",   3, 1, AccessType::RO,  0},
        {"RXFF",   4, 1, AccessType::RO,  0},
        {"TXFE",   5, 1, AccessType::RO,  1},
    };
    sr.reset();
    return sr;
}
```

## Step 4: Wire Up Callbacks

Attach post-write and pre-read callbacks for every register that has side effects:

```cpp
void UartModel::connect_callbacks() {
    // Writing to DR triggers a transmit
    bank_["DR"].post_write_cb = [this](uint32_t v) {
        uint8_t byte = v & 0xFF;
        tx_fifo_.push(byte);
        sr_["TXFE"].hardware_clear(); // TX FIFO no longer empty
        tx_event_.notify(SC_ZERO_TIME);
    };

    // Reading from DR pops a byte from RX FIFO
    bank_["DR"].pre_read_cb = [this]() {
        if (!rx_fifo_.empty()) {
            bank_["DR"].value = rx_fifo_.front();
            rx_fifo_.pop();
            if (rx_fifo_.empty()) sr_["RXFE"].hardware_set();
        }
    };

    // Writing to CR applies UART configuration
    bank_["CR"].post_write_cb = [this](uint32_t v) {
        apply_uart_config(v);
    };
}
```

## Step 5: Implement the b_transport Handler

Route incoming TLM transactions to the register bank:

```cpp
void UartModel::b_transport(tlm::tlm_generic_payload& trans,
                             sc_time& delay) {
    uint32_t offset = static_cast<uint32_t>(trans.get_address());
    uint8_t* ptr    = trans.get_data_ptr();
    uint32_t len    = trans.get_data_length();

    if (trans.get_command() == tlm::TLM_WRITE_COMMAND) {
        uint32_t val = 0;
        memcpy(&val, ptr, std::min(len, 4u));
        bank_.write(offset, val);
    } else {
        uint32_t val = bank_.read(offset);
        memcpy(ptr, &val, std::min(len, 4u));
    }

    trans.set_response_status(tlm::TLM_OK_RESPONSE);
    delay += sc_time(BUS_ACCESS_LATENCY_NS, SC_NS);
}
```

## Step 6: Test Against the Datasheet

Write a simple testbench that exercises boundary conditions documented in the spec:

- Read SR at reset: expect `0x00000024` (TXFE=1, RXFE=1).
- Write 0 to the OE W1C field: verify SR.OE is not cleared.
- Write 1 to the OE W1C field: verify SR.OE is cleared.
- Write a byte to DR and verify the TX callback fires.

```python
# Pseudocode testbench assertions
assert uart.read(SR_OFFSET) == 0x00000024
uart.write(SR_OFFSET, 0x00)  # write 0 to OE: should not clear
assert uart.read(SR_OFFSET) & 0x1 == expected_oe_value
```

## Common Pitfalls When Translating Specs

- **Ambiguous reset values.** If the datasheet says "undefined", pick a value and document it clearly; firmware must not rely on undefined reset state.
- **Missing "hardware-driven" updates.** Some RO bits change value autonomously (e.g., TXBUSY goes high when a byte starts transmitting). Ensure the FSM sets these bits, not just the write callback.
- **Register aliases.** Some UARTs use the same address for DR-read (RX) and DR-write (TX). Implement separate pre-read and post-write handlers for the aliased register rather than sharing a single value variable.

> **Interview answer:** Translating a register spec to a model follows five steps: extract the register map, enumerate bit fields with access types, instantiate descriptor objects from the table data, wire side-effect callbacks, and validate each reset value and access rule with targeted unit tests.
