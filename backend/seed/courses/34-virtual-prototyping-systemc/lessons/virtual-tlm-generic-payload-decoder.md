# TLM Generic Payload Decoder

The `tlm_generic_payload` (GP) is the universal transaction object in TLM-2.0. Before any transfer reaches a target, an initiator constructs a GP with the correct fields set. Understanding what makes a GP valid — and what error responses map to which violations — is fundamental to writing correct TLM-2.0 models.

## The Generic Payload Fields

A TLM-2.0 GP carries these key attributes:

| Field | Type | Meaning |
|-------|------|---------|
| `command` | `tlm_command` | `TLM_READ_COMMAND` or `TLM_WRITE_COMMAND` |
| `address` | `uint64` | Destination address (must be non-negative) |
| `data_length` | `unsigned int` | Byte count of the transfer (must be > 0) |
| `response_status` | `tlm_response_status` | Set by target to indicate outcome |

## Response Status Codes

When a target cannot fulfill a transaction, it sets the response status to one of these error codes:

```
TLM_OK_RESPONSE                — Transaction completed successfully
TLM_ADDRESS_ERROR_RESPONSE     — Address is not mapped or invalid
TLM_COMMAND_ERROR_RESPONSE     — Command type not supported by target
TLM_BURST_ERROR_RESPONSE       — Data length or burst parameters invalid
TLM_BYTE_ENABLE_ERROR_RESPONSE — Byte enable mask not supported
TLM_GENERIC_ERROR_RESPONSE     — Unspecified target error
TLM_INCOMPLETE_RESPONSE        — Response not yet set (initial state)
```

## Validation Order Matters

The IEEE 1666 standard defines a priority for error checking. Initiator-side validation typically checks fields in this order:

1. **Command**: must be `READ` or `WRITE` — unrecognized commands get `COMMAND_ERROR`
2. **Address**: must be non-negative — negative addresses get `ADDRESS_ERROR`
3. **Data length**: must be 1–64 bytes inclusive for standard transfers — out-of-range lengths get `BURST_ERROR`

Checking in this order ensures that an initiator receives the most actionable error for the first field that is wrong.

## Canonical Transaction Construction

A correctly constructed write GP looks like this in C++:

```cpp
tlm::tlm_generic_payload trans;
uint8_t buf[4] = {0xDE, 0xAD, 0xBE, 0xEF};

trans.set_command(tlm::TLM_WRITE_COMMAND);
trans.set_address(0x40000000ULL);
trans.set_data_ptr(buf);
trans.set_data_length(sizeof(buf));
trans.set_streaming_width(sizeof(buf));
trans.set_byte_enable_ptr(nullptr);
trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);

sc_core::sc_time delay = sc_core::SC_ZERO_TIME;
socket->b_transport(trans, delay);

if (trans.get_response_status() != tlm::TLM_OK_RESPONSE) {
    SC_REPORT_ERROR("initiator", "Write failed");
}
```

## Address Formatting Convention

TLM-2.0 addresses are 64-bit unsigned integers, but most embedded SoC address maps fit in 32 bits. In simulation logs and diagnostics, addresses are conventionally displayed in uppercase hexadecimal with a `0x` prefix — for example, `0x40000000` rather than `1073741824`.

## Common Mistakes

**Sending an unsupported command**: TLM-2.0 defines only READ and WRITE as standard commands. Custom extensions exist, but a standard target must return `COMMAND_ERROR` for anything else.

**Zero-length transfers**: `data_length = 0` is invalid. Even a zero-byte "probe" transaction should use a debug transport call rather than a zero-length blocking transport.

**Burst parameters too large**: Real bus protocols have maximum burst lengths. A model that enforces a 64-byte maximum is realistic for standard AXI4 burst sizes.

## Reference Materials

For the normative definitions of all GP fields and response codes:

- **OSCI TLM-2.0 Language Reference Manual** (free PDF from Accellera at https://www.accellera.org/images/downloads/standards/systemc/TLM_2_0_LRM.pdf): Section 8 covers `tlm_generic_payload` in full detail
- **TLM-2.0 Tutorial Series** (Doulos KnowHow, free at https://www.doulos.com/knowhow/systemc/tlm-20/): Tutorial 1 and Tutorial 2 walk through GP construction and response handling with runnable code examples

> **Interview answer:** The TLM-2.0 generic payload carries command, address, data pointer, length, byte enables, and response status. Field validation checks command first, then address, then data length. An invalid command returns COMMAND_ERROR; an invalid address returns ADDRESS_ERROR; invalid burst size returns BURST_ERROR.
