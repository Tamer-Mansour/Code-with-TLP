# Bytes, char, and Reading Raw Buffers

Raw binary data is almost always processed through `char*` or `unsigned char*` buffers in C and C++. Understanding the type system rules around these pointer types — and why they are special — prevents aliasing bugs and undefined behaviour.

## `char`, `unsigned char`, and `std::byte`

C++ has three one-byte types:

| Type | Signed? | Special aliasing permission? | Use case |
|------|---------|-------------------------------|----------|
| `char` | Implementation-defined | Yes | Text, string literals |
| `unsigned char` | No (always 0–255) | Yes | Raw byte I/O, type punning |
| `signed char` | Yes (-128–127) | Yes | Explicit signed byte |
| `std::byte` (C++17) | N/A (not arithmetic) | Yes (via `std::bit_cast` etc.) | Semantic clarity for raw bytes |

The special aliasing permission means the C++ strict aliasing rule allows you to read any object's bytes through a `char*`, `unsigned char*`, or `signed char*` — but not through `int*`, `float*`, or any other pointer type.

## Reading Raw Bytes Portably

```cpp
#include <cstdint>
#include <cstring>
#include <cstdio>

int main() {
    uint32_t value = 0xDEADBEEF;

    // Legal: char* can alias any object
    const unsigned char* p = reinterpret_cast<const unsigned char*>(&value);

    for (int i = 0; i < 4; ++i) {
        printf("byte[%d] = 0x%02X\n", i, p[i]);
    }
    // On little-endian: EF BE AD DE
}
```

You may also use `memcpy` to copy bytes out without even needing an alias:

```cpp
uint8_t buf[4];
std::memcpy(buf, &value, 4);   // always safe, no aliasing concern
```

## Parsing a Binary Buffer

A common pattern in systems code is parsing a raw byte stream into structured fields. Never cast the buffer pointer directly to a struct type — use `memcpy` to extract each field:

```cpp
#include <cstdint>
#include <cstring>

struct Packet {
    uint8_t  type;
    uint32_t seq;
    uint16_t data_len;
};

Packet parse(const uint8_t* buf) {
    Packet p;
    p.type = buf[0];

    uint32_t seq_raw;
    std::memcpy(&seq_raw, buf + 1, 4);
    p.seq = __builtin_bswap32(seq_raw);  // big-endian on wire

    uint16_t len_raw;
    std::memcpy(&len_raw, buf + 5, 2);
    p.data_len = __builtin_bswap16(len_raw);

    return p;
}
```

## The Strict Aliasing Rule (Brief)

The compiler is permitted to assume that pointers to different types do not point to the same memory. This allows aggressive optimisations. Violating it leads to miscompilations that are hard to debug because they only appear under optimisation:

```cpp
// UNDEFINED BEHAVIOUR — strict aliasing violation
float f = 3.14f;
uint32_t bits = *reinterpret_cast<uint32_t*>(&f);  // DO NOT DO THIS

// CORRECT: use memcpy or std::bit_cast (C++20)
uint32_t bits;
std::memcpy(&bits, &f, 4);                          // always correct

// C++20:
uint32_t bits2 = std::bit_cast<uint32_t>(f);        // cleanest
```

## `std::byte` for Semantic Clarity

`std::byte` (from `<cstddef>`) signals to the reader that a buffer holds raw bytes, not characters or arithmetic values:

```cpp
#include <cstddef>
#include <cstring>

void process(std::byte* buf, std::size_t len) {
    // buf[0] | std::byte{0x0F} — bitwise ops allowed, arithmetic ops not
    for (std::size_t i = 0; i < len; ++i) {
        buf[i] &= std::byte{0x7F};   // mask the high bit
    }
}
```

Arithmetic operators like `+` and `*` are intentionally not defined on `std::byte`, preventing accidental misuse as a numeric type.

## Common Pitfalls

- **Printing `char` as hex**: `printf("%02X", buf[i])` works only if `buf[i]` is `unsigned char` or cast to `unsigned`. A `signed char` with value `0xFF` will be sign-extended to `0xFFFFFFFF` before printing.
- **Off-by-one in buffer parsing**: multi-byte fields start at a specific byte offset; always track offsets carefully or use a cursor variable.
- **Assuming `CHAR_BIT == 8`**: on DSPs and embedded targets, `char` may be 16 bits. Use `<climits>` `CHAR_BIT` if true portability is needed; for network code it is always 8.

## Worked Example: Hex Dump

```cpp
#include <cstdio>
#include <cstdint>

void hex_dump(const void* data, std::size_t len) {
    const auto* p = static_cast<const unsigned char*>(data);
    for (std::size_t i = 0; i < len; ++i) {
        printf("%02X ", p[i]);
        if ((i + 1) % 16 == 0) putchar('\n');
    }
    if (len % 16 != 0) putchar('\n');
}
```

> **Interview answer:** `unsigned char*` and `char*` are special in C++ — they are the only pointer types allowed to alias any other object under the strict aliasing rule. Use `memcpy` to move bytes between typed objects and raw buffers safely. In C++20, `std::bit_cast` is the zero-copy alternative.
