# What Is a Memory Model?

A **memory model** is a software abstraction that behaves like physical memory from the perspective of a bus or initiator. In virtual prototyping, every memory-mapped resource — SRAM, Flash, ROM, peripheral registers — is represented by a model that responds to read and write transactions using the same TLM-2.0 interface as the rest of the platform.

## Why Models Instead of Real Hardware?

Physical memories are not available during early architecture exploration. A model lets you:

- Boot firmware and run software before the chip is taped out.
- Inject faults, record access patterns, and assert alignment requirements.
- Replace a simple byte-array model with a timing-accurate DRAM model without changing initiator code — because both implement the same `tlm_fw_transport_if`.

## The Simplest Possible Model

The minimal memory model in SystemC/TLM is a socket-bearing `sc_module` that wraps a `std::vector<uint8_t>`:

```cpp
#include <systemc>
#include <tlm>
#include <tlm_utils/simple_target_socket.h>
#include <vector>
#include <cstring>

SC_MODULE(Memory) {
    tlm_utils::simple_target_socket<Memory> socket;

    explicit Memory(sc_core::sc_module_name name, size_t size)
        : sc_module(name), socket("socket"), storage(size, 0)
    {
        socket.register_b_transport(this, &Memory::b_transport);
    }

    void b_transport(tlm::tlm_generic_payload& txn,
                     sc_core::sc_time& delay)
    {
        sc_dt::uint64  addr   = txn.get_address();
        uint8_t*       ptr    = txn.get_data_ptr();
        unsigned       len    = txn.get_data_length();

        if (addr + len > storage.size()) {
            txn.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
            return;
        }

        if (txn.get_command() == tlm::TLM_WRITE_COMMAND)
            std::memcpy(storage.data() + addr, ptr, len);
        else
            std::memcpy(ptr, storage.data() + addr, len);

        txn.set_response_status(tlm::TLM_OK_RESPONSE);
    }

private:
    std::vector<uint8_t> storage;
};
```

Key observations:

- `get_address()` returns the **offset within this target**, not the system-level address. The router strips the base address before forwarding.
- `get_data_length()` tells you how many bytes are in this transfer. Always bounds-check before indexing.
- Setting `TLM_ADDRESS_ERROR_RESPONSE` propagates a bus-error back to the initiator.

## What a Memory Model Must Handle

| Concern | What to implement |
|---|---|
| Reads and writes | Branch on `get_command()` |
| Byte enables | Check `get_byte_enable_ptr()` for masked writes |
| Bounds checking | Reject addresses past the end of storage |
| Response status | Always call `set_response_status()` |
| Debug transport | Implement `transport_dbg()` for gdbserver support |

## Byte Enables — The Hidden Pitfall

Many beginners ignore byte enables and pass all tests with aligned 4-byte accesses. The moment a compiler emits a `strb` (store-byte) instruction, the byte-enable mask selects which bytes in the word are live. Failing to honor it corrupts adjacent bytes.

```cpp
uint8_t* be  = txn.get_byte_enable_ptr();
unsigned  bel = txn.get_byte_enable_length();
if (be) {
    for (unsigned i = 0; i < len; ++i)
        if (be[i % bel] == TLM_BYTE_ENABLED)
            storage[addr + i] = ptr[i];
} else {
    std::memcpy(storage.data() + addr, ptr, len);
}
```

## Interview Answer

> "A TLM memory model is an `sc_module` with a target socket. It stores a byte array, checks bounds, copies data on reads/writes, and returns a TLM response status. The router translates system addresses to per-target offsets before the transaction arrives."
