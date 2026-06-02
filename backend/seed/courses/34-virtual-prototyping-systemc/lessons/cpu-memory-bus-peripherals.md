# CPU, Memory, Bus, and Peripherals at a Glance

This lesson gives a concise, interview-ready summary of each major VP component — what it does, how it is modeled in SystemC/TLM-2.0, and the one trap every developer falls into.

## CPU Model

The CPU model (ISS) is the only module that advances simulation time through instruction execution. It:

- Fetches instructions via **instruction fetch transactions** on the bus.
- Executes them internally (interpret or JIT).
- Issues **data transactions** (load/store) on the bus.
- Raises or accepts **interrupt signals** (`sc_signal<bool>` or `sc_in<bool>`).

```cpp
// Simplified ISS fetch loop
void cpu_model::run() {
    while (true) {
        uint32_t instr = fetch(pc);   // issues b_transport READ
        execute(instr);               // may issue b_transport READ/WRITE
        pc += 4;
        wait(cycle_time);             // advances simulation time
    }
}
```

**Key property:** The ISS sets simulation speed. A fast JIT ISS running at 500 MIPS dominates VP run time — optimize it before anything else.

## Memory Model

| Attribute | Typical value |
|---|---|
| Backing store | `std::vector<uint8_t>` |
| Latency | Annotated on the transaction delay parameter |
| DMI support | Yes — allows ISS to bypass `b_transport` for bulk reads |

DMI (Direct Memory Interface) is the most important memory optimization. Once the ISS receives a DMI pointer it reads/writes memory directly via host pointers, removing the overhead of a `b_transport` call per access.

```cpp
bool mem_target::get_direct_mem_ptr(tlm::tlm_generic_payload &txn,
                                    tlm::tlm_dmi &dmi_data) {
    dmi_data.set_dmi_ptr(&mem[0]);
    dmi_data.set_start_address(0);
    dmi_data.set_end_address(mem.size() - 1);
    dmi_data.allow_read_write();
    return true;
}
```

**Pitfall:** If you write to memory after issuing a DMI grant, you must call `invalidate_direct_mem_ptr` on all initiators or the ISS will see stale data.

## Bus / Interconnect

The bus is a **pass-through router** — it decodes the address, adjusts it, and re-calls `b_transport` on the correct target socket. It adds no functionality beyond routing.

```
Initiator calls:  bus.b_transport(txn, delay)
Bus decodes addr: 0x40000000 → UART (index 2)
Bus adjusts addr: txn.set_address(addr - 0x40000000)
Bus forwards:     uart.b_transport(txn, delay)
```

A well-written bus logs every unmatched address as an error rather than silently returning garbage data.

## Peripheral Models

Peripherals are **register-mapped targets** with side-effects. The standard structure:

1. Receive `b_transport`.
2. Decode to a register offset.
3. Perform the register read or write.
4. Trigger side-effect (e.g., assert an interrupt, push a byte to a FIFO).

```cpp
void uart_model::b_transport(tlm::tlm_generic_payload &txn,
                             sc_core::sc_time &delay) {
    uint64_t offset = txn.get_address();  // already base-subtracted by bus
    uint8_t  data   = *txn.get_data_ptr();

    if (txn.is_write() && offset == TXDATA_REG) {
        std::cout << (char)data;           // side-effect: terminal output
        if (tx_fifo_full()) irq.write(true);
    }
    txn.set_response_status(tlm::TLM_OK_RESPONSE);
}
```

## Component Interaction Summary

```
ISS  ──b_transport──>  Bus  ──b_transport──>  Peripheral
                                              │
                                         side-effect
                                              │
                                       sc_signal<bool>  ──>  ISS (IRQ)
```

## Quick Reference

| Component | TLM role | Key pitfall |
|---|---|---|
| CPU / ISS | Initiator | Forgetting to advance `sc_time` stalls simulation |
| Memory | Target + DMI | Not invalidating DMI after memory write |
| Bus | Target + Initiator | Missing base-address subtraction |
| Peripheral | Target | No response status set → TLM error |

**Interview answer:** In TLM-2.0, the CPU is an initiator, memory and peripherals are targets, and the bus is both. The bus decodes addresses and subtracts the base before forwarding; the peripheral sees only a local register offset. DMI lets the ISS bypass the bus entirely for hot memory regions.
