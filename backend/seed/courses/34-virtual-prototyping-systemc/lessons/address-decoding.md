# Address Decoding to the Right Target

**Address decoding** is the process of examining a transaction's address and deciding which target (slave) should handle it. In hardware this is done by combinational logic; in a TLM virtual prototype it is done by the interconnect module — the router or bus.

## The Decoding Algorithm

The router holds a table of `(base, size, target_socket)` triples. For every incoming transaction it runs:

```
for each entry in map:
    if entry.base <= txn.address < entry.base + entry.size:
        forward to entry.target_socket
        return
raise ADDRESS_ERROR   // no entry matched
```

This linear scan is fine for small maps (< 50 entries). A production interconnect uses an interval tree or a two-level page table for O(log n) or O(1) lookup.

## Priority Rules

When two entries could match the same address (overlapping regions are a misconfiguration, but some tools support "shadow" regions), a priority field decides the winner. Common rules:

| Priority policy | When used |
|---|---|
| First-match | Entries are sorted; lowest index wins |
| Most-specific-match | Smallest `size` wins (longest-prefix match) |
| Explicit priority field | Each entry carries an integer; highest wins |

## A Minimal TLM Router

```cpp
SC_MODULE(Router) {
    tlm_utils::simple_initiator_socket<Router> flash_socket;
    tlm_utils::simple_initiator_socket<Router> sram_socket;
    tlm_utils::simple_target_socket<Router>    cpu_socket;

    struct Entry {
        uint64_t base, size;
        tlm_utils::simple_initiator_socket<Router>* sock;
    };

    std::vector<Entry> map;

    SC_CTOR(Router) : flash_socket("flash"), sram_socket("sram"),
                      cpu_socket("cpu_in")
    {
        cpu_socket.register_b_transport(this, &Router::b_transport);
        map = {
            { 0x0000'0000, 0x0008'0000, &flash_socket },
            { 0x2000'0000, 0x0002'0000, &sram_socket  },
        };
    }

    void b_transport(tlm::tlm_generic_payload& txn,
                     sc_core::sc_time& delay)
    {
        uint64_t addr = txn.get_address();
        for (auto& e : map) {
            if (addr >= e.base && addr < e.base + e.size) {
                txn.set_address(addr - e.base);   // translate to offset
                (*e.sock)->b_transport(txn, delay);
                txn.set_address(addr);             // restore (optional)
                return;
            }
        }
        txn.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
    }
};
```

Notice `txn.set_address(addr - e.base)` — the router **subtracts the base** before forwarding so the target sees a zero-based offset. This is the most critical line in any router implementation.

## Decode Granularity

Hardware decoders often work at the granularity of a power-of-two block, using bit masks rather than arithmetic:

```cpp
// Example: top 4 bits select the region on a 32-bit bus
uint8_t region = (addr >> 28) & 0xF;
uint32_t offset = addr & 0x0FFF'FFFF;
```

This is cheaper in silicon but forces regions to be naturally aligned power-of-two sizes. TLM routers can use either approach.

## Common Pitfalls

- **Forgetting to translate the address**: The target receives a system-level address instead of an offset, causing bounds-check failures.
- **Not restoring the address after forwarding**: If the payload is reused (e.g., in a loosely-timed model), the modified address corrupts subsequent retries.
- **Linear scan with large maps**: Acceptable in simulation; never acceptable in production FPGA prototyping where latency matters.
- **No default slave**: Unmapped accesses silently succeed with garbage data instead of triggering an error.

## Interview Answer

> "The router iterates its address map, finds the entry whose `[base, base+size)` range contains the transaction address, subtracts the base to produce a target-local offset, and forwards the payload. If no entry matches it returns `TLM_ADDRESS_ERROR_RESPONSE`."
