# Components of a Virtual Platform

A **virtual platform (VP)** is a software model of a complete hardware system. It executes the same firmware and software as the real chip, but entirely in simulation. Understanding the building blocks is the foundation of every VP project.

## The Six Core Components

| Component | SystemC/TLM Role | Real-hardware analogy |
|---|---|---|
| Processor model | `sc_module` with instruction set simulator (ISS) | CPU die |
| Memory model | Simple initiator/target with array backing | SRAM, DDR |
| Interconnect / Bus | TLM-2.0 router or socket fabric | AXI/AHB bus matrix |
| Peripheral models | Target sockets + register files | UART, Timer, GPIO |
| Clock & Reset | `sc_clock` signals / reset ports | CRU / PLL |
| Platform top | `sc_main` + instantiation glue | Top-level netlist |

## Processor Model

The processor model is the heart of the VP. It drives the simulation by fetching, decoding, and executing instructions. Most VPs use one of two approaches:

- **Interpretive ISS** — executes one instruction per loop iteration; easy to instrument, slow.
- **JIT-compiled ISS** (e.g., QEMU, Synopsys ARC, Imperas OVPsim) — translates guest instructions to host native code; 100–1000x faster.

The ISS acts as a TLM **initiator**: it issues `b_transport` or `nb_transport` calls to fetch instructions and access data.

## Memory Models

Memory models are the simplest targets. They back a `std::vector<uint8_t>` and respond to every read/write within their address range.

```cpp
// Minimal flat memory target
void mem_target::b_transport(tlm::tlm_generic_payload &txn, sc_core::sc_time &delay) {
    uint64_t addr  = txn.get_address();
    uint8_t *ptr   = txn.get_data_ptr();
    uint32_t len   = txn.get_data_length();

    if (txn.is_write())
        memcpy(&mem[addr], ptr, len);
    else
        memcpy(ptr, &mem[addr], len);

    txn.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

**Pitfall:** Forgetting to clamp `addr` to `mem.size()` causes silent out-of-bounds writes that are hard to trace later.

## Interconnect / Bus

The bus routes transactions from one or more initiators to the correct target based on address decoding. In TLM-2.0 terms it owns:

- A `tlm_target_socket` for each upstream initiator.
- A `tlm_initiator_socket` for each downstream target.
- A decode table mapping address ranges to socket indices.

Common pitfalls in the decoder:

1. Overlapping address ranges (causes non-deterministic routing).
2. Off-by-one in range boundaries.
3. Forgetting to subtract the base address before forwarding.

## Peripheral Models

Peripherals expose a register file to the bus and side-effects to the simulation environment (interrupt signals, DMA requests, file I/O for UART). They are **targets** from the bus perspective and often **initiators** toward an interrupt controller.

```
Bus  -->  [UART target socket]  -->  register decode  -->  TX FIFO  -->  sc_fifo  -->  stdout
```

## Clock and Reset

`sc_clock` drives all clocked processes. Reset is typically a plain `sc_signal<bool>`. The platform top asserts reset for a few nanoseconds, then deasserts it so peripherals can initialize in a known state.

## Why This Matters

**Interview answer:** A virtual platform has six layers — ISS, memory, bus/interconnect, peripherals, clock/reset distribution, and a platform top that wires everything together. Each layer maps directly to a SystemC module with TLM-2.0 sockets, making the structure predictable and reusable across projects.

Common interview question: *"What is the difference between an initiator and a target in TLM-2.0?"* An initiator calls `b_transport`; a target implements it. The bus is both — a target to its upstream callers and an initiator to its downstream slaves.
