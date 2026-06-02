# Why SystemC Is Built on C++

SystemC is not a standalone language — it is a C++ class library and a simulation kernel. Before the first `sc_signal` ever appeared, the choice to embed a hardware-description language inside C++ was a deliberate engineering decision. Understanding that decision reveals why the language features in this module matter and why SystemC has become the standard for virtual prototyping.

## The Design Space: Custom Language vs Library

When Synopsys and other EDA companies started work on what became SystemC in the late 1990s, the alternatives were:

- **Design a new language** (like Verilog or VHDL) with custom parsers, simulators, and toolchains.
- **Embed into an existing language** and reuse its compiler, standard library, and ecosystem.

The embedded approach won. The chosen host language was C++.

## Why C++ Specifically?

### 1. Zero-Cost Abstraction

C++ templates allow the compiler to generate optimised, type-specific code at compile time with no runtime overhead. `sc_uint<32>` is not a boxed integer — it compiles down to native 32-bit operations wherever possible.

```cpp
sc_uint<8>  byte_a(0xAB), byte_b(0xCD);
sc_uint<16> result = byte_a.concat(byte_b);   // compile-time type, native instruction
```

### 2. Deterministic Object Lifetime (RAII)

Hardware simulation must create and destroy thousands of modules, channels, and processes in a controlled order. C++ destructors provide this without a garbage collector — the simulator controls lifetime precisely.

### 3. Classes and Inheritance for Hierarchy

An SoC is a hierarchy: chips contain subsystems, subsystems contain blocks, blocks contain registers. C++ classes map naturally: each module is a class, composition via member variables models structural hierarchy, and inheritance models reuse (an AHB slave is a specialisation of a generic slave interface).

### 4. Operator Overloading for Signal Arithmetic

Hardware designers think in terms of bus operations. C++ operator overloading lets `sc_lv<32>` types support `|`, `&`, `^`, and shifts with natural notation:

```cpp
sc_lv<32> flags = status_reg & mask;   // bitwise AND on a 32-bit logic vector
```

### 5. Templates for Parameterisation

Every bus interface has a width. Every FIFO has a depth. In RTL, parameters are integers in a module header. In SystemC, template arguments serve exactly the same role:

```cpp
template<int DATA_WIDTH, int ADDR_WIDTH>
SC_MODULE(SramModel) { ... };

SramModel<32, 16> sram("sram");   // 32-bit data, 16-bit address
```

### 6. Full Software Ecosystem

A SystemC model has access to all of C++: STL containers, file I/O, sockets, threading primitives, third-party math libraries, and profiling tools. A VHDL testbench cannot easily call a Python script or query a database; a SystemC testbench can.

## The Trade-offs

| Benefit | Trade-off |
|---------|-----------|
| Reuses C++ compiler and tools | No dedicated simulator optimisations for plain C++ code |
| Familiar language for software engineers | Hardware engineers face a learning curve |
| Full C++ expressiveness | Easy to write un-synthesisable models by accident |
| Portable across platforms | Requires a C++ build system (CMake, Make, etc.) |

## What the Kernel Provides on Top of C++

C++ alone is sequential. SystemC adds:

- A **discrete-event scheduler** — manages simulation time and event queues.
- **Delta cycles** — multiple evaluations at the same time step until stability.
- **Process types** — `SC_METHOD` (no suspension), `SC_THREAD` (can `wait()`), `SC_CTHREAD` (clocked thread).
- **Port/channel infrastructure** — typed connections with bind-time type checking.

These are all implemented as C++ classes and macros. There is no special compiler: `g++ -lsystemc` is all you need.

## Industry Adoption

SystemC / TLM-2.0 is standardised as **IEEE 1666-2011** (updated 2023). It is the foundation of:

- Virtual platforms used to develop firmware months before silicon is ready.
- Transaction-level performance models for memory sub-system analysis.
- High-level synthesis flows (Mentor Catapult, Cadence Stratus) that accept SystemC as input.

> **Interview answer:** SystemC is a C++ library rather than a new language because C++ provides zero-cost templates for parameterisation, RAII for deterministic object lifetime, operator overloading for natural hardware arithmetic, and a mature toolchain — all without the cost of building a new compiler. The SystemC kernel adds a discrete-event scheduler on top, giving designers both the expressiveness of C++ and the time-ordered semantics required for hardware modeling.
