# What Is Endianness?

Endianness describes the order in which a multi-byte value is stored in memory. Because processors work with data wider than one byte — integers of 2, 4, or 8 bytes — every architecture must decide whether the **most-significant byte (MSB)** or the **least-significant byte (LSB)** occupies the lowest memory address.

## The Core Idea

Think of the 32-bit hexadecimal integer `0x12345678`. It occupies four consecutive bytes in memory. The question endianness answers is: which byte comes first?

| Address | Big-Endian | Little-Endian |
|---------|-----------|---------------|
| 0x1000  | 0x12      | 0x78          |
| 0x1001  | 0x34      | 0x56          |
| 0x1002  | 0x56      | 0x34          |
| 0x1003  | 0x78      | 0x12          |

- **Big-endian**: The most significant byte is stored at the lowest address — like writing a number left-to-right the way humans read it.
- **Little-endian**: The least significant byte is stored at the lowest address — the "little end" comes first.

## Why Does It Exist?

Early processor designers made independent decisions about byte ordering. Intel's x86 family chose little-endian for simplicity in incrementing addresses during multi-byte reads. Motorola's 68000 (and later SPARC, PowerPC in big-endian mode) chose big-endian because it matches human-readable hex dumps. Neither choice is inherently superior; the difference only becomes visible when:

1. Data is shared across systems with different byte orders.
2. You interpret raw bytes directly (network packets, binary files, memory-mapped hardware).
3. You cast between pointer types.

## A Mental Model

Imagine the number 1,234 written on paper. In English you write the most significant digit first: "1234". That is big-endian thinking. Now imagine reversing the digits in storage to make arithmetic hardware slightly simpler: "4321" in memory. That is little-endian — the low digit (units place) sits at the lowest position.

## Worked Example in C

```c
#include <stdio.h>
#include <stdint.h>

int main(void) {
    uint32_t value = 0x12345678;
    uint8_t *bytes = (uint8_t *)&value;

    printf("Byte at offset 0: 0x%02X\n", bytes[0]);
    printf("Byte at offset 1: 0x%02X\n", bytes[1]);
    printf("Byte at offset 2: 0x%02X\n", bytes[2]);
    printf("Byte at offset 3: 0x%02X\n", bytes[3]);
    return 0;
}
```

On a little-endian x86 machine the output is:

```
Byte at offset 0: 0x78
Byte at offset 1: 0x56
Byte at offset 2: 0x34
Byte at offset 3: 0x12
```

On a big-endian machine (SPARC, network byte order) it would be `0x12, 0x34, 0x56, 0x78`.

## Key Terminology

- **MSB (Most Significant Byte)**: The byte carrying the highest-value bits (e.g., `0x12` in `0x12345678`).
- **LSB (Least Significant Byte)**: The byte carrying the lowest-value bits (e.g., `0x78` in `0x12345678`).
- **Network byte order**: Officially big-endian, defined by Internet standards (RFC 1700).
- **Host byte order**: Whatever the local machine uses — often little-endian on modern desktops.

## Common Pitfall

Endianness only affects **multi-byte values**. A single `uint8_t` (one byte) is unaffected — there is no ordering within a single byte. Bit ordering within a byte is a separate concept (bit-endianness) and is almost never relevant in software.

> **Interview answer:** Endianness is the byte ordering used when a multi-byte value is stored in memory. Little-endian stores the least significant byte at the lowest address; big-endian stores the most significant byte first. x86 is little-endian; network protocols use big-endian (network byte order).
