# Direct Memory Interface (DMI)

The Direct Memory Interface (DMI) is a TLM-2.0 optimization that lets an initiator bypass the socket transport entirely and access a target's backing memory using a raw C++ pointer. Once a DMI region is established, reads and writes become plain `memcpy` calls — no function-call overhead, no phase negotiation, no generic payload allocation.

## Why DMI Exists

Even with temporal decoupling, every `b_transport` call has overhead: argument passing, virtual dispatch, GP field checking. For a CPU model executing millions of instruction fetches per second — all hitting the same RAM — that overhead dominates. DMI removes it by exposing a pointer range:

```
Normal b_transport:     initiator → socket → target (function call per access)
After DMI grant:        initiator → memcpy into raw pointer (zero socket overhead)
```

Real speed-ups of 5x–20x for instruction-fetch-heavy workloads are typical.

## The `tlm_dmi` Descriptor

```cpp
class tlm_dmi {
public:
    enum dmi_access_e {
        DMI_ACCESS_NONE  = 0x00,
        DMI_ACCESS_READ  = 0x01,
        DMI_ACCESS_WRITE = 0x02,
        DMI_ACCESS_READ_WRITE = 0x03
    };

    unsigned char* get_dmi_ptr()   const;
    sc_dt::uint64  get_start_address() const;
    sc_dt::uint64  get_end_address()   const;
    sc_core::sc_time get_read_latency()  const;
    sc_core::sc_time get_write_latency() const;
    dmi_access_e   get_granted_access() const;
};
```

The pointer points directly into the target's backing array. The start/end addresses define the valid range in the target's address space. Latencies let the initiator still annotate time correctly.

## Requesting DMI

Step 1: A `b_transport` call returns with `dmi_allowed == true` — the target hints that DMI is available.

Step 2: The initiator calls `get_direct_mem_ptr`:

```cpp
tlm::tlm_dmi dmi_data;
if (trans.is_dmi_allowed()) {
    bool ok = socket->get_direct_mem_ptr(trans, dmi_data);
    if (ok && (dmi_data.get_granted_access() & tlm::tlm_dmi::DMI_ACCESS_READ)) {
        dmi_ptr   = dmi_data.get_dmi_ptr();
        dmi_start = dmi_data.get_start_address();
        dmi_end   = dmi_data.get_end_address();
        dmi_valid = true;
    }
}
```

Step 3: For subsequent accesses in the same range, bypass the socket:

```cpp
void Cpu::read_word(uint64_t addr, uint32_t& val) {
    if (dmi_valid && addr >= dmi_start && addr + 4 <= dmi_end + 1) {
        memcpy(&val, dmi_ptr + (addr - dmi_start), 4);
        wait(dmi_read_latency);
    } else {
        // Fall back to b_transport
        do_b_transport_read(addr, val);
    }
}
```

## DMI Invalidation

A target can revoke an outstanding DMI grant — for example, when a remapping register is written:

```cpp
// Target invalidates a range
socket->invalidate_direct_mem_ptr(start_addr, end_addr);
```

The initiator's backward path receives this as a callback and must clear its cached DMI data:

```cpp
void Cpu::invalidate_direct_mem_ptr(sc_dt::uint64 start,
                                    sc_dt::uint64 end) {
    if (dmi_start <= end && start <= dmi_end)
        dmi_valid = false;  // region overlaps; discard
}
```

## Worked Example: RAM with DMI

```cpp
void Ram::b_transport(tlm::tlm_generic_payload& trans,
                      sc_core::sc_time& delay) {
    // ... normal read/write logic ...
    trans.set_dmi_allowed(true);   // always hint
    trans.set_response_status(tlm::TLM_OK_RESPONSE);
}

bool Ram::get_direct_mem_ptr(tlm::tlm_generic_payload& trans,
                              tlm::tlm_dmi& dmi) {
    dmi.set_granted_access(tlm::tlm_dmi::DMI_ACCESS_READ_WRITE);
    dmi.set_dmi_ptr(mem);          // raw pointer to backing array
    dmi.set_start_address(0);
    dmi.set_end_address(MEM_SIZE - 1);
    dmi.set_read_latency(sc_core::sc_time(5, sc_core::SC_NS));
    dmi.set_write_latency(sc_core::sc_time(10, sc_core::SC_NS));
    return true;
}
```

## Common Pitfalls

- **Storing the DMI pointer forever** — the target can invalidate it; always check `dmi_valid` before use.
- **Not waiting the latency after a DMI access** — the `memcpy` is instant in simulation time; you still must call `wait(read_latency)` to model timing correctly.
- **Granting DMI for memory-mapped I/O registers** — reads/writes to MMIO may have side effects that DMI bypasses. Only grant DMI for true memory.

> **Interview answer:** DMI is a TLM-2.0 mechanism where the target exposes a raw C++ pointer covering an address range; the initiator uses `memcpy` directly into that pointer for subsequent accesses, eliminating socket overhead — achieving 5-20x speed-ups for instruction-fetch-heavy simulation while still annotating timing through the DMI latency fields.
