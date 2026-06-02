# Struct Padding and Alignment in Memory

When a C or C++ compiler lays out a struct in memory, it inserts invisible padding bytes between members to satisfy each member's alignment requirement. This padding can make a struct larger than the sum of its members' sizes — a common source of bugs in embedded systems, protocol parsers, and hardware register maps.

## Why Padding Exists

CPUs access data most efficiently when it is naturally aligned. A 4-byte integer loads fastest when its address is divisible by 4. A 2-byte short loads fastest when its address is divisible by 2. Compilers enforce these requirements by inserting padding bytes before a member whose address would otherwise be misaligned.

```c
#include <stdint.h>
#include <stdio.h>

struct Naive {
    uint8_t  a;   /* offset 0 */
    /* 3 bytes padding */
    uint32_t b;   /* offset 4 */
    uint8_t  c;   /* offset 8 */
    /* 3 bytes padding */
};
/* sizeof(struct Naive) == 12, not 6 */
```

## The Alignment Rule

A struct's own alignment is the alignment of its largest member. The compiler pads the struct at the end so that its size is a multiple of this alignment (enabling arrays of structs to stay aligned).

```c
struct Example {
    uint8_t  x;   /* 1-byte aligned, offset 0 */
    uint16_t y;   /* 2-byte aligned → 1 pad byte inserted → offset 2 */
    uint32_t z;   /* 4-byte aligned, offset 4 */
};
/* Total: 1 + 1(pad) + 2 + 4 = 8 bytes. sizeof == 8. */
```

## Minimising Padding: Largest-First Ordering

Ordering members from largest to smallest alignment eliminates most padding:

```c
struct Packed {
    uint32_t z;   /* offset 0 */
    uint16_t y;   /* offset 4 */
    uint8_t  x;   /* offset 6 */
    /* 1 byte tail padding to round size to 4 */
};
/* sizeof(struct Packed) == 8 — same here, but many cases save space */
```

For a struct with a `uint64_t`, a `uint8_t`, and a `uint32_t`, reordering from worst to best order reduces size from 24 bytes to 16 bytes.

## `__attribute__((packed))` — Use With Caution

GCC and Clang support a packed attribute that removes all padding:

```c
struct __attribute__((packed)) RegisterMap {
    uint8_t  status;   /* offset 0 */
    uint32_t data;     /* offset 1 — UNALIGNED on most architectures */
    uint16_t control;  /* offset 5 — UNALIGNED */
};
/* sizeof == 7 */
```

Packed structs are useful for **overlay on hardware register maps or network packet buffers** where the memory layout is fixed by the protocol. However, accessing unaligned fields through a struct pointer directly can cause:

- A hardware fault on strict-alignment architectures (older ARM Cortex-M).
- Unexpected byte-by-byte loads on ARMv7 with unaligned access support enabled.
- Subtle compiler bugs on some compilers when the packed field is passed by value.

**Prefer** `memcpy` into a local properly-aligned variable rather than a direct pointer dereference into packed memory.

## `offsetof` and `sizeof` — Your Diagnostic Tools

```c
#include <stddef.h>
#include <stdio.h>

struct S {
    uint8_t  a;
    uint32_t b;
    uint16_t c;
};

int main(void) {
    printf("sizeof(S)  = %zu\n", sizeof(struct S));          /* 12 */
    printf("offsetof a = %zu\n", offsetof(struct S, a));     /* 0  */
    printf("offsetof b = %zu\n", offsetof(struct S, b));     /* 4  */
    printf("offsetof c = %zu\n", offsetof(struct S, c));     /* 8  */
    return 0;
}
```

Always use `offsetof` when you need to know where a field starts — never compute offsets manually.

## Hardware Register Maps

Device register layouts are fixed by the silicon. If the datasheet says CTRL is at offset 4 and STATUS at offset 8, your struct must match exactly. Always:

1. Verify with `static_assert(offsetof(RegMap, STATUS) == 8, "layout mismatch");`
2. Use `volatile` for all memory-mapped fields.
3. Use `uint32_t` reservations (`uint32_t _reserved[N]`) to skip unused register ranges.

## Common Pitfalls

- Comparing sizeof a struct to the sum of its members' sizes — they will differ whenever padding is present.
- Using `memcmp` on structs that contain padding — the padding bytes are uninitialised and the comparison is unreliable.
- Relying on packed structs for register maps without validating offsets with `static_assert`.

## Interview Answer

> "The compiler inserts padding bytes to satisfy each member's alignment requirement. A struct's size is always a multiple of its largest member's alignment. Use `offsetof` to inspect actual offsets, order members largest-first to minimise waste, and use `__attribute__((packed))` only when you need a fixed binary layout — but access unaligned fields via `memcpy`, not direct pointer dereference."
