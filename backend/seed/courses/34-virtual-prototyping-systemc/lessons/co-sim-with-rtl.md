# Co-Simulating with RTL Blocks

Not every block in a chip needs a high-level SystemC model. Custom accelerators, memory controllers, or cryptographic cores often carry RTL that must be validated against real firmware. RTL co-simulation plugs those blocks directly into the virtual platform without re-implementing them at a higher abstraction level.

## Why Mix RTL and SystemC?

- The RTL block already exists and is the ground truth.
- Rewriting it in SystemC would duplicate effort and risk divergence.
- The firmware driver must be validated against the *actual* register behaviour, not an approximation.
- Power or timing sign-off requires the real netlist stimulated with real SW traffic.

## The Two Main Coupling Mechanisms

### 1. Direct Language Interface (DLI) / Verilog PLI / DPI

SystemC and HDL simulators communicate through a shared C API. The SystemC process calls a Verilog task; the Verilog module calls a SystemC function via DPI-C.

```cpp
// SystemC side: trigger RTL execution for one clock cycle
extern "C" void vl_step_one_cycle();  // implemented in Verilog DPI-C

void Accelerator_Wrapper::b_transport(
        tlm::tlm_generic_payload& t, sc_core::sc_time& delay) {
    write_dpi_regs(t);          // push transaction into RTL via DPI
    vl_step_one_cycle();        // advance RTL by one cycle
    read_dpi_result(t);         // pull result back
    delay += sc_time(1, SC_NS);
}
```

### 2. TLM–RTL Transactor (Adapter)

A transactor sits between the TLM bus and the RTL block. It converts abstract `b_transport` calls into pin-level signal sequences that the RTL block expects.

```
TLM initiator (ISS)
      | b_transport()
      v
  Transactor (SystemC module)
      | drives clock, addr, data, we signals
      v
  RTL block (Verilog/VHDL, run by HDL simulator)
      | outputs result signals
      v
  Transactor (collects response)
      | returns tlm_generic_payload
      v
TLM initiator (ISS) sees result
```

The transactor is the place where abstraction levels meet. It must correctly model the handshake protocol of the RTL interface.

## Toolchain Integration Approaches

| Approach | Tools | Notes |
|---|---|---|
| SystemC + Verilator | Verilator (converts RTL to C++), linked into SystemC binary | No licence cost, fast, no waveform viewer integration |
| SystemC + Questa co-sim | Mentor Questa Multi-Language | Full mixed-language, waveforms, assertions |
| SystemC + VCS | Synopsys VCS UVM | Industry standard, expensive licence |
| SystemC + ModelSim DPI | Siemens ModelSim | Good for small RTL blocks |

## Verilator Integration Example

Verilator translates synthesisable Verilog to C++ classes. You can instantiate those classes directly in SystemC:

```cpp
#include "Vaes_core.h"   // Verilator-generated C++ model of aes_core.v

SC_MODULE(AesWrapper) {
    tlm_utils::simple_target_socket<AesWrapper> socket;
    Vaes_core* vl_model;

    SC_CTOR(AesWrapper) : socket("socket") {
        vl_model = new Vaes_core("aes_core");
        socket.register_b_transport(this, &AesWrapper::b_transport);
    }

    void b_transport(tlm::tlm_generic_payload& t, sc_core::sc_time& delay) {
        // Map TLM payload to Verilator signals
        vl_model->clk = 0; vl_model->eval();
        vl_model->data_in = *reinterpret_cast<uint32_t*>(t.get_data_ptr());
        vl_model->clk = 1; vl_model->eval(); // rising edge
        // Collect output
        if (t.get_command() == tlm::TLM_READ_COMMAND)
            *reinterpret_cast<uint32_t*>(t.get_data_ptr()) = vl_model->data_out;
        delay += sc_time(10, SC_NS);
    }
};
```

## Timing Challenges

RTL blocks run on a clock; TLM models are transaction-based. The transactor must:

- **Drive the RTL clock** explicitly for each cycle it wants to advance.
- **Handle multi-cycle operations** — many RTL blocks require several clock cycles to produce a result. The transactor must loop, driving clocks, until the `done` signal goes high.
- **Return to SystemC** by issuing `wait()` for each cycle driven, so the rest of the platform keeps time correctly.

```cpp
// Transactor: drive RTL for N cycles until done
void wait_for_rtl_done() {
    while (!vl_model->done) {
        vl_model->clk = 0; vl_model->eval();
        wait(sc_time(5, SC_NS));
        vl_model->clk = 1; vl_model->eval();
        wait(sc_time(5, SC_NS));
    }
}
```

## Common Pitfalls

- **Clock domain crossing in the transactor** — The TLM bus may run at a different frequency than the RTL block. The transactor must model any CDC FIFO or synchroniser logic.
- **Reset handling** — RTL blocks require a reset pulse at start-up. Forgetting to assert `rst_n` leaves internal state undefined.
- **X-propagation** — Verilog X values are not modelled in C++/SystemC. Verilator collapses X to 0 or 1; unexpected simulation-only X bugs may be hidden.

## Interview Answer

> "RTL blocks are integrated into a virtual platform using transactors that convert TLM transactions into pin-level signal sequences. Verilator is a popular zero-cost option: it compiles Verilog to C++ classes that the SystemC module drives clock-by-clock inside `b_transport`. Commercial co-simulation (Questa, VCS) connects the SystemC kernel to an HDL simulator via DPI or language-interface APIs, enabling full waveform debug across both domains."
