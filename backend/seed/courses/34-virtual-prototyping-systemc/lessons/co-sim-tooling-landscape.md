# The Co-Simulation Tooling Landscape

The tooling ecosystem for HW/SW co-simulation is a patchwork of open-source projects, commercial platforms, and standards bodies. Knowing which tool solves which problem — and where the boundaries are — saves weeks of evaluation time.

## Tool Categories

| Category | Role in co-simulation |
|---|---|
| Virtual platform / ISS | Executes target software; ARM Fast Models, QEMU, Imperas OVP, gem5 |
| SystemC simulator | Runs the simulation kernel; Accellera reference, Cadence Xcelium, Synopsys VCS |
| HDL simulator | Runs RTL; Questa (Siemens), VCS (Synopsys), Xcelium (Cadence), Icarus/Verilator (OSS) |
| High-level synthesis | Generates RTL from C/C++; Vitis HLS, Catapult, Stratus |
| SoC integration | Platform assembly; ARM Corstone, Synopsys Virtualizer, Carbon SoC Designer |

## Open-Source Options

### QEMU

- Mature, widely used, primarily a JIT ISS.
- Supports ARM, RISC-V, x86, MIPS, PowerPC, and many more.
- Not natively a SystemC module but can be wrapped: the `libqemu` API lets SystemC code control QEMU's execution and intercept MMIO.
- Simulation speed: 500–2000 MIPS for ARM Linux.

### gem5

- Highly configurable, academic origin.
- Supports both functional and detailed (O3 CPU) modes.
- Has a native SystemC-coupled mode (`gem5 + SystemC cosim`), enabling TLM-connected peripherals.
- Best for computer-architecture research; steeper learning curve.

### Verilator

- Converts synthesisable Verilog/SystemVerilog to C++.
- Integrates directly into SystemC builds (no separate simulator process).
- Free, fast (often the fastest RTL simulation for large designs).
- Limitation: no X propagation, no analogue, synthesisable subset only.

### Renode

- Open-source (C#), targets embedded/IoT firmware.
- Large peripheral model library, CI-friendly, Python scriptable.
- Supports ARM Cortex-M/A, RISC-V, Xtensa.

## Commercial Platforms

### ARM Fast Models / Corstone

- ARM's reference virtual platforms.
- Very fast JIT ISS (1000+ MIPS for Cortex-A).
- SystemC export (SCMI) produces a synthesisable TLM module wrapping the ISS.
- Used by virtually all ARM-based SoC teams for early SW bring-up.

### Synopsys Virtualizer / Innovator

- Platform assembly tool; integrates Fast Models, Virtualizer Development Kit (VDK) models, and RTL co-simulation.
- Supports TLM-2.0 natively, includes peripheral model library.

### Siemens Mentor Questa

- Full mixed-language HDL simulation with SystemC integration.
- Strong for UVM + SystemC testbench flows.
- Waveform debug across RTL and SystemC in one window.

### Imperas OVP / riscvOVPsim

- Commercial ISS framework with open model library.
- Fastest simulation for many RISC-V targets.
- Used for RISC-V compliance testing.

## Standards That Glue the Ecosystem

| Standard | Body | Purpose |
|---|---|---|
| TLM-2.0 | Accellera | Bus transaction API; all platforms support it |
| SystemC 2.3.x | Accellera / IEEE 1666 | Simulation kernel |
| DPI-C | IEEE 1800 | SystemVerilog–C interop for RTL co-sim |
| AMBA / CHI | ARM | Bus protocols modelled in TLM |
| RISC-V specs | RISC-V International | ISA definitions for open ISSes |

## Choosing a Stack

```
Need to boot Linux on ARM?
  → ARM Fast Models (or QEMU if budget-constrained)

Need to validate a custom RISC-V accelerator?
  → gem5 or Imperas OVP + Verilator for the RTL block

Need to run on CI with no licence?
  → QEMU + Verilator + SystemC reference kernel

Need full SoC integration with waveforms?
  → Synopsys Virtualizer + Questa or VCS
```

## Common Pitfalls

- **Licence lock-in** — Building your entire flow on a single vendor's tools creates risk if the vendor changes pricing or drops a platform.
- **Model version mismatch** — Fast Model versions and SystemC kernel versions must be compatible; mixing major versions breaks the `sc_export` ABI.
- **QEMU as a black box** — QEMU is not a timing model. Using QEMU for performance analysis without additional instrumentation produces meaningless results.

## Interview Answer

> "The co-simulation tooling landscape splits into ISSes (QEMU, ARM Fast Models, Imperas OVP, gem5), SystemC/HDL simulators (Questa, VCS, Xcelium, Verilator), and SoC integration platforms (Synopsys Virtualizer, ARM Corstone). TLM-2.0 is the common bus API that allows components from different vendors to connect. Open-source stacks (QEMU + Verilator + SystemC reference) are viable for budget-constrained teams, while commercial stacks add waveform debug, licence-grade support, and certified ISS models."
