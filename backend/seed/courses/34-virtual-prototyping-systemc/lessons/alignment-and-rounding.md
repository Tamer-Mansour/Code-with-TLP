# Alignment, Rounding Up, and Masks

Memory alignment is a recurring constraint in hardware and systems programming. DMA buffers, cache lines, stack pointers, and TLM transaction addresses all have alignment requirements. Getting alignment wrong causes bus errors, performance penalties, or outright data corruption.

## What Is Alignment?

An N-byte aligned address is one whose value is a multiple of N. N is always a power of 2 in hardware contexts.

| Alignment | Requirement | Example valid addresses |
|-----------|-------------|------------------------|
| 1-byte | Any address | 0, 1, 2, 3, ... |
| 4-byte (word) | Multiple of 4 | 0, 4, 8, 12, ... |
| 16-byte (cache line) | Multiple of 16 | 0, 16, 32, ... |
| 4096-byte (page) | Multiple of 4096 | 0, 4096, 8192, ... |

## Checking Alignment with a Mask

A power-of-2 alignment N has the property that all multiples of N have their low `log2(N)` bits equal to zero. The alignment check becomes:

```cpp
bool is_aligned(uintptr_t addr, size_t align) {
    // align must be a power of 2
    return (addr & (align - 1)) == 0;
}

// Examples
is_aligned(0x1000, 4096)  // true  — 0x1000 & 0xFFF == 0
is_aligned(0x1001, 4096)  // false — 0x1001 & 0xFFF == 1
```

`align - 1` produces a mask with 1s in the low bits. If any of those bits are set in the address, it is not aligned.

## Rounding Down to an Alignment Boundary

Clear the low bits by ANDing with the inverted mask:

```cpp
uintptr_t align_down(uintptr_t addr, size_t align) {
    return addr & ~(align - 1);
}

align_down(0x1003, 4096)  // 0x1000
align_down(0x2FFE, 16)    // 0x2FF0
```

This is how the kernel computes the base of the page containing a faulting address.

## Rounding Up to an Alignment Boundary

Add `align - 1` first (to push past the current boundary if the address is not aligned), then round down:

```cpp
uintptr_t align_up(uintptr_t addr, size_t align) {
    return (addr + align - 1) & ~(align - 1);
}

align_up(0x1001, 4096)  // 0x2000  (already not aligned, rounds up)
align_up(0x1000, 4096)  // 0x1000  (already aligned, unchanged)
align_up(5, 4)          // 8
align_up(8, 4)          // 8
```

> **Pitfall:** `align_up` can overflow if `addr` is near the maximum of `uintptr_t`. Production code adds an overflow check or uses saturating arithmetic.

## Why `align - 1` Works

For N = 2^k:
- N in binary: `1 followed by k zeros`
- N - 1 in binary: `k ones`

The mask `N - 1` selects the low k bits (the "offset within the block"). Its complement `~(N-1)` selects the high bits (the "block number").

```
N = 16 = 0b0001'0000
N - 1  = 0b0000'1111  ← low 4 bits: offset within 16-byte block
~(N-1) = 0b1111'0000  ← high bits: block base address
```

## Computing Buffer Size After Alignment

When allocating a DMA buffer that must start at a 4096-byte boundary but the allocator may return any address:

```cpp
uint8_t raw[BUFFER_SIZE + 4096];           // over-allocate
uint8_t* buf = (uint8_t*)align_up((uintptr_t)raw, 4096);
```

## TLM / SystemC Context

In a TLM model, initiator sockets must send transactions at the granularity the target supports. Sending a non-aligned transaction to a 32-bit-aligned slave is an error. The standard pattern in TLM-2.0 is to check `(trans.get_address() & 0x3) == 0` for 4-byte alignment before processing.

```cpp
// Inside a TLM-2.0 b_transport
if (trans.get_address() & 3u) {
    trans.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);
    return;
}
```

## Key Takeaways

- Alignment N is always a power of 2; the low `log2(N)` bits must be zero.
- `addr & (N-1)` extracts the misalignment offset.
- `align_down = addr & ~(N-1)`, `align_up = (addr + N - 1) & ~(N-1)`.
- Over-allocate by N-1 bytes when you need a guaranteed-aligned pointer from an unaligned allocator.

**Interview answer:** "I check alignment with `(addr & (align-1)) == 0` and round up with `(addr + align - 1) & ~(align - 1)` — both exploit the fact that align is a power of 2 so the mask is simply `align - 1`."
