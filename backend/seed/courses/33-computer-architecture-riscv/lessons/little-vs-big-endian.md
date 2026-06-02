# Little-Endian vs Big-Endian

Both byte orders are in active use today. Understanding the difference in concrete terms — and knowing which systems use which — is essential for systems programming, network code, and binary file parsing.

## Side-by-Side Comparison

Consider storing the 64-bit value `0xDEADBEEF_CAFEBABE` starting at address `0x2000`.

| Address | Little-Endian | Big-Endian |
|---------|--------------|-----------|
| 0x2000  | 0xBE        | 0xDE      |
| 0x2001  | 0xBA        | 0xAD      |
| 0x2002  | 0xFE        | 0xBE      |
| 0x2003  | 0xCA        | 0xEF      |
| 0x2004  | 0xEF        | 0xCA      |
| 0x2005  | 0xBE        | 0xFE      |
| 0x2006  | 0xAD        | 0xBA      |
| 0x2007  | 0xDE        | 0xBE      |

Little-endian starts with the "little end" (`0xBE` is the LSB of the lower 32-bit word). Big-endian starts with the "big end" (`0xDE`).

## Which Systems Use Which?

**Little-endian:**
- x86 and x86-64 (Intel, AMD) — all modern PCs and servers
- ARM in its default configuration (ARMv7, AArch64)
- RISC-V in its standard configuration
- Most modern embedded controllers (AVR, ESP32, STM32)

**Big-endian:**
- Network byte order (TCP/IP, UDP headers, DNS, HTTP/2 frames)
- IBM POWER and System z (mainframes)
- SPARC
- Many binary file formats (TIFF, AIFF, Java `.class` files, Motorola S-records)

**Bi-endian (configurable at boot or per-instruction):**
- ARM (can be switched; most OSes run little-endian)
- PowerPC
- MIPS
- RISC-V (the spec allows big-endian extensions, but nearly all implementations are little-endian)

## Memory Diagram for a 32-bit Integer

```
Value: 0xAABBCCDD

Little-endian layout (x86):
  Low addr  ──→  High addr
  [ DD ] [ CC ] [ BB ] [ AA ]
         LSB first

Big-endian layout (network):
  Low addr  ──→  High addr
  [ AA ] [ BB ] [ CC ] [ DD ]
         MSB first
```

## Reading Back the Value

Both orderings are internally consistent. When the CPU reads back the bytes it stored, it produces the correct value. The mismatch only appears when:

- One system writes bytes and another system reads them.
- Code interprets raw byte arrays as integers.

```c
// Manually reconstruct a 32-bit big-endian integer from a byte buffer
uint32_t read_be32(const uint8_t *buf) {
    return ((uint32_t)buf[0] << 24) |
           ((uint32_t)buf[1] << 16) |
           ((uint32_t)buf[2] <<  8) |
           ((uint32_t)buf[3]      );
}

// Manually reconstruct a 32-bit little-endian integer from a byte buffer
uint32_t read_le32(const uint8_t *buf) {
    return ((uint32_t)buf[3] << 24) |
           ((uint32_t)buf[2] << 16) |
           ((uint32_t)buf[1] <<  8) |
           ((uint32_t)buf[0]      );
}
```

## A Subtle Advantage of Each

**Little-endian advantage**: If you only need the lower bytes of an integer (e.g., truncating a 32-bit int to 16-bit), you can simply read from the same starting address without any offset arithmetic. The LSB is always at offset 0.

**Big-endian advantage**: The most significant digit comes first, matching the human convention of writing numbers. This makes hex dumps easier to read and is why network protocols standardized on it.

## Common Pitfall: Casting Pointers

```c
uint32_t x = 0x01020304;
uint8_t lo = *(uint8_t *)&x;   // 0x04 on little-endian, 0x01 on big-endian
```

This kind of pointer cast produces different values on different architectures — a classic portability bug.

> **Interview answer:** Little-endian stores the LSB at the lowest address (used by x86, ARM, RISC-V); big-endian stores the MSB first (used by network protocols and some mainframes). Both are internally consistent; the mismatch only matters when bytes are shared between systems or interpreted directly as integers.
