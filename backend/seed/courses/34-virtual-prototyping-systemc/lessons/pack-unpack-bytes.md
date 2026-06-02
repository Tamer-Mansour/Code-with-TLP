# Pack and Unpack Bytes into Words

Packing and unpacking is the process of combining multiple smaller values into a single wider integer, or splitting a wider integer back into its component bytes. This operation appears constantly in protocol parsers, register-level device drivers, and TLM payload construction.

## The Operations

**Packing** assembles individual bytes into a word:

```c
uint32_t pack_le(uint8_t b0, uint8_t b1, uint8_t b2, uint8_t b3) {
    /* b0 is least significant, b3 is most significant (little-endian) */
    return ((uint32_t)b3 << 24)
         | ((uint32_t)b2 << 16)
         | ((uint32_t)b1 <<  8)
         |  (uint32_t)b0;
}
```

**Unpacking** extracts individual bytes from a word:

```c
void unpack_le(uint32_t word, uint8_t *b0, uint8_t *b1,
                              uint8_t *b2, uint8_t *b3) {
    *b0 = (uint8_t)( word        & 0xFF);
    *b1 = (uint8_t)((word >>  8) & 0xFF);
    *b2 = (uint8_t)((word >> 16) & 0xFF);
    *b3 = (uint8_t)((word >> 24) & 0xFF);
}
```

## Why the Cast to `uint32_t` Matters

In C, integer arithmetic is performed in `int`. If `b3` is `uint8_t` and you write `b3 << 24` without casting, the shift may overflow a 32-bit signed `int` when `b3 >= 0x80`, producing undefined behaviour. Always widen to `uint32_t` (or `uint64_t` for 64-bit packing) before shifting.

## Worked Example: Parsing a Network Header Field

A 4-byte array arrives over a network (big-endian byte order):

```
buf[0] = 0x08
buf[1] = 0x00
buf[2] = 0x45
buf[3] = 0x00
```

Reassemble as a big-endian 32-bit value:

```c
uint8_t buf[4] = { 0x08, 0x00, 0x45, 0x00 };

uint32_t value = ((uint32_t)buf[0] << 24)
               | ((uint32_t)buf[1] << 16)
               | ((uint32_t)buf[2] <<  8)
               |  (uint32_t)buf[3];
/* value == 0x08004500 */
```

## Using `memcpy` for Portable Packing

The cleanest portable approach avoids pointer aliasing entirely:

```c
#include <string.h>
#include <stdint.h>

uint32_t pack_from_bytes(const uint8_t *src) {
    uint32_t result;
    memcpy(&result, src, sizeof(result));
    /* result holds the bytes in NATIVE endian order */
    return result;
}
```

Use `memcpy` when the byte array was already written in the host's native byte order. Use the explicit shift-and-OR approach when you need to control endianness independently of the host.

## Python Equivalents

```python
import struct

# Pack four bytes into a little-endian 32-bit word
word = struct.pack('<I', 0xDEADBEEF)   # b'\xef\xbe\xad\xde'

# Unpack a big-endian 32-bit word from bytes
value, = struct.unpack('>I', b'\xDE\xAD\xBE\xEF')  # 0xDEADBEEF
```

`struct.pack` / `struct.unpack` is the preferred Pythonic approach and is exactly what you would use in a SystemC Python co-simulation harness or test generator.

## Your Task

In the exercise, you will read byte arrays from stdin, pack them into 32-bit words using both little-endian and big-endian conventions, and print the results. You will also unpack provided 32-bit words back into their constituent bytes.

The full specification is in the accompanying prompt file.

## Common Pitfalls

- Forgetting to mask with `0xFF` before shifting — if the source value is already wider than 8 bits, the upper bits contaminate the result.
- Mixing up which byte is `[0]`: in little-endian, `[0]` is the LSB; in big-endian, `[0]` is the MSB.
- Using `char` instead of `uint8_t` — `char` may be signed, causing sign extension when widening.

## Interview Answer

> "Packing combines bytes into a wider integer using shift-and-OR; unpacking extracts bytes using shift-and-mask. The byte order (endianness) determines which byte goes in which position. Always cast to the target unsigned type before shifting to avoid undefined behaviour from signed overflow."
