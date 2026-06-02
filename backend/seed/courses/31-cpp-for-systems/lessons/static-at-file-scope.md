# static at File Scope and Internal Linkage

When `static` is applied to a variable or function at **file scope** (outside any function or class), it does not affect the lifetime — everything at file scope already lives for the whole program. Instead, it controls **linkage**.

## Linkage Explained

Linkage determines whether a name is visible to the linker across translation units (`.cpp` files).

| Linkage | Meaning |
|---|---|
| **External** (default for non-const globals and non-static functions) | Name exported; other `.cpp` files can `extern` it |
| **Internal** | Name stays in this translation unit; linker cannot see it |
| **No linkage** | Local variables — no linker involvement |

```cpp
// file: a.cpp
int    global_counter = 0;         // external linkage — other files can access
static int  local_counter = 0;     // internal linkage — invisible outside a.cpp
static void helper() { /* ... */ } // internal linkage — invisible outside a.cpp
```

## Why Internal Linkage Matters

**Avoiding name collisions:** Large codebases often have helper functions with common names (`init`, `reset`, `write`). Without `static`, two translation units defining the same name would violate the **One Definition Rule** and cause a linker error.

```cpp
// uart.cpp
static void reset() { /* UART reset logic */ }

// spi.cpp
static void reset() { /* SPI reset logic */ }
// No linker conflict — both are internal to their own file
```

**Encapsulation at the file level:** `static` is the C-style alternative to unnamed namespaces for hiding implementation details.

## anonymous namespaces vs static

In modern C++, the preferred way to express internal linkage is an **unnamed namespace**:

```cpp
namespace {
    int helper_counter = 0;   // internal linkage, C++ style
    void helper() { }
}
```

Both `static` (for free functions/variables) and unnamed namespaces produce internal linkage. The unnamed namespace also works for types and templates, which `static` cannot mark with internal linkage.

| Approach | Works for | Standard recommendation |
|---|---|---|
| `static` | Variables, functions | Legacy C code, C-compatible headers |
| Unnamed `namespace {}` | Variables, functions, types, templates | Preferred C++ style |

## Practical Systems Example

```cpp
// driver_core.cpp — internal implementation details

static const uint32_t BASE_ADDR = 0x4000'0000;   // never exported

static uint32_t read_reg(uint32_t offset) {
    return *(volatile uint32_t*)(BASE_ADDR + offset);
}

static void write_reg(uint32_t offset, uint32_t val) {
    *(volatile uint32_t*)(BASE_ADDR + offset) = val;
}

// Public API — external linkage (no static)
void driver_init() {
    write_reg(0x00, 0x01);
}
```

The `read_reg` / `write_reg` helpers and `BASE_ADDR` are invisible to the rest of the codebase. Only `driver_init` is exported.

## Common Pitfalls

- **`static` in headers is dangerous.** Each `.cpp` that includes the header gets its own private copy of the variable — silent data duplication instead of sharing.
- **Confusion with `static` locals and class statics.** The keyword has three distinct meanings depending on context: internal linkage (file scope), persistent lifetime (local scope), and shared member (class scope).
- **Link-time visibility tools.** On Linux, `nm -u` shows undefined external symbols; `nm | grep ' T '` shows exported functions. Use these to verify your internal helpers don't accidentally leak.

> **Interview answer:** "`static` at file scope gives a variable or function internal linkage, meaning the linker cannot see the symbol outside that translation unit. It prevents name collisions and hides implementation details, similar to an unnamed namespace in modern C++."
