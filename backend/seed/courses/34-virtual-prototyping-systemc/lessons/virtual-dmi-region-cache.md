# Direct Memory Interface (DMI) Region Cache

The Direct Memory Interface (DMI) is an optimization in TLM-2.0 that allows an initiator to bypass the socket mechanism for subsequent accesses to a memory region it has already mapped. Instead of issuing a full `b_transport` call for every read or write, the initiator uses a raw pointer directly into the target's memory array.

## The Problem DMI Solves

Without DMI, every memory access — including reads to a large flat ROM — must travel through the complete TLM-2.0 transaction machinery: construct a GP, call `b_transport`, check the response. For a software workload that does millions of instruction fetches per second, this overhead dominates simulation time.

DMI short-circuits this by giving the initiator a host-side pointer, an address range, and an access mask (read, write, or read-write). Once the initiator has a DMI grant, it can read and write directly using `memcpy`, achieving near-native host speed.

## The DMI Cache

An initiator maintains a **DMI cache** — a table of granted regions. Each entry contains:

- `start_address`: first address covered by this DMI region
- `end_address`: last address covered (inclusive)
- `access_type`: `R` (read-only), `W` (write-only), or `RW` (read-write)
- `dmi_ptr`: host pointer to the start of the region (used at runtime)

Before issuing a transaction, the initiator checks the cache:

```
for each entry in dmi_cache:
    if entry.start <= address <= entry.end:
        if access_type matches requested command:
            DMI_HIT → use pointer directly
```

If no entry matches, it is a `DMI_MISS` and a full `b_transport` call is required. After a successful `b_transport`, if `trans.is_dmi_allowed()` is true, the initiator calls `get_direct_mem_ptr` to populate a new cache entry.

## Access Type Matching

The access type in the DMI entry restricts which operations can use it:

| Entry access_type | READ allowed | WRITE allowed |
|-------------------|-------------|---------------|
| R                 | Yes         | No            |
| W                 | No          | Yes           |
| RW                | Yes         | Yes           |

A read request can only use a DMI entry with type `R` or `RW`. A write request can only use a DMI entry with type `W` or `RW`. If the address matches but the access type does not permit the requested operation, it is a `DMI_MISS`.

## DMI Invalidation

The target can invalidate DMI entries at any time by calling `socket->invalidate_direct_mem_ptr(start, end)`. The initiator must then remove all overlapping entries from its DMI cache and fall back to `b_transport` for that range. This happens when:

- A memory-mapped region is remapped (e.g., a bootrom alias removed at runtime)
- A write-protected page becomes writable (e.g., after an unlock sequence)
- The simulation model reconfigures itself

## Implementation Pattern

```cpp
bool initiator::read_u32(uint64_t addr, uint32_t& value) {
    // Check DMI cache first
    for (auto& entry : dmi_cache) {
        if (entry.start <= addr && addr <= entry.end &&
            (entry.type == DMI_READ || entry.type == DMI_RW)) {
            value = *reinterpret_cast<uint32_t*>(
                entry.ptr + (addr - entry.start));
            return true;  // DMI_HIT
        }
    }
    // DMI_MISS: fall back to b_transport
    tlm::tlm_generic_payload trans;
    // ... set up trans ...
    sc_core::sc_time delay = sc_core::SC_ZERO_TIME;
    socket->b_transport(trans, delay);
    if (trans.is_dmi_allowed()) {
        tlm::tlm_dmi dmi_data;
        if (socket->get_direct_mem_ptr(trans, dmi_data)) {
            dmi_cache.push_back({
                dmi_data.get_start_address(),
                dmi_data.get_end_address(),
                dmi_data.get_granted_access(),
                dmi_data.get_dmi_ptr()
            });
        }
    }
    return false;
}
```

## Performance Impact

On a model with a 64 MB flat ROM, enabling DMI can improve instruction-fetch simulation speed by 10–50x compared to pure `b_transport` calls, because every fetch becomes a single pointer dereference on the host rather than a function call through multiple socket layers.

## Reference

For the normative DMI specification:

- **OSCI TLM-2.0 Language Reference Manual** (free PDF from Accellera at https://www.accellera.org/images/downloads/standards/systemc/TLM_2_0_LRM.pdf): Section 10 covers `get_direct_mem_ptr`, `invalidate_direct_mem_ptr`, and `tlm_dmi` in full
- **TLM-2.0 Tutorial Series** (Doulos KnowHow at https://www.doulos.com/knowhow/systemc/tlm-20/): Tutorial 2 demonstrates DMI with a worked example including invalidation

> **Interview answer:** TLM-2.0 DMI lets an initiator obtain a host pointer to a target's memory region, bypassing the socket for subsequent accesses. The initiator maintains a DMI cache keyed by address range and access type (R/W/RW). Cache misses fall back to b_transport; targets can invalidate entries when their memory layout changes.
