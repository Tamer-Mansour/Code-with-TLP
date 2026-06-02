# What Is sc_module?

`sc_module` is the cornerstone of SystemC structural modeling. Every hardware block, IP core, or subsystem you describe in SystemC is a class derived from `sc_module`. Understanding it deeply unlocks the entire SystemC methodology.

## The Core Idea

In RTL languages like VHDL or Verilog, a module or entity is a built-in language construct. SystemC takes a different approach: it implements module semantics as a C++ class. `sc_module` is that class, defined in the SystemC standard library. When you write `struct MyBlock : sc_module { ... }`, you are creating a C++ class that the SystemC simulation kernel recognizes as a simulatable entity.

This design choice is fundamental. It means:

- SystemC is ordinary, portable C++, compilable by any standards-compliant compiler.
- The full power of C++ (templates, inheritance, operator overloading) applies to hardware modeling.
- Existing C++ tooling (debuggers, profilers, static analyzers) works without modification.

## What sc_module Provides

Inheriting from `sc_module` gives your class several built-in capabilities:

| Feature | What It Does |
|---|---|
| Hierarchical naming | Registers the module in the kernel's object tree |
| Port ownership | Allows `sc_in`, `sc_out`, `sc_inout` members to bind to signals |
| Process registration | Enables `SC_THREAD`, `SC_METHOD`, and `SC_CTHREAD` declarations |
| Elaboration callbacks | Provides `before_end_of_elaboration`, `end_of_elaboration`, `start_of_simulation`, `end_of_simulation` |
| `name()` accessor | Returns the full hierarchical dot-separated name of the instance |

## Minimal Example

```cpp
#include <systemc.h>

SC_MODULE(Counter) {
    sc_in<bool>  clk;
    sc_in<bool>  reset;
    sc_out<int>  count;

    int value;

    SC_CTOR(Counter) : value(0) {
        SC_METHOD(update);
        sensitive << clk.pos();
    }

    void update() {
        if (reset.read())
            value = 0;
        else
            value++;
        count.write(value);
    }
};
```

`SC_MODULE(Counter)` is a convenience macro that expands to:

```cpp
struct Counter : sc_module {
    typedef Counter SC_CURRENT_USER_MODULE;
```

It saves boilerplate but hides nothing — both forms are equivalent.

## The Module Constructor Contract

The SystemC kernel requires every module to be constructed during *elaboration* — the phase before simulation begins. At construction time you must:

1. Declare all child module instances.
2. Bind ports to signals (connect the netlist).
3. Register all processes with `SC_METHOD` / `SC_THREAD`.

You must **not** start waiting for events, drive signals, or call time-consuming operations during construction. Those actions belong in `start_of_simulation` or inside processes.

## Common Pitfalls

- **Forgetting `SC_CTOR` or an equivalent constructor.** Without it the module name is never registered and the kernel cannot track it.
- **Allocating child modules with `new` but forgetting to keep a pointer.** The child is alive but unreachable for port binding later.
- **Putting simulation logic in the constructor.** Code like `wait()` inside the constructor causes undefined behavior.
- **Multiple inheritance from `sc_module`.** It is allowed but uncommon and error-prone; prefer composition.

## Why It Matters for Interviews

Engineers ask about `sc_module` to test whether you understand the elaboration-simulation split and why SystemC modules must be fully wired before `sc_start()` is called.

> **Interview answer:** `sc_module` is the base class every SystemC design component inherits from. It registers the instance in the kernel's hierarchy, owns ports and processes, and enforces the rule that structure (ports, bindings, processes) is declared during elaboration before simulation begins.
