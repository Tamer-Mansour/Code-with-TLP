# Namespaces and Organizing Model Code

A real SystemC project can easily have hundreds of modules spread across dozens of files. Without deliberate organisation, name collisions and opaque `#include` graphs become maintenance nightmares. Namespaces and disciplined header conventions are the C++ tools that keep models readable and reusable.

## What Is a Namespace?

A namespace groups names (types, functions, variables) under a common prefix to avoid collisions.

```cpp
namespace cpu {
    struct Register { int value; };
    void reset();
}

namespace gpu {
    struct Register { float value; };   // no clash with cpu::Register
    void reset();
}

cpu::Register r;   // unambiguous
```

Every SystemC name lives in the `sc_core` namespace. The `#include <systemc.h>` convenience header adds `using namespace sc_core;` (and `sc_dt;`) so you can write `sc_signal` instead of `sc_core::sc_signal`. For library code you should qualify fully to avoid pollution.

## Defining Namespaces

```cpp
// myip/bus_types.h
namespace myip {
namespace bus {
    using addr_t = sc_uint<32>;
    using data_t = sc_uint<64>;
}
}

// Nested shorthand (C++17)
namespace myip::bus {
    using addr_t = sc_uint<32>;
}
```

You can reopen a namespace in multiple files; the compiler merges them.

## `using` Declarations vs Directives

| Syntax | What it does | Recommended scope |
|--------|-------------|-------------------|
| `using sc_core::sc_signal;` | Imports one name | Inside a `.cpp` function or class |
| `using namespace sc_core;` | Imports all names | Inside a `.cpp` function body only |
| `namespace sc = sc_core;` | Alias — shorter prefix | File scope in `.cpp` |

Never put `using namespace X` at file scope in a header — it contaminates every file that includes yours.

## Header Organisation

A well-organised SystemC project follows this layout:

```
myip/
  include/
    myip/adder.h        ← module declaration
    myip/fifo.h
  src/
    adder.cpp           ← module implementation
    fifo.cpp
  tb/
    adder_tb.h
    adder_tb.cpp
  sc_main.cpp
```

Every header should be **self-contained** and use an **include guard** (or `#pragma once`):

```cpp
// myip/adder.h
#pragma once
#include <systemc.h>

namespace myip {

SC_MODULE(Adder) {
    sc_in<int>  a, b;
    sc_out<int> result;

    SC_CTOR(Adder);   // defined in adder.cpp
};

}  // namespace myip
```

Splitting the constructor definition into a `.cpp` file shortens rebuild times: changing the implementation does not force recompilation of everything that includes the header.

## Forward Declarations

When module `A` only needs a pointer or reference to module `B`, a **forward declaration** avoids pulling in the full header:

```cpp
// In a.h — no need to include b.h
namespace myip { struct B; }

SC_MODULE(A) {
    myip::B* partner;   // pointer only — forward declaration is enough
    SC_CTOR(A) : partner(nullptr) {}
};
```

This breaks circular `#include` chains and dramatically reduces incremental build times in large projects.

## Anonymous and Inline Namespaces

An **anonymous namespace** makes names visible only within the current translation unit — the preferred replacement for `static` at file scope:

```cpp
// In adder.cpp
namespace {
    const int PIPE_DEPTH = 4;   // visible only in this file
}
```

An **inline namespace** lets a versioned sub-namespace act as if its names were in the enclosing namespace — used in TLM 2.0 versioning (`tlm::tlm_2_0`).

## Common Pitfalls

- **Using `using namespace std;` in a header** — every includer gets the entire `std` namespace, which can silently shadow local names (e.g., `count`, `max`, `left`).
- **Missing include guards** — double-inclusion causes redefinition errors. Prefer `#pragma once` for simplicity.
- **Circular includes** — if A.h includes B.h and B.h includes A.h, the compiler loops. Use forward declarations to break the cycle.
- **Confusing `using` declaration and directive** — importing one name (`using foo::Bar`) is almost always safer than importing all names (`using namespace foo`).

> **Interview answer:** Namespaces prevent name collisions in large codebases by scoping identifiers under a qualified prefix. In SystemC, all library types live in `sc_core` and `sc_dt`; keeping your own model types in a project-specific namespace and using `#pragma once` with self-contained headers makes the codebase maintainable and prevents inadvertent symbol conflicts with the simulator internals.
