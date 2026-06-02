# Routing Transactions by Address

Address routing is the first job every bus model performs. Before any data moves, the bus must map the 64-bit (or 32-bit) address in a transaction to a specific target socket. Getting this right prevents accidental aliasing, access violations, and hard-to-reproduce simulation bugs.

## The Address Map

An address map is a table of non-overlapping regions. Each entry records the base address, size, and which target index owns that range.

```cpp
struct Region {
    uint64_t base;
    uint64_t size;
    int      target_index;
    std::string name;  // useful for debug messages
};

std::vector<Region> map_ = {
    {0x0000'0000, 0x0010'0000, 0, "ROM"},    // 1 MB ROM
    {0x2000'0000, 0x0002'0000, 1, "SRAM"},   // 128 KB SRAM
    {0x4000'0000, 0x0001'0000, 2, "UART"},   // 64 KB UART
    {0x4001'0000, 0x0001'0000, 3, "GPIO"},   // 64 KB GPIO
};
```

## The Decode Function

A linear scan is fine for small maps (fewer than 16 entries). For larger SoCs, use a sorted vector and binary search, or a radix trie.

```cpp
int decode(uint64_t addr) {
    for (auto& r : map_) {
        if (addr >= r.base && addr < r.base + r.size)
            return r.target_index;
    }
    return -1; // unmapped — generate error response
}
```

For unmapped addresses, always set the response status on the transaction rather than throwing:

```cpp
if (idx < 0) {
    txn.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
    return;
}
```

## Stripping the Base Address

Targets are typically unaware of their position in the global address map. They expect addresses starting at zero. The bus must subtract the region base before forwarding:

```cpp
void b_transport(tlm::tlm_generic_payload& txn, sc_time& delay) {
    uint64_t global_addr = txn.get_address();
    int idx = decode(global_addr);
    if (idx < 0) { /* error */ return; }

    // Translate to target-local address
    txn.set_address(global_addr - map_[idx].base);
    delay += sc_time(BUS_LATENCY_NS, SC_NS);
    target_socket[idx]->b_transport(txn, delay);

    // Restore global address (good practice for debug)
    txn.set_address(global_addr);
}
```

## DMI (Direct Memory Interface) and Routing

DMI allows initiators to bypass the bus for subsequent accesses to the same region, achieving near-zero-overhead memory reads. The bus must translate DMI hints too:

```cpp
bool get_direct_mem_ptr(tlm::tlm_generic_payload& txn,
                        tlm::tlm_dmi& dmi) {
    int idx = decode(txn.get_address());
    txn.set_address(txn.get_address() - map_[idx].base);
    bool ok = target_socket[idx]->get_direct_mem_ptr(txn, dmi);
    // Translate DMI address range back to global space
    dmi.set_start_address(dmi.get_start_address() + map_[idx].base);
    dmi.set_end_address  (dmi.get_end_address()   + map_[idx].base);
    return ok;
}
```

## Routing Table Configuration Patterns

| Pattern | Description | Trade-off |
|---------|-------------|-----------|
| Static array | Hard-coded at compile time | Fast; inflexible |
| JSON/YAML loaded at runtime | Read from memory map file | Flexible; adds startup cost |
| Constructor parameters | Passed by the testbench | Testbench-driven; reusable |

Always load the map before `sc_start()`. Changing it mid-simulation is undefined behavior in most TLM frameworks.

## Common Pitfalls

- **Overlapping regions**: The first match wins in a linear scan. Overlapping ranges are almost always a modeling error.
- **Off-by-one on size**: Region `{base=0x1000, size=0x100}` covers `0x1000..0x10FF`, not `0x1100`. Use `addr < base + size`, not `<=`.
- **Forgetting to restore the address**: Some initiators re-read `get_address()` after `b_transport` returns. Restore it for traceability.

**Interview answer:** "The bus decode function scans the address map, finds which region contains the transaction address, subtracts the region base to produce a target-local address, then forwards the transaction to the correct target socket — returning an error response for any unmapped address."
