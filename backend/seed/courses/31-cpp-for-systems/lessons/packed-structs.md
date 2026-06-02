# Packed Structs and the Cost of Misalignment

Sometimes you need a struct's binary layout to exactly match an external format — a network packet header, a filesystem on-disk structure, or a hardware register map. In those cases the compiler's padding is the enemy, and `#pragma pack` or `__attribute__((packed))` is the solution. But the cost can be severe.

## Requesting Packed Layout

### GCC / Clang

```cpp
struct __attribute__((packed)) PacketHeader {
    uint8_t  version;       // offset 0
    uint16_t length;        // offset 1  ← misaligned (not on 2-byte boundary)
    uint32_t sequence;      // offset 3  ← misaligned (not on 4-byte boundary)
    uint8_t  flags;         // offset 7
};
// sizeof(PacketHeader) == 8 — no padding, exactly matches wire format
```

### MSVC and Portable (`#pragma pack`)

```cpp
#pragma pack(push, 1)   // save current packing, set to 1 byte
struct PacketHeader {
    uint8_t  version;
    uint16_t length;
    uint32_t sequence;
    uint8_t  flags;
};
#pragma pack(pop)       // restore previous packing
```

`#pragma pack(N)` sets the maximum alignment of each member to `N`. With `N=1` every member is placed at the next consecutive byte — no gaps.

## What "Misaligned" Actually Costs

### x86 / x64

x86 handles misaligned accesses in hardware — but not for free:

- **Cache-line split**: if a 4-byte int straddles a 64-byte cache-line boundary, the CPU must fetch two cache lines, merge the bytes, and deliver them. This is roughly 2× the latency.
- **SIMD restrictions**: many SSE/AVX instructions (`movaps`, `vmovaps`) require 16/32-byte alignment and will **fault** if given a misaligned pointer — even on x86.
- **Atomic operations**: `std::atomic<T>` is only lock-free when `T` is naturally aligned. Misaligned atomics may silently fall back to a mutex.

### ARM / RISC-V / SPARC

Older or stricter architectures raise a **bus error / hardware exception** on any misaligned access. Even modern ARMv8 in strict mode will fault.

```c
// Dangerous on ARM strict mode or any RISC architecture:
void process(uint8_t* buf) {
    uint32_t val = *(uint32_t*)(buf + 1);  // UB + possible SIGBUS
}

// Safe — use memcpy to read unaligned bytes portably:
uint32_t val;
memcpy(&val, buf + 1, sizeof(val));
```

`memcpy` on modern compilers compiles to a single `movl` or `ldr` instruction when size is small and constant — zero overhead.

## Benchmark: The Real Cost on x86

A tight loop reading misaligned 4-byte integers from a hot cache can be 30–50 % slower than the aligned equivalent. The penalty spikes when accesses straddle cache-line (64-byte) or page (4096-byte) boundaries.

```
Aligned    4-byte reads:  ~1.0 ns/op
Misaligned 4-byte reads:  ~1.5 ns/op  (same cache line)
Cache-line split reads:   ~3.0 ns/op  (two cache-line fetches)
Page boundary split:      ~10+ ns/op  (TLB hit × 2)
```

## Safe Pattern: Packed Serialization, Aligned Computation

The best practice is to keep two representations:

```cpp
// Wire format (packed) — used only at the boundary
#pragma pack(push, 1)
struct WireHeader {
    uint8_t  version;
    uint16_t length;
    uint32_t sequence;
};
#pragma pack(pop)

// Working struct (natural alignment) — used in computation
struct Header {
    uint32_t sequence;  // largest first
    uint16_t length;
    uint8_t  version;
};

// Convert on receive:
Header from_wire(const WireHeader& w) {
    Header h;
    // memcpy to safely read potentially unaligned fields:
    memcpy(&h.length,   &w.length,   sizeof(h.length));
    memcpy(&h.sequence, &w.sequence, sizeof(h.sequence));
    h.version = w.version;
    return h;
}
```

## Pitfalls Summary

| Pitfall | Consequence |
|---|---|
| Taking the address of a packed member | Pointer is misaligned → UB if dereferenced |
| Passing packed member ref to function expecting `int&` | Binds a misaligned reference → UB |
| SIMD load from packed struct | Hardware fault on aligned-only instructions |
| Atomic on packed member | May not be lock-free; silent correctness bug |

```cpp
// DO NOT do this with packed structs:
void inc(int& x) { ++x; }
inc(pkt.sequence);  // UB — misaligned reference
```

> **Interview answer:** `#pragma pack(1)` or `__attribute__((packed))` removes padding so a struct matches an external binary format exactly. The cost is potential misaligned memory accesses, which cause bus errors on strict architectures and performance penalties (cache-line splits) on x86. Use `memcpy` to safely read fields from packed or unaligned memory.
