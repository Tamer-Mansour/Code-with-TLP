# The Reset Vector and First Instruction

The **reset vector** is the address the CPU's program counter (PC) is set to immediately after reset. It is the very first instruction the processor fetches. In a virtual platform, correctly modeling this single address is the foundation of the entire boot flow.

## What Is the Reset Vector?

Every CPU architecture defines a fixed or configurable reset vector:

| Architecture | Default Reset Vector |
|---|---|
| ARMv7-A | `0x00000000` (or `0xFFFF0000` with HIVECS) |
| ARMv8-A (AArch64) | Implementation-defined, typically `0x00000000` |
| RISC-V | Configurable via `mtvec`; commonly `0x80000000` |
| x86 | `0xFFFFFFF0` (top of 32-bit address space) |

**Interview answer:** The reset vector is the hardwired or strapped address where the CPU fetches its first instruction after reset; in a VP, the CPU ISS must present this PC value at `start_of_simulation()`.

## Modeling the Reset Vector in SystemC

In a SystemC VP, the CPU ISS (Instruction Set Simulator) models the reset vector as a compile-time or constructor parameter so it can be adapted per target SoC:

```cpp
SC_MODULE(CpuModel) {
    sc_in<bool> reset_n;
    tlm_utils::simple_initiator_socket<CpuModel> ibus; // instruction bus

    const uint64_t reset_vector;

    CpuModel(sc_module_name name, uint64_t rv)
        : sc_module(name), reset_vector(rv) {
        SC_THREAD(run);
        sensitive << reset_n.negedge(); // active-low reset
    }

    void run() {
        wait();              // wait for reset de-assertion
        uint64_t pc = reset_vector;
        while (true) {
            uint32_t insn = fetch(pc);
            pc = execute(insn, pc);
        }
    }

    uint32_t fetch(uint64_t addr) {
        tlm::tlm_generic_payload gp;
        uint32_t data = 0;
        gp.set_command(tlm::TLM_READ_COMMAND);
        gp.set_address(addr);
        gp.set_data_ptr(reinterpret_cast<unsigned char*>(&data));
        gp.set_data_length(4);
        sc_core::sc_time delay = SC_ZERO_TIME;
        ibus->b_transport(gp, delay);
        return data;
    }
};
```

## The First Fetch and the Memory Map

When the CPU fetches from the reset vector, that address must be mapped to something that returns valid instruction bytes. Typically this is the **Boot ROM**:

```
Reset vector: 0x0000_0000
  |
  v
Router → Boot ROM @ 0x0000_0000 – 0x0000_FFFF
```

If the address is unmapped and the router returns `TLM_ADDRESS_ERROR_RESPONSE`, a well-modeled CPU should trigger a reset-loop or bus fault — just like real hardware.

## HIVECS and Remap

ARM processors support an alternate reset vector at `0xFFFF0000` (called **HIVECS**, or high vectors). This is controlled by the `SCTLR.V` bit or a hardware strap. The VP must respect this:

```cpp
uint64_t effective_reset_vector() {
    if (hivecs_strap || (sctlr & SCTLR_V)) {
        return 0xFFFF0000UL;
    }
    return 0x00000000UL;
}
```

## Common Pitfalls

- **Reset vector points to unmapped memory**: The bus returns an error response. The CPU model should log a clear error message rather than silently reading zero.
- **Forgetting to deassert reset**: If your `reset_n` signal stays low, the CPU never starts. Always ensure the testbench drives `reset_n` high after the reset pulse.
- **Endianness of the first fetch**: If the Boot ROM contains little-endian instructions but the bus model byte-swaps, the first instruction is corrupt. Validate with a known opcode like `NOP` (`0xD503201F` in ARMv8).

## Verifying the Reset Vector in a VP

A quick sanity check: insert a trace callback on the very first bus transaction and confirm the address matches your expected reset vector:

```cpp
void CpuModel::run() {
    wait();
    uint64_t pc = reset_vector;
    SC_REPORT_INFO("CPU", ("First fetch from 0x" +
        std::to_string(pc)).c_str());
    // ... rest of run loop
}
```

This single line of output lets you confirm the VP is starting correctly before any other debugging begins.
