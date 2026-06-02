# Big-Endian vs Little-Endian: What Is the Difference?

Endianness describes the order in which bytes of a multi-byte integer are stored in memory. It is one of those topics that seems trivial until you are debugging a network protocol at 2 AM or trying to read a binary file written on a different architecture.

## The Core Concept

Consider the 32-bit integer `0x12345678`. It occupies four bytes. The question is: which byte goes to the lowest memory address?

| Byte | Value |
|------|-------|
| Most significant byte (MSB) | `0x12` |
| Next | `0x34` |
| Next | `0x56` |
| Least significant byte (LSB) | `0x78` |

**Big-endian** stores the most significant byte at the lowest address — just like how we write numbers on paper, left to right, big end first.

**Little-endian** stores the least significant byte at the lowest address — the "little end" comes first.

```
Address:    0x1000  0x1001  0x1002  0x1003
Big-endian:   0x12    0x34    0x56    0x78
Little-endian:0x78    0x56    0x34    0x12
```

## Which Systems Use Which?

- **Little-endian**: x86, x86-64 (Intel/AMD), ARM (in LE mode, default on Linux/Windows)
- **Big-endian**: Network byte order (TCP/IP), IBM POWER (historically), SPARC (historically), Motorola 68k
- **Bi-endian**: ARM, MIPS, and PowerPC can switch modes; the OS picks one at boot

## Seeing It in C++

You can inspect endianness directly by peeking at memory:

```cpp
#include <cstdint>
#include <cstring>
#include <cstdio>

int main() {
    uint32_t value = 0x12345678;
    uint8_t bytes[4];
    std::memcpy(bytes, &value, 4);  // safe alias

    printf("Byte at lowest address: 0x%02X\n", bytes[0]);
    // Little-endian machine: prints 0x78
    // Big-endian machine:    prints 0x12
}
```

Using `memcpy` (not a cast through `uint8_t*`) is the correct, defined-behavior way to inspect raw bytes in C++.

## Why It Matters

- **Binary file formats**: a `.wav` or `.bmp` file specifies a fixed byte order. Reading it on the wrong-endian machine gives garbage values unless you swap.
- **Network protocols**: TCP/IP mandates big-endian (network byte order). Sending a `uint32_t` directly from an x86 machine sends it in little-endian — the receiver reads the wrong number.
- **Cross-platform serialization**: any time you write raw integers to disk or a socket and read them on a potentially different machine, you must agree on byte order.
- **Hardware registers**: embedded firmware reads 16-bit or 32-bit peripheral registers whose byte layout is fixed by the hardware datasheet.

## Common Pitfall

The classic bug is casting a pointer to reinterpret bytes without accounting for endianness:

```cpp
// WRONG on a little-endian machine if you expect big-endian data
uint32_t val = *reinterpret_cast<uint32_t*>(buffer);
```

This is also undefined behavior due to strict aliasing. Use `memcpy` or `std::bit_cast` (C++20) instead, then byte-swap if needed.

## Worked Example

A binary file stores a 16-bit integer as big-endian `0x01 0xF4` (= 500 decimal). Reading it on a little-endian x86 machine:

```cpp
uint8_t raw[2] = {0x01, 0xF4};  // as read from file
uint16_t val;
std::memcpy(&val, raw, 2);
// val == 0xF401 == 63489 on little-endian — WRONG

// Fix: manual swap
val = (uint16_t)((raw[0] << 8) | raw[1]);
// val == 0x01F4 == 500 — correct
```

> **Interview answer:** Big-endian stores the most significant byte at the lowest address; little-endian stores the least significant byte first. x86/x86-64 is little-endian; network protocols use big-endian. When exchanging binary data across systems, you must explicitly handle byte order.
