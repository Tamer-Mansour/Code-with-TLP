# Big-Endian vs Little-Endian

Endianness describes the order in which bytes of a multi-byte value are stored in memory. It is one of the most fundamental — and frequently misunderstood — concepts in embedded systems, computer architecture, and network programming. Getting it wrong causes silent data corruption that can take days to debug.

## The Core Idea

Consider the 32-bit hexadecimal value `0xDEADBEEF`. It occupies four consecutive bytes in memory. The question endianness answers is: which byte goes at the lowest address?

| Scheme | Address N | Address N+1 | Address N+2 | Address N+3 |
|---|---|---|---|---|
| Big-Endian (BE) | `0xDE` | `0xAD` | `0xBE` | `0xEF` |
| Little-Endian (LE) | `0xEF` | `0xBE` | `0xAD` | `0xDE` |

**Big-Endian** stores the most significant byte (MSB) at the lowest address — just like how humans write numbers (thousands before units).

**Little-Endian** stores the least significant byte (LSB) at the lowest address. x86, x86-64, and ARM (in its default mode) are all little-endian.

## Why It Matters

- **Network protocols** (Ethernet, IP, TCP) use big-endian byte order, also called "network byte order". POSIX provides `htonl()`, `ntohl()`, `htons()`, `ntohs()` to convert between host and network order.
- **File formats** must document their endianness. ELF binaries encode their byte order in the header at offset 5 (`EI_DATA`).
- **SystemC / TLM simulations** that bridge two subsystems with different endianness must explicitly swap bytes in the interconnect model or the initiator's payload.
- **Debugging** with a logic analyzer or hexdump becomes confusing if you forget which endianness the target uses.

## Detecting Endianness at Runtime

```c
#include <stdint.h>
#include <stdio.h>

int is_little_endian(void) {
    uint32_t word = 0x00000001;
    uint8_t  *byte_ptr = (uint8_t *)&word;
    return byte_ptr[0] == 1;   /* LSB at lowest address => little-endian */
}

int main(void) {
    printf("%s-endian\n", is_little_endian() ? "little" : "big");
    return 0;
}
```

The union trick is equally common:

```c
union {
    uint32_t word;
    uint8_t  bytes[4];
} probe = { .word = 0xDEADBEEF };

/* On a little-endian machine: bytes[0] == 0xEF */
```

## Worked Example: Storing 0x12345678

Suppose the value `0x12345678` is written to address `0x1000`.

```
Address:   0x1000  0x1001  0x1002  0x1003
Big-endian:   12      34      56      78
Little-endian:78      56      34      12
```

To read the value back correctly you must know which convention was used when writing it. This is why protocols and file formats always specify endianness explicitly.

## Common Pitfalls

- **Casting a pointer and reading the raw bytes** without accounting for endianness is undefined behaviour in C++ and a portability bug in C.
- **Memcpy is safe; pointer casts are not** — copying bytes through `memcpy` into a properly typed variable respects the local platform's endianness.
- **Bitfields** in C structs have implementation-defined layout, making them unreliable for hardware register maps that cross machine boundaries.
- ARM processors can switch endianness per memory region (BIGENDINIT signal), so never assume ARM == little-endian unconditionally.

## Interview Answer

> "Big-endian places the most significant byte at the lowest address; little-endian places the least significant byte there. x86 is little-endian; network protocols use big-endian. In TLM models you must swap bytes in the payload when bridging the two domains."
