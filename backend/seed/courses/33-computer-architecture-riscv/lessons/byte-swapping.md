# Byte Swapping and Conversion Routines

Byte swapping reverses the byte order of a multi-byte integer — turning a little-endian value into big-endian, or vice versa. It is the fundamental primitive behind all endianness conversion.

## What a Byte Swap Does

For a 32-bit value `0xAABBCCDD`:

```
Before swap:  [ AA ] [ BB ] [ CC ] [ DD ]
After swap:   [ DD ] [ CC ] [ BB ] [ AA ]
Result: 0xDDCCBBAA
```

Each byte moves to the mirror position. This is its own inverse: swapping twice returns the original value.

## Manual Bit-Shift Swap (C)

Understanding the shift-and-mask approach builds the right mental model:

```c
#include <stdint.h>

uint16_t bswap16(uint16_t x) {
    return (uint16_t)((x >> 8) | (x << 8));
}

uint32_t bswap32(uint32_t x) {
    return ((x & 0xFF000000U) >> 24) |
           ((x & 0x00FF0000U) >>  8) |
           ((x & 0x0000FF00U) <<  8) |
           ((x & 0x000000FFU) << 24);
}

uint64_t bswap64(uint64_t x) {
    return ((x & 0xFF00000000000000ULL) >> 56) |
           ((x & 0x00FF000000000000ULL) >> 40) |
           ((x & 0x0000FF0000000000ULL) >> 24) |
           ((x & 0x000000FF00000000ULL) >>  8) |
           ((x & 0x00000000FF000000ULL) <<  8) |
           ((x & 0x0000000000FF0000ULL) << 24) |
           ((x & 0x000000000000FF00ULL) << 40) |
           ((x & 0x00000000000000FFULL) << 56);
}
```

## Compiler Intrinsics (Preferred)

Hand-written shifts are readable but modern compilers often cannot optimize them to a single `bswap` instruction automatically. Use builtins instead:

```c
#include <stdint.h>

// GCC / Clang
uint16_t x16 = __builtin_bswap16(0x1234);   // → 0x3412
uint32_t x32 = __builtin_bswap32(0x12345678); // → 0x78563412
uint64_t x64 = __builtin_bswap64(0x0102030405060708ULL); // → 0x0807060504030201

// MSVC
#include <stdlib.h>
uint16_t y16 = _byteswap_ushort(0x1234);
uint32_t y32 = _byteswap_ulong(0x12345678);
uint64_t y64 = _byteswap_uint64(0x0102030405060708ULL);
```

## POSIX Network Conversion Functions

These are the most common interface in networking code:

```c
#include <arpa/inet.h>

// Convert between host and network (big-endian) byte order
uint32_t net_val = htonl(0x12345678);  // host → network
uint16_t net_port = htons(8080);       // host → network
uint32_t host_val = ntohl(net_val);    // network → host
uint16_t host_port = ntohs(net_port);  // network → host
```

On a little-endian host all four functions perform a byte swap. On a big-endian host they are no-ops. Writing `htonl(x)` is always correct regardless of platform.

## Linux Kernel Helpers

The Linux kernel headers define `cpu_to_be32`, `be32_to_cpu`, `cpu_to_le16`, etc., for all width and direction combinations. User-space programs can use `<byteswap.h>`:

```c
#include <byteswap.h>

uint32_t swapped = bswap_32(0xDEADBEEF);  // → 0xEFBEADDE
```

## Python Struct Module

Python's `struct.pack` / `struct.unpack` handle byte order through format prefixes:

```python
import struct

value = 0x12345678

# Pack as big-endian
be_bytes = struct.pack(">I", value)   # b'\x12\x34\x56\x78'

# Pack as little-endian
le_bytes = struct.pack("<I", value)   # b'\x78\x56\x34\x12'

# Unpack back
print(struct.unpack(">I", le_bytes)[0])  # reads LE bytes as BE → 0x78563412
```

The `int.to_bytes` / `int.from_bytes` methods are an alternative:

```python
n = 0x12345678
be = n.to_bytes(4, "big")     # b'\x12\x34\x56\x78'
le = n.to_bytes(4, "little")  # b'\x78\x56\x34\x12'
print(int.from_bytes(le, "big"))  # 0x78563412
```

## Assembly: The `BSWAP` Instruction (x86)

On x86, a single instruction handles the swap for 32- and 64-bit registers:

```asm
mov  eax, 0x12345678
bswap eax             ; eax = 0x78563412
```

For 16-bit values x86 uses `xchg al, ah` or a `ror` by 8.

## Common Pitfall: Swapping Float/Double

Never byte-swap floating-point values by reinterpreting them as integers unless you also change the endianness of the float representation on the target. The IEEE 754 standard does not mandate byte order. The safe approach is to serialize floats as text or use a format that explicitly specifies representation.

> **Interview answer:** A byte swap reverses the byte order of a multi-byte integer. Use compiler intrinsics (`__builtin_bswap32`) for efficiency, POSIX `htonl`/`ntohl` for network code, or Python's `struct.pack` with `>` / `<` format characters. The operation is its own inverse.
