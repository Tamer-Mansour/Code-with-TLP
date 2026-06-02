# Detecting Endianness at Runtime

Most code should use well-defined APIs rather than probing byte order, but knowing how to detect endianness at runtime is a core systems skill and a frequent interview topic.

## The Classic Union Trick (C)

The most common portable runtime check uses a `union` to overlap a multi-byte integer with an array of bytes:

```c
#include <stdint.h>
#include <stdbool.h>

bool is_little_endian(void) {
    union {
        uint32_t word;
        uint8_t  bytes[4];
    } probe = { .word = 0x00000001 };

    return probe.bytes[0] == 1;   // 1 at offset 0 → LSB first → little-endian
}
```

If the machine is little-endian, the value `1` places `0x01` at the lowest address (`bytes[0]`). On a big-endian machine `bytes[0]` holds `0x00` and `bytes[3]` holds `0x01`.

## The Pointer Cast Approach

An alternative that avoids the union:

```c
#include <stdint.h>

int detect_endianness(void) {
    uint16_t x = 0x0100;
    return *((uint8_t *)&x);   // returns 1 if big-endian, 0 if little-endian
}
```

This is technically undefined behavior in C++ (strict aliasing), so the union approach is preferred in portable code.

## Compile-Time Detection

Modern compilers and standard headers expose macros you can test before the program even runs:

```c
#if defined(__BYTE_ORDER__) && defined(__ORDER_LITTLE_ENDIAN__)
  #if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    #define MY_LITTLE_ENDIAN 1
  #else
    #define MY_BIG_ENDIAN 1
  #endif
#elif defined(__LITTLE_ENDIAN__)
    #define MY_LITTLE_ENDIAN 1
#elif defined(__BIG_ENDIAN__)
    #define MY_BIG_ENDIAN 1
#endif
```

On Linux you can also include `<endian.h>` and check `__BYTE_ORDER == __LITTLE_ENDIAN`.

## Python Runtime Detection

Python exposes byte order through the `sys` and `struct` modules:

```python
import sys
import struct

# sys.byteorder returns 'little' or 'big'
print(sys.byteorder)

# struct.pack uses native byte order with '@' or '='
val = struct.pack("=I", 0x01020304)
print(val.hex())   # e.g. '04030201' on little-endian
```

## Worked Example: A Self-Describing Binary Header

A robust binary format encodes its own byte order so readers can adapt:

```c
#define MAGIC_LE 0x454C494C   // 'LILE' in ASCII
#define MAGIC_BE 0x4C494C45   // 'ELIL' in ASCII

void write_header(FILE *f) {
    uint32_t magic;
    if (is_little_endian()) magic = MAGIC_LE;
    else                    magic = MAGIC_BE;
    fwrite(&magic, sizeof(magic), 1, f);
}
```

The reader checks the magic bytes first. If they are reversed, the reader knows it must byte-swap all subsequent fields.

## The `__builtin_bswap` Family (GCC/Clang)

When you need byte order information at compile time to generate efficient swap code, GCC and Clang provide:

```c
uint16_t swap16(uint16_t x) { return __builtin_bswap16(x); }
uint32_t swap32(uint32_t x) { return __builtin_bswap32(x); }
uint64_t swap64(uint64_t x) { return __builtin_bswap64(x); }
```

These compile to a single `bswap` instruction on x86 — far more efficient than a manual byte shuffle.

## Summary Table

| Method              | Language | When to Use                              |
|---------------------|----------|------------------------------------------|
| Union trick         | C        | Portable runtime check                   |
| `sys.byteorder`     | Python   | Quick scripting check                    |
| `__BYTE_ORDER__`    | C/C++    | Conditional compilation                  |
| `<endian.h>`        | Linux C  | POSIX-style compile-time check           |
| Magic bytes in file | Any      | Let readers self-detect and swap         |

> **Interview answer:** The canonical C runtime check stores `0x00000001` in a `uint32_t`, then reads the first byte via a `uint8_t` pointer or union. If it is `1`, the machine is little-endian. For compile-time detection use `__BYTE_ORDER__` macros; for Python use `sys.byteorder`.
