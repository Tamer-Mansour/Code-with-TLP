# Host vs Target Execution

In co-simulation, two CPUs are always involved: the **host** (the machine running the simulation) and the **target** (the processor being simulated). Understanding which code runs where — and the implications of that distinction — is fundamental to building correct and efficient virtual platforms.

## Definitions

- **Host** — The physical machine where the simulator process executes. Typically x86-64 Linux or Windows, running at 3–5 GHz with gigabytes of RAM.
- **Target** — The processor being modeled: an ARM Cortex-A, RISC-V core, or custom DSP. It exists only as a software model on the host.
- **Host code** — The C++ simulator itself: SystemC modules, TLM sockets, peripheral models, the ISS.
- **Target code** — The firmware or OS binary compiled for the target ISA. It executes *inside* the ISS, interpreted or JIT-compiled by host code.

## Two Execution Contexts

```
Host machine (x86-64)
  +-----------------------------------------+
  |  SystemC simulation process             |
  |  +------------------+  +-------------+ |
  |  |   ISS (host C++) |  | UART model  | |
  |  |  +-----------+   |  | (host C++)  | |
  |  |  | target    |   |  +-------------+ |
  |  |  | binary    |   |                  |
  |  |  | (ARM ELF) |   |                  |
  |  |  +-----------+   |                  |
  |  +------------------+                  |
  +-----------------------------------------+
```

The target binary never directly executes on host hardware (unless JIT-compiled — see below). Its instructions are decoded by the ISS and emulated.

## Interpretation vs JIT Compilation

| Technique | How it works | Speed | Accuracy |
|---|---|---|---|
| Interpretation | ISS decodes each target instruction and calls a host function | Slow (~50 MIPS) | High |
| JIT (just-in-time) | Target basic blocks translated to host machine code at runtime | Fast (~1000 MIPS) | Medium |
| Native execution | Target ISA == host ISA; binary runs directly | Fastest | Requires ISA match |

QEMU uses a JIT (TCG — Tiny Code Generator). Gem5 uses interpretation by default. Commercial ISSes like Synopsys ARC offer both.

## Native Execution (Same-ISA Platforms)

If the target is x86 and the host is x86, you can run the target binary *directly* on the host processor, replacing the ISS with a process or virtual machine. This is the basis of **binary translation platforms** and **hypervisor-based co-simulation**.

```bash
# Example: run x86 bare-metal firmware directly, with peripheral stubs
# The "hardware" is the simulation process itself
./vp_runner --firmware bios.elf --peripheral uart_model.so
```

Benefit: near-native speed. Risk: host and target share the same address space — a firmware bug can corrupt the simulator.

## Endianness and Data Width

Host (x86) is always little-endian. Targets may be big-endian (SPARC, network processors). Every byte transferred across the TLM socket must be byte-swapped correctly.

```cpp
// Peripheral model receiving a 32-bit write from a big-endian target
void Reg32::b_transport(tlm_generic_payload& t, sc_time& delay) {
    uint32_t val;
    memcpy(&val, t.get_data_ptr(), 4);
#if TARGET_BIG_ENDIAN
    val = __builtin_bswap32(val);  // convert to host byte order
#endif
    do_write(val);
}
```

Forgetting endianness conversion is one of the most common bugs in a first co-simulation bring-up.

## Debugging Across the Boundary

- **Target-side debug** — GDB connected via a stub in the ISS. The target binary can be debugged as if it were on real hardware, with breakpoints and watch-points in target address space.
- **Host-side debug** — Standard C++ debugger (gdb, VS, MSVC) attached to the simulation process. Useful for peripheral model bugs.
- **Cross-domain trace** — Some platforms expose a combined trace that interleaves target instruction execution with host-side SystemC events, letting you see cause and effect across both domains.

## Common Pitfalls

- **Pointer size mismatch** — On a 64-bit host simulating a 32-bit target, host pointers passed into TLM `data_ptr` fields must not be confused with target addresses.
- **Floating-point ABI** — Host and target may use different FP standards (IEEE-754 soft vs hard). ISS must emulate target FP exactly, not delegate to host FPU, unless ISAs match.
- **Time zones of memory** — Writes by a DMA model (host code) to shared memory are instantly visible to the ISS (host code). This is correct but can mask timing bugs that would be exposed by a real cache hierarchy.

## Interview Answer

> "The host is the physical machine running the simulation; the target is the processor being simulated, which exists only as an ISS inside the host process. Target binaries are interpreted or JIT-compiled by the ISS; all peripheral models are host C++ code. Key hazards are endianness mismatches and pointer-size differences between the two environments."
