# What Is Simulation in This Context?

The word "simulation" is used loosely in engineering — it can mean anything from a spreadsheet model to a full-chip gate-level netlist running in a cycle-accurate EDA tool. In the context of virtual prototyping and SystemC/TLM, "simulation" has a specific, precise meaning that is important to nail down early.

## Simulation vs. Emulation vs. Execution

| Term | What Runs | Where | Speed |
|---|---|---|---|
| Simulation | A software model | Host CPU | Slow–medium |
| Emulation | RTL mapped to FPGAs | Dedicated hardware | Near real-time |
| Native execution | Binary on target ISA | Real silicon or ISS | Full speed |

In the VP world, **simulation** means running a software model of the target system on a host machine. The host CPU interprets or JIT-compiles the model — it does not execute target binaries natively (unless an ISS is involved).

## Types of Simulation Relevant to VPs

### 1. Functional Simulation (Transaction-Level)

This is what TLM-2.0 targets. Models communicate via **transactions** — high-level messages that represent a read or write of a memory range — rather than cycle-by-cycle signal changes. This abstraction gives 100x–10,000x speedup over RTL simulation.

```cpp
// A TLM initiator sending a write transaction (no clock, no signals)
tlm::tlm_generic_payload trans;
sc_time delay = SC_ZERO_TIME;
trans.set_command(tlm::TLM_WRITE_COMMAND);
trans.set_address(0x4000'0004);
trans.set_data_ptr(reinterpret_cast<unsigned char*>(&data));
trans.set_data_length(4);
socket->b_transport(trans, delay); // blocking transport
```

No clock toggling. No wire-level signals. Just a function call that transfers data from point A to point B.

### 2. Cycle-Accurate Simulation (RTL)

RTL simulators (ModelSim, Xcelium, VCS) model every flip-flop and every clock edge. They are used for hardware verification, not for running software stacks. Running Linux on an RTL simulation of a modern SoC can take weeks of simulation time for a few seconds of boot.

### 3. Instruction-Set Simulation (ISS)

An ISS interprets or translates target ISA instructions on the host CPU. It models the processor's software-visible behavior (registers, memory, exceptions) without modeling pipeline microarchitecture. Fast ISS tools (QEMU, Imperas OVPsim) run at hundreds of millions of instructions per second, fast enough to boot Linux in seconds.

```bash
# Running a bare-metal ARM binary in QEMU (an ISS)
qemu-system-arm -M versatilepb -kernel firmware.elf -nographic
```

### 4. Mixed-Level Simulation

A real VP often combines these levels:
- An ISS for the processor core (fast functional execution)
- TLM-2.0 models for memory, DMA, UART, and other peripherals
- A few RTL blocks (wrapped via TLM adapters) where cycle-accurate behavior matters

## The SystemC Simulation Kernel

SystemC provides a **discrete-event simulation kernel** (IEEE 1666). Every process in a SystemC model is a coroutine. The kernel manages:

- **Simulation time** — a monotonically increasing counter (not wall-clock time)
- **Delta cycles** — zero-time steps used to propagate signal changes within one time step
- **Process scheduling** — which `SC_THREAD` or `SC_METHOD` runs next

```cpp
SC_MODULE(counter) {
    sc_in<bool> clk;
    sc_out<sc_uint<8>> count;
    SC_CTOR(counter) {
        SC_METHOD(on_clk);
        sensitive << clk.pos(); // triggers on rising edge
    }
    void on_clk() { count.write(count.read() + 1); }
};
```

## Interview Answer

> "In the VP context, simulation refers to running a software model of a hardware system on a host machine using a discrete-event kernel like SystemC, typically at the transaction level for speed. This is distinct from RTL simulation (cycle-accurate, slow) and FPGA emulation (near real-time but expensive)."

## Key Takeaway

The power of TLM-based simulation is the **abstraction trade-off**: you sacrifice cycle-level accuracy in exchange for simulation speed that is fast enough to run real software workloads. Knowing when that trade-off is acceptable — and when you need RTL accuracy — is a core judgment call in virtual prototyping.
