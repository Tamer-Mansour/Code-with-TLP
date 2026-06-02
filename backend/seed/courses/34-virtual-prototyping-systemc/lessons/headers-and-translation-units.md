# Headers and Translation Units in C++

A **translation unit (TU)** is the single `.cpp` file plus every header it `#include`s, after preprocessing. The compiler processes one TU at a time, producing one object file per TU. How you split code across headers and source files directly affects compile times, link correctness, and maintainability of SystemC models.

## Headers vs Source Files

| File type | Contains | Included by |
|-----------|----------|-------------|
| Header `.h` / `.hpp` | Declarations, inline functions, templates, `constexpr` | Many TUs |
| Source `.cpp` | Definitions (function bodies, non-inline globals) | Only itself |

A **declaration** tells the compiler a name exists and what its type is. A **definition** provides the storage or code. Every name must be declared before use and defined exactly once across all TUs (the One Definition Rule, ODR).

## Include Guards

Without guards, including a header twice in the same TU causes redeclaration errors.

```cpp
// memory_map.h
#ifndef MEMORY_MAP_H
#define MEMORY_MAP_H

struct MemoryMap {
    uint32_t base;
    uint32_t size;
};

#endif // MEMORY_MAP_H
```

Modern equivalent — `#pragma once` (supported by all major compilers, but non-standard):

```cpp
#pragma once

struct MemoryMap { uint32_t base; uint32_t size; };
```

## Forward Declarations

If a header only needs a pointer or reference to a type, a forward declaration avoids pulling in the full header, reducing compilation dependencies:

```cpp
// bus.h
class Device;          // forward declaration — no #include needed

class Bus {
    void attach(Device* d);
};
```

## The ODR in Practice

Defining a non-inline function in a header and including it in two TUs violates the ODR:

```cpp
// bad.h — do NOT do this
int add(int a, int b) { return a + b; }  // linker sees two definitions of add()
```

Fix: declare in the header, define in exactly one `.cpp`, or mark `inline`:

```cpp
// good.h
inline int add(int a, int b) { return a + b; }  // inline: each TU may have its own copy
```

## Translation Units in a SystemC Project

A typical SystemC module is split across three files:

```
cpu_model.h      — SC_MODULE declaration, port/signal members, method declarations
cpu_model.cpp    — SC_CTOR body, SC_METHOD/SC_THREAD implementations
main.cpp         — sc_main(), instantiation, binding
```

```cpp
// cpu_model.h
#pragma once
#include <systemc.h>

SC_MODULE(CpuModel) {
    sc_in<bool> clk;
    sc_out<uint32_t> addr;
    void execute();
    SC_CTOR(CpuModel) {
        SC_METHOD(execute);
        sensitive << clk.pos();
    }
};
```

```cpp
// cpu_model.cpp
#include "cpu_model.h"

void CpuModel::execute() {
    addr.write(addr.read() + 4);
}
```

```cpp
// main.cpp
#include "cpu_model.h"

int sc_main(int, char**) {
    sc_clock clk("clk", 10, SC_NS);
    sc_signal<uint32_t> addr_sig;
    CpuModel cpu("cpu");
    cpu.clk(clk);
    cpu.addr(addr_sig);
    sc_start(100, SC_NS);
    return 0;
}
```

## Compile-Time Dependency Graph

Including a header creates a compile-time dependency. Change `cpu_model.h` and every `.cpp` that includes it must recompile. Minimising unnecessary includes is the primary technique for keeping large virtual platforms buildable in reasonable time.

**Rule of thumb:** include in the header only what is needed for the declaration; include implementation headers in the `.cpp`.

## Common Pitfalls

- **Missing include guard** — double-include causes redeclaration errors.
- **Including `.cpp` files** — creates duplicate definitions at link time.
- **Circular includes** — A includes B, B includes A. Break cycles with forward declarations.
- **Template definitions in `.cpp`** — templates must be fully visible to every TU that instantiates them; put them in the header.

## Interview Answer

> "A translation unit is one `.cpp` file after preprocessing. Headers contain declarations shared between TUs; definitions go in exactly one `.cpp` to satisfy the One Definition Rule. Include guards prevent double-inclusion within a single TU."
