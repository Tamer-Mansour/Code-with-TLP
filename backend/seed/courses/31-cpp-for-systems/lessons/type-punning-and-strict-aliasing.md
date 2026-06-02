# Type Punning, Strict Aliasing, and memcpy

Type punning — reinterpreting the raw bytes of one type as another — is a fundamental systems programming technique for serialization, bit manipulation, and hardware interfacing. It is also one of the most common sources of subtle undefined behavior in C++.

## The Strict Aliasing Rule

The C and C++ standards include the **strict aliasing rule**: the compiler may assume that pointers to different types do not point to the same memory, unless one of the types is `char`, `unsigned char`, or `std::byte`. This assumption enables powerful optimizations — the compiler does not have to reload a value it just stored if it sees no stores through a pointer of the same type.

```cpp
void scale(float* f, int* n, int count) {
    for (int i = 0; i < count; ++i)
        f[i] *= *n;   // compiler assumes f and n never alias
                      // so *n is hoisted out of the loop
}
```

Violating strict aliasing is **undefined behavior**. The compiler is free to generate code that ignores the aliased write entirely.

## Unsafe Type Punning (Undefined Behavior)

### Pointer Cast — UB

```cpp
float f = 1.0f;
// WRONG: violates strict aliasing — compiler may optimize away the store
uint32_t bits = *(uint32_t*)(&f);
```

### Union Pun — UB in C++ (well-defined in C)

```cpp
union Pun { float f; uint32_t i; };
Pun p;
p.f = 1.0f;
uint32_t bits = p.i;   // reading inactive member → UB in C++
                       // defined in C (C11 §6.5.2.3), and as a
                       // GCC/Clang extension in C++
```

GCC documents the union pun as defined behavior even in C++ mode, but the standard does not guarantee it — it is a dangerous habit in portable code.

## Safe Type Punning with `memcpy`

The correct, portable, zero-UB way to type-pun is `memcpy`. With constant size and trivially-copyable types, every modern compiler optimizes this to a single register move or load instruction — there is no runtime overhead.

```cpp
#include <cstring>
#include <cstdint>

float f = 1.0f;
uint32_t bits;
std::memcpy(&bits, &f, sizeof(bits));
// bits == 0x3F800000 — IEEE 754 representation of 1.0f

float restored;
std::memcpy(&restored, &bits, sizeof(restored));
// restored == 1.0f
```

Both types must be **trivially copyable** (no user-defined copy constructor, destructor, or virtual functions) for `memcpy` to be valid.

```cpp
static_assert(std::is_trivially_copyable_v<float>);
static_assert(std::is_trivially_copyable_v<uint32_t>);
```

## C++20: `std::bit_cast`

C++20 introduced `std::bit_cast<To>(from)` as the language-blessed, `constexpr`-capable type pun:

```cpp
#include <bit>

constexpr float f = 1.0f;
constexpr uint32_t bits = std::bit_cast<uint32_t>(f);   // 0x3F800000
static_assert(bits == 0x3F800000u);
```

`std::bit_cast` requires:
- `sizeof(To) == sizeof(From)`
- Both types are trivially copyable

It is the preferred approach in modern C++.

## `std::byte` as a Portable Aliasing Type

`std::byte` (C++17) is an alias-safe byte type, similar to `unsigned char`. You can legally view any object's bytes through a `std::byte*`:

```cpp
#include <cstddef>

float f = 3.14f;
auto* p = reinterpret_cast<std::byte*>(&f);
// Reading p[0..3] is defined — std::byte aliases any type
```

This is useful for generic serialization code.

## `__attribute__((may_alias))` (GCC Extension)

GCC provides `__attribute__((may_alias))` to mark a type as allowed to alias anything — the mechanism that makes `uint8_t` an alias for `unsigned char` on GCC:

```cpp
typedef uint32_t __attribute__((may_alias)) aliasing_u32;
float f = 1.0f;
aliasing_u32 bits = *(aliasing_u32*)&f;   // defined with this typedef
```

This is a compiler extension and not portable.

## Summary: Hierarchy of Correctness

| Method | Standard? | `constexpr`? | Verdict |
|---|---|---|---|
| Pointer cast (`*(T*)&x`) | No | No | Always UB |
| Union pun | No (C++ only) | No | Avoid |
| `memcpy` | Yes | No | Correct, portable |
| `std::bit_cast` | Yes (C++20) | Yes | Best modern approach |
| `std::byte*` aliasing | Yes (C++17) | No | Good for byte loops |

## The `-fno-strict-aliasing` Flag

`-fno-strict-aliasing` disables the strict aliasing optimization in GCC/Clang, making pointer-cast puns "work" in practice. The Linux kernel uses this flag for historical reasons. In new code, fix the UB properly rather than relying on this flag.

```bash
g++ -O2 -fno-strict-aliasing my_file.cpp   # masks the bug, not recommended
```

> **Interview answer:** The strict aliasing rule lets the compiler assume pointers to different types do not alias, enabling critical optimizations. Casting a pointer to a different type and reading through it is undefined behavior. The safe way to type-pun is `std::memcpy` (C++11) or `std::bit_cast` (C++20) — compilers optimize both to a single instruction when the size is constant.
