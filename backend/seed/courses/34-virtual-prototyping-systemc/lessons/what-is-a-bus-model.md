# What Is a Bus/Interconnect Model?

A **bus** is the communication backbone of any System-on-Chip. It carries addresses, data, and control signals between initiators (CPUs, DMAs) and targets (memories, peripherals). In virtual prototyping, modeling the bus correctly determines whether your simulation reflects real timing, contention, and bandwidth behavior.

## Why Model the Bus at All?

At RTL level, a bus is thousands of flip-flops and muxes. That level of detail is too slow for system-level exploration. Virtual prototyping uses **Transaction-Level Modeling (TLM)** — a bus is represented as a C++ object that accepts transaction objects and forwards them to the right target. The result is a model that runs orders of magnitude faster while preserving enough timing accuracy to catch real architectural problems.

**Key questions the bus model must answer:**

- Which target owns a given address?
- How long does a transaction take (latency)?
- What happens when two initiators want the bus at the same time (arbitration)?
- How wide is the data path and how does it affect throughput?

## Anatomy of a TLM Bus Model

A minimal TLM-2.0 bus model in SystemC has three parts:

```cpp
// 1. Slave socket array — one per connected initiator
tlm_utils::simple_target_socket<Bus> initiator_socket[NUM_INITIATORS];

// 2. Master socket array — one per connected target
tlm_utils::simple_initiator_socket<Bus> target_socket[NUM_TARGETS];

// 3. Address map table
struct Region { uint64_t base, size; int target_index; };
std::vector<Region> address_map;
```

When an initiator calls `b_transport()` on the bus's target socket, the bus:

1. Decodes the address to find the target index.
2. Applies bus latency to the `delay` parameter.
3. Forwards the call to the correct master socket.

```cpp
void b_transport(tlm::tlm_generic_payload& txn, sc_time& delay) {
    uint64_t addr = txn.get_address();
    int idx = decode(addr);          // address decode
    delay += SC_NS(BUS_LATENCY_NS);  // add bus overhead
    target_socket[idx]->b_transport(txn, delay); // forward
}
```

## Blocking vs. Non-Blocking Transport

| Mode | API call | Use case |
|------|----------|----------|
| Blocking (AT loosely timed) | `b_transport()` | Fast simulation, correct order |
| Non-blocking (AT timed) | `nb_transport_fw/bw()` | Pipelined protocols, split transactions |

Most bus models start with blocking transport. Non-blocking is needed when modeling out-of-order completion or split-transaction buses like AXI.

## Common Pitfalls

- **Forgetting address offsets**: Targets expect addresses relative to their base, not the global address. Strip the base before forwarding: `txn.set_address(addr - region.base)`.
- **Ignoring byte-enable**: Wide buses may carry partial writes. Always check `get_byte_enable_ptr()`.
- **Shared mutable state without synchronization**: If two threads call `b_transport` simultaneously, non-thread-safe data structures corrupt silently.

## The "Why" in One Line

> A TLM bus model replaces thousands of RTL wires with a C++ function call that decodes addresses, enforces timing, and routes transactions — giving you a simulation fast enough for software bring-up.

**Interview answer:** "A TLM bus model is a SystemC module with initiator and target sockets, an address map, and transport methods. It decodes each transaction's address, adds bus latency to the delay parameter, and forwards the call to the correct target socket — abstracting RTL wire-level detail while preserving architectural timing."
