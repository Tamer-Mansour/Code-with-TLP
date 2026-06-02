# SystemC as a Class Library, Not a New Language

One of the most important conceptual anchors in SystemC is the fact that it is a C++ **library** — not a compiled language, not a DSL with its own parser, and not a tool that generates code. Every SystemC construct is ultimately a macro, a template class, or a function from a header you `#include`.

## What "Library" Means in Practice

When you write:

```cpp
SC_MODULE(Adder) {
    sc_in<sc_uint<8>>  a, b;
    sc_out<sc_uint<8>> sum;

    SC_CTOR(Adder) {
        SC_METHOD(compute);
        sensitive << a << b;
    }

    void compute() {
        sum.write(a.read() + b.read());
    }
};
```

there is no special compiler pass. The preprocessor expands `SC_MODULE`, `SC_CTOR`, and `SC_METHOD` into plain C++ class declarations and constructor calls. The resulting translation unit is compiled by `g++` or `clang++` just like any other C++ file.

## Core Macro Expansions

| SystemC macro | Expands to |
|---------------|-----------|
| `SC_MODULE(X)` | `struct X : sc_module { typedef X SC_CURRENT_USER_MODULE;` |
| `SC_CTOR(X)` | `X(::sc_core::sc_module_name nm) : sc_module(nm)` |
| `SC_METHOD(f)` | `declare_method_process(...)` — registers `f` with the kernel |
| `SC_THREAD(f)` | `declare_thread_process(...)` — registers `f` as a coroutine |
| `SC_CTHREAD(f, clk)` | Registers `f` as a clocked thread sensitive to `clk` |

You can verify this by looking at `<systemc>/src/sysc/kernel/sc_module.h` in the open-source reference implementation.

## The Simulation Kernel

SystemC ships with a discrete-event simulation kernel (`libsystemc`). The kernel:

1. Maintains a global event queue sorted by simulated time.
2. Dispatches processes (`SC_METHOD` / `SC_THREAD`) when their sensitivity lists trigger.
3. Implements the **delta-cycle** mechanism for zero-time signal propagation.
4. Provides simulated time (`sc_time`) independent of wall-clock time.

You do not write the kernel — you link against it.

```
your_model.cpp  ──→  g++ -I$(SYSTEMC)/include  \
                          -L$(SYSTEMC)/lib-linux64 \
                          -lsystemc -o sim
```

## Header-Only vs. Library

SystemC is **not** header-only. The kernel implementation is compiled into a static or shared library (`libsystemc.a`). You must:

1. Include `systemc.h` (or `systemc`) in your source.
2. Link against `libsystemc`.

Some lightweight re-implementations (e.g., SystemC-Components by MINRES) provide header-only subsets, but the standard reference implementation requires the link step.

## What You Can and Cannot Do

**You can:**
- Use any C++ standard library alongside SystemC.
- Mix SystemC modules with plain C++ classes freely.
- Use templates to build generic, reusable models.
- Debug with GDB — set breakpoints inside `SC_METHOD` bodies normally.

**You cannot:**
- Call `wait()` from an `SC_METHOD` (only `SC_THREAD` / `SC_CTHREAD` supports suspension).
- Use C++ exceptions freely across `wait()` boundaries without care.
- Rely on wall-clock time for simulation timing — use `sc_time` objects.

## Worked Example: Plain Class vs. SC_MODULE

```cpp
// Plain C++ class — no simulation awareness
class PlainAdder {
public:
    int add(int a, int b) { return a + b; }
};

// SystemC module — lives in simulation time, reacts to events
SC_MODULE(ScAdder) {
    sc_in<int>  a, b;
    sc_out<int> result;

    SC_CTOR(ScAdder) {
        SC_METHOD(do_add);
        sensitive << a << b;
    }

    void do_add() {
        result.write(a.read() + b.read());
        // This executes at a specific simulated time point
    }
};
```

`PlainAdder::add` is called synchronously by whatever calls it. `ScAdder::do_add` is scheduled by the kernel whenever `a` or `b` changes — a fundamentally different execution model despite the similar code.

## Common Pitfalls

- **Missing `-lsystemc` linker flag** — produces undefined reference errors on `sc_module`, `sc_start`, etc.
- **Including `systemc.h` after headers that define `uint`** — type conflicts with SystemC's own `uint` typedef.
- **Assuming `SC_MODULE` creates a namespace** — it creates a struct; member access is public by default.

> **Interview answer:** "SystemC is a plain C++ library — `SC_MODULE` and `SC_THREAD` are macros that expand to normal class declarations, and the simulation kernel is a static library you link against. No special compiler is needed; `g++` and `clang++` work out of the box."
