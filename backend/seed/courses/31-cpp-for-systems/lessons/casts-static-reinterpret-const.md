# C++ Casts: static_cast, reinterpret_cast, const_cast

C++ provides four named cast operators to replace the catch-all C-style cast `(Type)expr`. Each named cast expresses a specific intent and is searchable with `grep`. Using the right cast makes code safer, clearer, and easier to audit.

## Why Avoid C-Style Casts?

```cpp
int x = 42;
double d = (double)x;   // C-style: could be static, reinterpret, or const_cast
                         // — ambiguous at a glance
```

A C-style cast tries casts in this order: `const_cast` → `static_cast` → `reinterpret_cast`. It silently selects the first one that compiles — which may not be what you intended.

## `static_cast` — Well-Defined Conversions

Use `static_cast` for conversions that are valid and well-defined: numeric type conversions, upcasts/downcasts in an inheritance hierarchy, `void*` to/from typed pointer (in C++, only with care).

```cpp
double pi = 3.14159;
int truncated = static_cast<int>(pi);   // 3 — truncates toward zero

uint32_t u = 300;
uint8_t  narrow = static_cast<uint8_t>(u);  // 44 — explicit truncation
                                              // compiler won't warn now

// Pointer upcast (always safe, implicit is fine too)
class Base {};
class Derived : public Base {};
Derived* d = new Derived;
Base* b = static_cast<Base*>(d);  // upcast

// Downcast — only safe if you know the runtime type
Derived* d2 = static_cast<Derived*>(b);  // no runtime check — use dynamic_cast if unsure
```

`static_cast` is checked at compile time but not at runtime. For safe polymorphic downcasts, use `dynamic_cast` (requires RTTI and a virtual function).

## `reinterpret_cast` — Bit Pattern Reinterpretation

`reinterpret_cast` tells the compiler to treat the bits of one type as if they were another type. It generates no machine code — it is purely a type-system instruction to stop complaining.

```cpp
// Read hardware register at fixed address
volatile uint32_t* reg = reinterpret_cast<volatile uint32_t*>(0xFFFE0000);
*reg = 0x01;  // write to memory-mapped I/O

// Safe type punning: use memcpy or bit_cast instead!
float f = 1.0f;
uint32_t bits = reinterpret_cast<uint32_t&>(f);  // technically UB (strict aliasing)

// Preferred: memcpy for type punning
uint32_t safe_bits;
std::memcpy(&safe_bits, &f, sizeof(f));  // defined behavior
// C++20: std::bit_cast<uint32_t>(f)     // also defined
```

`reinterpret_cast` between unrelated pointer types violates the **strict aliasing rule** unless the target is `char*`, `unsigned char*`, or `std::byte*`. This is a common source of undefined behavior in low-level code.

```cpp
int x = 42;
char* bytes = reinterpret_cast<char*>(&x);  // OK — char* can alias anything
for (size_t i = 0; i < sizeof(x); ++i)
    printf("%02X ", (unsigned char)bytes[i]);  // print raw bytes
```

## `const_cast` — Adding or Removing const

`const_cast` is the only cast that can add or remove `const` (or `volatile`). Removing `const` from an originally-const object and then writing through it is undefined behavior.

```cpp
// Legitimate use: calling a legacy C API that lacks const correctness
void old_c_api(char* s);  // should be const char* but isn't

const char* msg = "hello";
old_c_api(const_cast<char*>(msg));  // OK if old_c_api doesn't modify the string

// DANGEROUS: writing through a removed const is UB
const int ci = 42;
int* p = const_cast<int*>(&ci);
*p = 99;  // undefined behavior — ci may be in read-only memory
```

## `dynamic_cast` — Safe Polymorphic Downcast

Though not the focus here, `dynamic_cast` completes the set. It checks the runtime type and returns `nullptr` (for pointers) or throws `std::bad_cast` (for references) if the cast fails.

```cpp
Base* b = get_object();
Derived* d = dynamic_cast<Derived*>(b);
if (d != nullptr) {
    d->derived_method();  // safe
}
```

It requires at least one virtual function in the class hierarchy and RTTI to be enabled.

## Quick Reference

| Cast | What it does | When to use |
|------|-------------|-------------|
| `static_cast` | Well-defined type conversions | Numeric conversions, hierarchy casts |
| `reinterpret_cast` | Bit-pattern reinterpretation | Hardware registers, serialization |
| `const_cast` | Add/remove `const`/`volatile` | Interfacing with non-const-correct APIs |
| `dynamic_cast` | Runtime-checked downcast | Polymorphism, when type is unknown |

## The Audit Rule

In a code review, every `reinterpret_cast` and `const_cast` deserves a comment explaining why it is safe. `static_cast` is benign by comparison. A `const_cast` that removes `const` and then writes through the pointer is almost always a bug.

**Interview answer:** "static_cast handles well-defined conversions and is checked at compile time. reinterpret_cast reinterprets the bit pattern with no generated code — essential for hardware registers but violates strict aliasing if misused. const_cast is the only way to legally remove const, but writing through a pointer to a genuinely const object is undefined behavior."
