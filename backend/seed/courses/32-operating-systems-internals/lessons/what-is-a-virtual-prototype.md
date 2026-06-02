# What Is a Virtual Prototype? SystemC and ISS

A **virtual prototype** is a software model of a hardware system that lets you run firmware and operating system code before physical silicon exists. Instead of waiting months for an ASIC tape-out, engineers boot Linux on a simulated SoC the same day the RTL freeze is declared. Understanding virtual prototypes is essential for OS and firmware engineers working on embedded, mobile, or server silicon.

## Why Virtual Prototypes Matter

- **Shift-left software development** — OS and driver teams work in parallel with hardware design, not sequentially after it.
- **Deterministic debugging** — you can replay an exact execution trace, set watchpoints on register writes, and freeze time. Real silicon rarely offers this.
- **Fault injection** — simulate memory errors, interrupt storms, or power loss without destroying hardware.
- **Coverage analysis** — instrument every instruction to measure which boot paths are exercised.

> **Interview answer:** A virtual prototype is a host-executable functional model of a target SoC that allows software development and debugging before physical hardware is available.

## SystemC and TLM-2.0

**SystemC** is an IEEE standard (1666-2011) C++ class library for hardware modeling. It adds discrete-event simulation semantics — modules, ports, signals, and a kernel that advances simulated time — on top of standard C++.

```cpp
// Minimal SystemC module skeleton
#include <systemc.h>

SC_MODULE(SimpleCPU) {
    sc_in<bool>  clk;
    sc_in<bool>  reset_n;
    sc_out<sc_uint<32>> addr_out;

    void run();
    SC_CTOR(SimpleCPU) {
        SC_THREAD(run);
        sensitive << clk.pos();
    }
};
```

**TLM-2.0** (Transaction Level Modeling) sits on top of SystemC. Instead of toggling individual wires (cycle-accurate RTL), a TLM model fires a function call representing an entire bus transaction. This makes models 10-100x faster than RTL simulation, which is why virtual prototypes use TLM.

| Abstraction level | Speed | Accuracy |
|---|---|---|
| RTL (Verilog/VHDL) | ~1 KHz | Cycle-exact |
| Cycle-approximate TLM | ~1 MHz | ±few cycles |
| Loosely-timed TLM | ~100 MHz | Functional only |
| ISS (no timing) | ~500 MHz | Instruction-accurate |

## Instruction Set Simulators (ISS)

An **ISS** is the CPU component of a virtual prototype. It decodes and executes target instructions on the host CPU:

1. **Fetch** — read bytes from simulated memory at the program counter.
2. **Decode** — identify the opcode and operands.
3. **Execute** — update simulated registers and flags.
4. **Memory access** — issue a TLM transaction to the memory model.
5. **Write-back** — commit result registers.

Popular open-source ISSes include QEMU (multi-architecture, JIT-based), Spike (RISC-V reference), and OVPsim. Commercial platforms such as Synopsys Virtualizer and Arm Fast Models add peripheral models and timing annotations.

## Typical Virtual Prototype Stack

```
+---------------------------+
|   OS / Firmware (target)  |
+---------------------------+
|   ISS (CPU model)         |  ← executes target binary
+---------------------------+
|   TLM peripheral models   |  ← UART, GIC, MMU, timer
+---------------------------+
|   SystemC simulation      |  ← discrete-event kernel
+---------------------------+
|   Host OS (Linux/Windows) |
+---------------------------+
```

## Common Pitfalls

- **Assuming timing fidelity** — loosely-timed TLMs do not model cache misses or pipeline stalls. Real-time constraints may not hold.
- **Endianness bugs** — host and target may differ; byte-swap every memory access explicitly.
- **Peripheral side effects** — clearing an interrupt by reading a status register must be modeled, or the OS will spin forever.
- **Missing memory-mapped I/O** — unmodeled regions should return 0 and log a warning, not silently succeed.

Virtual prototypes are the industry standard for pre-silicon software development. Knowing the SystemC/TLM architecture and the role of an ISS will set you apart in both embedded and systems engineering interviews.
