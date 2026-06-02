# Detecting and Reasoning About Host Endianness

Before you can correct for endianness, you need to know what endianness the running machine uses. There are several techniques — compile-time macros, runtime checks, and modern C++20 facilities — each with trade-offs.

## Runtime Detection

The classic runtime approach inspects the first byte of a known integer:

```cpp
#include <cstdint>
#include <cstring>
#include <cstdio>

bool is_little_endian() {
    uint32_t x = 1;
    uint8_t first_byte;
    std::memcpy(&first_byte, &x, 1);
    return first_byte == 1;  // LSB is at lowest address → little-endian
}

int main() {
    puts(is_little_endian() ? "Little-endian" : "Big-endian");
}
```

This is always correct, costs essentially nothing, and avoids undefined behavior by using `memcpy`.

### Union Trick (Common but Technically UB in C++)

You will frequently see this in older codebases:

```cpp
union Probe { uint32_t i; uint8_t b[4]; };
Probe p; p.i = 1;
bool le = (p.b[0] == 1);  // type-punning via union is UB in C++, defined in C99
```

It works in practice on every real compiler, but the C++ standard marks reading from a union member that was not last written as undefined behavior. Prefer `memcpy`.

## Compile-Time Detection

Many projects use preprocessor macros to branch at compile time, which eliminates runtime cost entirely:

```cpp
#if defined(__BYTE_ORDER__) && defined(__ORDER_LITTLE_ENDIAN__)
  #if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    #define HOST_LITTLE_ENDIAN 1
  #else
    #define HOST_BIG_ENDIAN 1
  #endif
#elif defined(_WIN32)
  // Windows on x86/x86-64 is always little-endian
  #define HOST_LITTLE_ENDIAN 1
#endif
```

GCC and Clang expose `__BYTE_ORDER__`, `__ORDER_LITTLE_ENDIAN__`, and `__ORDER_BIG_ENDIAN__`. MSVC does not define these, but Windows only runs on little-endian hardware (x86, ARM in LE mode).

## C++20: `std::endian`

C++20 standardised endianness detection in `<bit>`:

```cpp
#include <bit>
#include <cstdio>

int main() {
    if constexpr (std::endian::native == std::endian::little) {
        puts("little-endian");
    } else if constexpr (std::endian::native == std::endian::big) {
        puts("big-endian");
    } else {
        puts("mixed-endian (exotic)");  // PDP-11 nostalgia
    }
}
```

`if constexpr` means the check is resolved at compile time, so there is zero runtime cost and the compiler can eliminate dead branches.

## Reasoning About Endianness Without Running Code

When reading code or a spec you need to reason statically:

1. **Target architecture**: x86/x86-64/ARM-LE → little-endian. MIPS/SPARC/PowerPC-BE → big-endian.
2. **ABI documents**: the System V AMD64 ABI and the ARM ABI both specify little-endian as default on modern Linux.
3. **Protocol specs**: "values are in network byte order" always means big-endian.

## Pitfalls

- **Assuming the host**: code that assumes `HOST_LITTLE_ENDIAN` without a compile guard will silently produce wrong results on a MIPS router or a SPARC server.
- **Mixed-endian structs**: some hardware (old ARM Cortex-M in FPU) stores `double` in a mixed-endian "middle-endian" layout. `std::endian::mixed` covers this case.
- **Endianness vs. bit order**: endianness is about byte order, not bit order. Bit fields within a byte have their own, compiler-defined ordering — another reason to avoid bit fields in wire formats.

## Quick Decision Guide

| Situation | Preferred technique |
|-----------|---------------------|
| C++20 project | `std::endian::native` with `if constexpr` |
| Older GCC/Clang project | `__BYTE_ORDER__` macros |
| Purely runtime, portable | `memcpy` probe of `uint32_t{1}` |
| Windows-only code | Assume little-endian safely |

> **Interview answer:** Use `std::endian::native` in C++20 for a zero-cost compile-time check. For older code, inspect the first byte of `uint32_t x = 1` via `memcpy` — if it equals `1`, the machine is little-endian.
