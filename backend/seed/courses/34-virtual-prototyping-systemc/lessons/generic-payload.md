# The Generic Payload

The `tlm_generic_payload` (GP) is TLM-2.0's universal transaction object. Every transfer — read, write, burst — is described by one GP instance. Its fields map to the information a real bus protocol carries, abstracted just enough to be protocol-neutral while remaining simulation-efficient.

## Field Reference

| Field | Setter/Getter | Meaning |
|---|---|---|
| `tlm_command` | `set_command` / `get_command` | `TLM_READ_COMMAND`, `TLM_WRITE_COMMAND`, or `TLM_IGNORE_COMMAND` |
| `sc_dt::uint64 address` | `set_address` / `get_address` | Target address in the system memory map |
| `unsigned char* data_ptr` | `set_data_ptr` / `get_data_ptr` | Pointer to the data buffer |
| `unsigned int data_length` | `set_data_length` / `get_data_length` | Total byte count of the transaction |
| `unsigned char* byte_enable_ptr` | `set_byte_enable_ptr` | Byte-enable mask; `nullptr` means all bytes active |
| `unsigned int byte_enable_length` | `set_byte_enable_length` | Length of the byte-enable buffer |
| `unsigned int streaming_width` | `set_streaming_width` | Bytes per beat in a streaming/burst transfer |
| `bool dmi_allowed` | `set_dmi_allowed` / `is_dmi_allowed` | Target hints that DMI is available |
| `tlm_response_status` | `set_response_status` / `get_response_status` | Outcome of the transaction |

## Initializing a GP Correctly

Skipping any field can cause subtle bugs. A canonical write transaction looks like this:

```cpp
uint32_t data = 0xDEADBEEF;
tlm::tlm_generic_payload trans;
sc_core::sc_time delay = sc_core::SC_ZERO_TIME;

trans.set_command(tlm::TLM_WRITE_COMMAND);
trans.set_address(0x4000'0000ULL);
trans.set_data_ptr(reinterpret_cast<unsigned char*>(&data));
trans.set_data_length(sizeof(data));
trans.set_streaming_width(sizeof(data));  // no streaming burst
trans.set_byte_enable_ptr(nullptr);       // all bytes enabled
trans.set_dmi_allowed(false);
trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);

initiator_socket->b_transport(trans, delay);

if (trans.get_response_status() != tlm::TLM_OK_RESPONSE)
    SC_REPORT_ERROR("GP", "Write failed");
```

Setting `response_status` to `TLM_INCOMPLETE_RESPONSE` before the call and checking it afterward is the standard handshake. A target must write back a meaningful status.

## Response Status Values

```
TLM_OK_RESPONSE            — Success
TLM_INCOMPLETE_RESPONSE    — Not yet set (initial / in-flight)
TLM_GENERIC_ERROR_RESPONSE — Unspecified error
TLM_ADDRESS_ERROR_RESPONSE — Address not mapped
TLM_COMMAND_ERROR_RESPONSE — Command not supported
TLM_BURST_ERROR_RESPONSE   — Burst parameters invalid
TLM_BYTE_ENABLE_ERROR_RESPONSE — Byte-enable not supported
```

## Streaming Bursts

`streaming_width < data_length` signals a streaming burst: the target wraps the address every `streaming_width` bytes. For example, a 16-byte write with `streaming_width = 4` means four consecutive 4-byte beats all to the same 4-byte-aligned address range, useful for modeling FIFO-like peripherals.

## Memory Management and Ownership

The GP uses a reference-counting scheme based on `acquire()` / `release()`:

```cpp
// Allocate from the pool (preferred, avoids heap churn)
tlm::tlm_generic_payload* p = mm.allocate();
p->acquire();

// ... fill and send ...

p->release();  // returned to pool when ref count reaches zero
```

When you pass a GP through multiple sockets or store it, always `acquire()` before storing and `release()` when done. Forgetting `release()` leaks memory; calling it too early causes use-after-free crashes.

## Byte Enables

Byte enables mimic the `BE` signals on real buses (e.g., AXI WSTRB). Each bit in the byte-enable buffer corresponds to one byte of the data buffer. A value of `0xFF` means the byte is active; `0x00` means it is masked off. The byte-enable buffer repeats cyclically over the data length:

```cpp
uint8_t be[4] = {0xFF, 0xFF, 0x00, 0x00};  // write only bytes 0 and 1
trans.set_byte_enable_ptr(be);
trans.set_byte_enable_length(4);
```

## Common Pitfalls

- **Reusing a GP without resetting fields** — previous values leak into the new transaction. Either zero-initialize or set every field before each call.
- **Storing a raw pointer instead of acquiring** — another module may release the GP and return it to the pool while you still hold a dangling pointer.
- **Ignoring `streaming_width`** — targets that do not handle `streaming_width != data_length` correctly silently produce wrong data for burst transfers.

> **Interview answer:** The TLM-2.0 generic payload is a protocol-neutral struct containing command, address, data pointer, length, byte-enables, streaming width, and response status; all TLM-2.0 components exchange this object through sockets, enabling interoperability without per-protocol adapters.
