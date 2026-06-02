# Buses and the Von Neumann vs Harvard Model

Two foundational architectural decisions shape how a CPU communicates with memory and peripherals: the bus topology and the memory model. Understanding both clarifies why OS kernel design makes the choices it does.

## What Is a Bus?

A **bus** is a shared communication channel — a set of electrical lines that multiple components use to transfer data. In a classic PC architecture three buses collaborate:

| Bus | What it carries | Width (typical) |
|---|---|---|
| **Address bus** | The memory or I/O address the CPU wants to access | 32 or 64 bits |
| **Data bus** | The actual data being read or written | 8, 16, 32, or 64 bits |
| **Control bus** | Signals like READ, WRITE, INTERRUPT REQUEST | Several single-bit lines |

The CPU asserts an address on the address bus, sets READ or WRITE on the control bus, and either reads data from or places data onto the data bus. RAM and I/O controllers listen and respond when their address range is selected.

### Modern Bus Reality

Classic parallel buses (ISA, PCI) have been replaced by high-speed **serial point-to-point links**:

- **PCIe** — GPU, NVMe SSD, high-speed NICs
- **HyperTransport / QPI / UPI** — CPU-to-CPU links on multi-socket servers
- **DDR memory channels** — CPU to RAM DIMMs (still parallel, but dedicated point-to-point)

The OS interacts with buses mainly through **memory-mapped I/O (MMIO)** — device registers are mapped into the physical address space, so a normal memory write to a special address controls hardware.

## The Von Neumann Model

In the Von Neumann (Princeton) architecture, **instructions and data share the same memory and the same bus**:

```
        ┌──────────────────┐
        │        CPU       │
        │  [ALU][Registers]│
        │   [Control Unit] │
        └────────┬─────────┘
                 │  Single shared bus
        ┌────────┴─────────┐
        │   Unified Memory  │
        │  (code + data)   │
        └──────────────────┘
```

**Advantages:**
- Simpler hardware — one memory pool, one bus
- Self-modifying code is possible (the OS uses this for JIT compilation)
- Easy to adjust the code/data split dynamically

**Disadvantages — the Von Neumann bottleneck:**
The single bus means the CPU cannot fetch an instruction and read/write data simultaneously. This is the fundamental throughput ceiling of the model.

## The Harvard Model

The Harvard architecture uses **separate memory and buses for instructions and data**:

```
        ┌──────────────────┐
        │        CPU       │
        └──┬───────────────┤
           │               │
  Instruction bus     Data bus
           │               │
  ┌────────┴──┐    ┌───────┴───┐
  │ Instruction│    │   Data    │
  │  Memory   │    │  Memory   │
  └───────────┘    └───────────┘
```

**Advantages:**
- Fetch and data access happen in parallel → no Von Neumann bottleneck
- Instruction memory can be made read-only — no accidental self-modification

**Where it appears:** Microcontrollers (PIC, AVR, ARM Cortex-M), DSPs, and some embedded CPUs are pure Harvard. They have separate Flash (program) and SRAM (data) address spaces.

## Modified Harvard — What Modern CPUs Actually Use

Modern x86/ARM desktop CPUs use a **modified Harvard** design:

- The **L1 cache is split** into an instruction cache (I-cache) and a data cache (D-cache) — parallel fetch and data access at the cache level.
- Below the L1, a **unified L2/L3 cache and RAM** hold both code and data — Von Neumann at the main-memory level.

This gives the best of both worlds: parallel L1 performance with the flexibility of a single unified address space that the OS and compiler can use without special partitioning.

## OS Implications

- **Instruction cache coherence** — when the OS or a JIT writes new code into memory (Von Neumann-style), it must flush the instruction cache on relevant cores before executing that code, otherwise cores may run stale cached instructions.
- **Memory-mapped I/O** — the OS maps device registers into the address space; writes to those addresses cross the bus to hardware, not to RAM.
- **Bus mastering / DMA** — devices can take control of the bus to transfer data directly to RAM without CPU involvement. The OS must set up DMA descriptors and synchronize cache state afterward.

> **Interview answer:** Von Neumann architecture uses a single shared bus and memory for both code and data, creating the Von Neumann bottleneck (can't fetch instruction and access data simultaneously). Harvard uses separate buses and memories, allowing parallel access. Modern CPUs use modified Harvard — a split L1 cache — backed by a unified Von Neumann-style main memory and OS address space.
