# Serializing Structs to a Portable Wire Format

Sending a raw C++ struct over a network or saving it to disk is tempting but almost always wrong. Padding, alignment, and endianness make the in-memory layout compiler- and platform-specific. A proper wire format explicitly controls every byte.

## Why You Cannot Use `memcpy` on a Struct Directly

```cpp
struct Header {
    uint8_t  version;    // 1 byte
    // 3 bytes of padding inserted by compiler for alignment!
    uint32_t length;     // 4 bytes
    uint16_t checksum;   // 2 bytes
    // 2 bytes of trailing padding for struct alignment
};
// sizeof(Header) is likely 12, not 8
```

The compiler inserts padding to satisfy alignment requirements. The exact padding depends on the target ABI, compiler flags, and sometimes the surrounding context. A struct written by one program may be read incorrectly by another even on the same machine.

## `#pragma pack` — Use With Care

You can suppress padding with `#pragma pack(1)`:

```cpp
#pragma pack(push, 1)
struct Header {
    uint8_t  version;
    uint32_t length;
    uint16_t checksum;
};  // sizeof == 7, no padding
#pragma pack(pop)
```

This is a non-standard extension that all major compilers support. However:
- Unaligned access to `length` triggers a bus error on strict-alignment architectures (ARM v5 and older).
- It bypasses compiler alignment optimisations.
- The endianness of `length` and `checksum` is still host-endian — not portable across machines.

## The Right Approach: Explicit Serialization

Write each field one byte at a time in a known byte order (almost always big-endian / network byte order for protocols):

```cpp
#include <cstdint>
#include <cstring>
#include <vector>

struct Header {
    uint8_t  version;
    uint32_t length;
    uint16_t checksum;
};

// Serialize to a byte buffer (big-endian wire format)
std::vector<uint8_t> serialize(const Header& h) {
    std::vector<uint8_t> buf(7);
    buf[0] = h.version;
    buf[1] = (h.length >> 24) & 0xFF;
    buf[2] = (h.length >> 16) & 0xFF;
    buf[3] = (h.length >>  8) & 0xFF;
    buf[4] = (h.length      ) & 0xFF;
    buf[5] = (h.checksum >> 8) & 0xFF;
    buf[6] = (h.checksum     ) & 0xFF;
    return buf;
}

// Deserialize from a byte buffer
Header deserialize(const uint8_t* buf) {
    Header h;
    h.version  = buf[0];
    h.length   = ((uint32_t)buf[1] << 24) |
                 ((uint32_t)buf[2] << 16) |
                 ((uint32_t)buf[3] <<  8) |
                 ((uint32_t)buf[4]);
    h.checksum = ((uint16_t)buf[5] << 8) |
                 ((uint16_t)buf[6]);
    return h;
}
```

This is completely portable. It does not matter what the host byte order is, what compiler built the program, or what alignment rules apply.

## Wire Format Design Checklist

| Decision | Recommendation |
|----------|----------------|
| Byte order | Big-endian (network) for protocols; little-endian for file formats like RIFF/PE |
| Integer sizes | Use fixed-width types (`uint32_t`, not `int`) |
| Floating point | Specify IEEE 754; consider serializing as integer (scaled) |
| Strings | Length-prefixed, not null-terminated, to handle embedded nulls |
| Versioning | Include a version field early in the header |
| Alignment in buffer | Not required; serialise field-by-field |

## Using `__attribute__((packed))` / `#pragma pack`

On GCC/Clang you can also use `__attribute__((packed))` on a struct. The same warnings about unaligned access apply. Never dereference a packed struct member through a pointer on a strict-alignment target; use `memcpy` to pull the bytes into an aligned local variable first.

```cpp
struct [[gnu::packed]] WireHeader {
    uint8_t  version;
    uint32_t length;     // may be unaligned in memory
    uint16_t checksum;
};

// Safe read on strict-alignment targets:
WireHeader* ptr = reinterpret_cast<WireHeader*>(buf);
uint32_t length;
std::memcpy(&length, &ptr->length, 4);  // copies bytes, avoids unaligned deref
length = ntohl(length);                 // then fix endianness
```

## Worked Example: A Minimal Binary Protocol Frame

```
Byte 0:   magic (0xAB)
Byte 1:   version (uint8)
Bytes 2-5: payload_length (uint32, big-endian)
Bytes 6+: payload (raw bytes)
```

```cpp
bool write_frame(uint8_t* out, const uint8_t* payload, uint32_t len) {
    out[0] = 0xAB;          // magic
    out[1] = 1;             // version
    out[2] = (len >> 24) & 0xFF;
    out[3] = (len >> 16) & 0xFF;
    out[4] = (len >>  8) & 0xFF;
    out[5] = (len      ) & 0xFF;
    std::memcpy(out + 6, payload, len);
    return true;
}
```

> **Interview answer:** Never send raw struct bytes across systems — padding and endianness make the layout non-portable. Instead, serialise each field explicitly into a byte buffer using a fixed byte order (usually big-endian), with fixed-width integer types, then deserialise symmetrically on the other side.
