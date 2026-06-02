# What Is SystemC?

SystemC is an open-source C++ class library that extends the C++ language with hardware modeling constructs — modules, ports, signals, clocks, and a discrete-event simulation kernel — so that designers can describe and simulate electronic systems at multiple abstraction levels within a single language ecosystem.

## The Core Idea

Before SystemC, hardware/software co-design teams faced a painful split: hardware engineers wrote RTL in VHDL or Verilog, while software engineers wrote C or C++. The two worlds were hard to integrate, simulate together, or explore architecturally before committing to silicon.

SystemC solves this by bringing hardware concepts into C++:

- **sc_module** — the building block, analogous to a Verilog `module` or VHDL `entity`.
- **sc_port / sc_signal** — typed connection points and wires.
- **sc_clock** — a dedicated clock signal generator.
- **Simulation kernel** — a built-in discrete-event scheduler that advances simulated time.

## What SystemC Is NOT

| What people assume | Reality |
|--------------------|---------|
| A new language | A C++ library; you compile with any standard C++ compiler |
| A replacement for RTL | An addition: SystemC spans algorithmic → TLM → RTL levels |
| Only for hardware engineers | Used by firmware, software, and architect teams too |
| Proprietary | Standardized as IEEE 1666-2011 (and updated) |

## Abstraction Levels SystemC Supports

SystemC is deliberately multi-level. The same library supports:

1. **Algorithmic / Untimed** — pure functional models, no cycle concept.
2. **Transaction Level (TLM)** — communication modeled as function calls, not wires; fastest simulation speed.
3. **Cycle-Accurate** — every clock edge is modeled; used for hardware/software integration testing.
4. **RTL** — synthesizable subset, comparable to traditional HDL.

This lets teams start with a fast architectural model and incrementally add timing detail.

## A Minimal Taste

```cpp
#include <systemc.h>

SC_MODULE(Hello) {
    SC_CTOR(Hello) {
        SC_THREAD(say_hello);  // register a process
    }

    void say_hello() {
        std::cout << "Hello, SystemC! Time = "
                  << sc_time_stamp() << "\n";
    }
};

int sc_main(int argc, char* argv[]) {
    Hello h("hello_inst");
    sc_start();   // run the simulation
    return 0;
}
```

**Key observations:**
- `SC_MODULE` is a macro that expands to a class derived from `sc_module`.
- `SC_CTOR` constructs the module and registers processes.
- `sc_start()` hands control to the simulation kernel.
- `sc_main` replaces `main` — more on this in a later lesson.

## Why SystemC Matters for Your Career

SystemC is the lingua franca of virtual prototyping. It is used by:

- ARM, Intel, NVIDIA, and most major semiconductor companies for firmware bring-up before tape-out.
- EDA vendors (Synopsys, Cadence, Mentor) whose tools generate or consume SystemC models.
- RISC-V ecosystem projects that ship TLM-2.0 platform models.

Understanding SystemC signals that you can work across hardware and software boundaries — a skill that commands a significant salary premium.

> **Interview answer:** "SystemC is a C++ library that adds hardware simulation primitives — modules, ports, signals, and a discrete-event kernel — so teams can model and simulate systems from high-level architecture down to cycle-accurate RTL without leaving C++."

## Common Pitfalls

- **Forgetting `sc_start()`** — your processes never run.
- **Using `main` instead of `sc_main`** — the library provides its own `main` that calls `sc_main`; defining both causes a linker error.
- **Treating SystemC signals like plain C++ variables** — signal updates are scheduled for the next delta cycle, not immediate.
