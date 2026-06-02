# Struct Packing and Layout

Struct packing is the practice of removing compiler-inserted padding bytes to minimize the memory footprint of a structure. It trades the performance and portability advantages of natural alignment for compact, byte-exact layout — which is essential when a struct must map directly onto a network packet, binary file header, or hardware register block.

## Default Layout vs Packed Layout

```c
// Default layout — compiler adds padding for alignment
struct Default {
    uint8_t  a;   // 1 byte  (offset 0)
                  // 3 bytes padding
    uint32_t b;   // 4 bytes (offset 4)
    uint16_t c;   // 2 bytes (offset 8)
                  // 2 bytes tail padding
};
// sizeof = 12

// Packed layout — no padding
#pragma pack(1)
struct Packed {
    uint8_t  a;   // 1 byte  (offset 0)
    uint32_t b;   // 4 bytes (offset 1) ← misaligned!
    uint16_t c;   // 2 bytes (offset 5)
};
#pragma pack()
// sizeof = 7
```

On x86 the packed struct works correctly but `b` at offset 1 incurs a misaligned read penalty. On ARM without hardware unaligned support it may fault.

## GCC/Clang Attribute Syntax

```c
struct __attribute__((packed)) PackedGCC {
    uint8_t  type;
    uint32_t length;
    uint16_t checksum;
};
// sizeof = 7, no padding anywhere
```

The `packed` attribute is per-struct and is preferred over `#pragma pack` in GCC/Clang because it has tighter scope.

## MSVC `#pragma pack`

```c
#pragma pack(push, 1)   // save current packing, set to 1-byte alignment
struct NetworkHeader {
    uint8_t  version;
    uint16_t total_length;
    uint32_t src_ip;
    uint32_t dst_ip;
};
#pragma pack(pop)       // restore previous packing
// sizeof = 11
```

Always use `push`/`pop` to avoid inadvertently changing packing for subsequent code.

## Optimal Field Ordering (Avoiding Waste)

Instead of packing, you can often eliminate padding entirely by reordering fields from largest to smallest:

```c
// BAD ordering — 6 bytes padding
struct BadOrder {
    uint8_t  a;    // 1 byte  (offset 0) + 7 bytes padding
    uint64_t b;    // 8 bytes (offset 8)
    uint8_t  c;    // 1 byte  (offset 16) + 7 bytes padding
};
// sizeof = 24

// GOOD ordering — 0 bytes padding
struct GoodOrder {
    uint64_t b;    // 8 bytes (offset 0)
    uint8_t  a;    // 1 byte  (offset 8)
    uint8_t  c;    // 1 byte  (offset 9)
                   // 6 bytes tail padding (struct size must be multiple of 8)
};
// sizeof = 16
```

Reordering saves 8 bytes per instance. For arrays of millions of structs this matters significantly.

## Use Case: Parsing a Binary Protocol

```c
// IPv4 header — must match the wire format exactly
#pragma pack(push, 1)
struct IPv4Header {
    uint8_t  ihl_version;   // 4 bits each, combined
    uint8_t  dscp_ecn;
    uint16_t total_length;
    uint16_t identification;
    uint16_t flags_fragment;
    uint8_t  ttl;
    uint8_t  protocol;
    uint16_t checksum;
    uint32_t src_addr;
    uint32_t dst_addr;
};
#pragma pack(pop)
// sizeof = 20 — matches the minimum IP header size exactly

void parse_packet(const uint8_t *raw) {
    const struct IPv4Header *hdr = (const struct IPv4Header *)raw;
    // Still need to convert multi-byte fields from network byte order!
    uint16_t len = ntohs(hdr->total_length);
}
```

Note: even with perfect packing, fields wider than one byte must still be converted from network byte order.

## Python `ctypes.Structure`

Python exposes the same control through `ctypes`:

```python
import ctypes

class Packed(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("a", ctypes.c_uint8),
        ("b", ctypes.c_uint32),
        ("c", ctypes.c_uint16),
    ]

print(ctypes.sizeof(Packed))  # 7 — no padding
```

Without `_pack_ = 1`, `sizeof` would be 8 (padding after `a`).

## Key Rules

1. **Pack only when necessary** — for protocol headers, file format structs, or memory-mapped registers.
2. **Prefer reordering fields** over packing when you control the layout; it preserves alignment without sacrificing portability.
3. **Byte-swap fields** after reading a packed network/file struct — packing solves layout, not endianness.
4. **Document the layout** with an explicit comment showing expected offsets and total size.

> **Interview answer:** Struct packing removes compiler-inserted padding to make a struct's memory layout byte-exact. Use `__attribute__((packed))` in GCC/Clang or `#pragma pack(1)` in MSVC. It is essential for binary protocol parsing but causes misaligned accesses that hurt performance or fault on strict architectures. The portable alternative is to reorder fields largest-first.
