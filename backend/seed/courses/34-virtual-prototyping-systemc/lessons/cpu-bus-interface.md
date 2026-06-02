# The CPU's Bus Interface

Every CPU needs to reach memory and peripherals. In a SystemC TLM-2.0 virtual prototype, this connection is called the **bus interface** — the layer that translates the CPU model's internal load/store operations into TLM transactions on the system interconnect. Getting this interface right determines whether the platform can be composed, reused, and substituted with a real CPU driver without touching peripheral models.

## The TLM-2.0 Initiator Socket

In TLM-2.0 terminology, the CPU is always the **initiator** of bus transactions. It holds an `initiator socket`:

```cpp
#include <tlm.h>
#include <tlm_utils/simple_initiator_socket.h>

SC_MODULE(RISCVCPU) {
    // The single outward-facing bus port
    tlm_utils::simple_initiator_socket<RISCVCPU> ibus; // instruction bus
    tlm_utils::simple_initiator_socket<RISCVCPU> dbus; // data bus

    // ... register file, PC, etc.
};
```

Some designs share a single socket for instructions and data (Harvard-style separation is handled upstream by the interconnect or MMU model); others use two sockets as shown above.

## Translating a Load/Store to a TLM Transaction

When the ISS decode step encounters a load (`LW`) or store (`SW`) instruction, it calls a helper that packages the access as a `tlm_generic_payload` and forwards it via `b_transport` (blocking transport):

```cpp
uint32_t cpu_read32(RISCVCPU* cpu, uint32_t addr) {
    tlm::tlm_generic_payload trans;
    uint32_t data = 0;

    trans.set_command(tlm::TLM_READ_COMMAND);
    trans.set_address(addr);
    trans.set_data_ptr(reinterpret_cast<unsigned char*>(&data));
    trans.set_data_length(4);
    trans.set_streaming_width(4);
    trans.set_byte_enable_ptr(nullptr);
    trans.set_dmi_allowed(false);
    trans.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);

    sc_core::sc_time delay = sc_core::SC_ZERO_TIME;
    cpu->dbus->b_transport(trans, delay);

    if (trans.get_response_status() != tlm::TLM_OK_RESPONSE) {
        cpu->raise_bus_fault(addr);
    }
    return data;
}
```

The `delay` parameter carries the local time offset accumulated by temporal decoupling. The ISS adds notional bus latency to it rather than blocking SystemC simulation time on every access.

## Direct Memory Interface (DMI) for Speed

Crossing the TLM socket boundary on every instruction fetch is expensive. TLM-2.0 provides the **Direct Memory Interface (DMI)**: after a successful transaction, the target may grant the initiator a raw host pointer to its backing storage, valid for a range of addresses.

```cpp
// After the first fetch to a ROM region, request DMI
tlm::tlm_dmi dmi_data;
if (cpu->ibus->get_direct_mem_ptr(trans, dmi_data)) {
    // Cache the host pointer for fast fetch
    uint8_t* rom_ptr = dmi_data.get_dmi_ptr();
    sc_dt::uint64 start = dmi_data.get_start_address();
    // Now fetch is just: instr = *(uint32_t*)(rom_ptr + (pc - start))
}
```

DMI reduces instruction-fetch overhead from a full `b_transport` call to a single pointer dereference. For ROM regions (bootloader, firmware), this is effectively free. Writable regions must invalidate DMI pointers when the backing memory is written.

## Instruction Fetch vs. Data Access

A CPU with separate I-bus and D-bus sockets allows the interconnect to route them independently:

- The **I-bus** typically only issues `TLM_READ_COMMAND` accesses, aligned to the instruction word size.
- The **D-bus** issues both reads and writes with variable widths (byte, halfword, word).

This separation lets the memory map enforce execute-never (XN) permissions at the interconnect level: a peripheral slave wired only to the D-bus will never be reached by a speculative instruction fetch.

## Handling Bus Errors

Not every address is mapped. When the interconnect cannot route a transaction, it must return `TLM_ADDRESS_ERROR_RESPONSE` or `TLM_GENERIC_ERROR_RESPONSE`. The CPU interface checks the response status and raises the appropriate machine exception (e.g., Load Access Fault in RISC-V, Data Abort in Arm).

```cpp
if (trans.get_response_status() == tlm::TLM_ADDRESS_ERROR_RESPONSE) {
    // RISC-V: set mcause = LOAD_ACCESS_FAULT, mepc = PC, jump to trap handler
    take_exception(cpu, CAUSE_LOAD_ACCESS_FAULT, addr);
}
```

## Common Pitfalls

- **Not initializing all payload fields**: TLM-2.0 mandates `streaming_width == data_length` for simple single-beat accesses. Leaving it at zero causes subtle bugs in some interconnect models.
- **Accumulating delay without waiting**: If the CPU keeps adding to `delay` without calling `wait(delay)`, it can run arbitrarily far ahead of SystemC time, breaking peripherals that depend on real-time ordering.
- **Ignoring DMI invalidation**: If another initiator writes to a region for which the CPU holds a DMI pointer, the CPU will read stale data. Always register a DMI invalidation callback.

## Interview Answer

> "The CPU's bus interface in a TLM-2.0 platform is an initiator socket. Every load and store instruction generates a `tlm_generic_payload` and calls `b_transport` on that socket. DMI optimization lets the CPU cache a raw host pointer to backing memory, eliminating the socket-crossing overhead for read-only regions like ROM."
