# Struct Padding and Member Reordering

Padding is invisible bytes the compiler inserts between — and after — struct members so that every field lands on its required alignment boundary. Understanding it is essential for writing compact, cache-friendly data structures and for passing structs across process or network boundaries.

## How the Compiler Lays Out a Struct

The compiler walks members in declaration order and applies a simple rule for each member:

1. Advance the current offset to the next multiple of `alignof(member)`.
2. Place the member there.
3. Add the member's size to the current offset.

After all members, round the total size up to the next multiple of the struct's own alignment (which equals the largest member's alignment).

```cpp
struct Example {
    char  a;    // offset 0, size 1
                // +3 padding → offset becomes 4
    int   b;    // offset 4, size 4  → offset becomes 8
    char  c;    // offset 8, size 1
                // +7 padding → offset becomes 16
    double d;   // offset 16, size 8 → offset becomes 24
};
// Alignment of Example = alignof(double) = 8
// sizeof(Example) = 24
```

You can verify with `offsetof`:

```cpp
#include <cstddef>
#include <cstdio>

printf("a=%zu b=%zu c=%zu d=%zu size=%zu\n",
       offsetof(Example, a),   // 0
       offsetof(Example, b),   // 4
       offsetof(Example, c),   // 8
       offsetof(Example, d),   // 16
       sizeof(Example));       // 24
```

## Tail Padding

Tail padding is added at the end of a struct to make its size a multiple of its alignment. It is critical for arrays: if `sizeof(T)` were not a multiple of `alignof(T)`, the second element of `T arr[2]` would be misaligned.

```cpp
struct Tail {
    int  x;   // offset 0, size 4
    char y;   // offset 4, size 1
              // +3 tail padding
};
// sizeof(Tail) = 8 — NOT 5
```

## Reordering Members to Eliminate Waste

The most impactful zero-cost optimization: **sort members from largest to smallest**. This eliminates most internal padding because each smaller type naturally fits in the "gap" left by a larger predecessor.

```cpp
// Wasteful: 24 bytes
struct Wasteful {
    char   a;   // 1 + 3 pad
    int    b;   // 4
    char   c;   // 1 + 7 pad
    double d;   // 8
};

// Optimal: 16 bytes — same four fields, different order
struct Optimal {
    double d;   // 8
    int    b;   // 4
    char   a;   // 1
    char   c;   // 1
                // +2 tail padding
};
```

Saving 8 bytes per instance sounds small, but in a container of one million objects it is 8 MB — the difference between fitting in L3 cache and missing it on every access.

## Nested Struct Alignment

A nested struct contributes its own alignment requirement to the outer struct. The outer struct's alignment is the maximum of all member alignments, including nested ones.

```cpp
struct Inner {
    char a;
    int  b;
};
// sizeof(Inner) = 8, alignof(Inner) = 4

struct Outer {
    char  x;
    Inner inner;   // must be at offset divisible by 4 → +3 pad before it
    char  y;
};
// sizeof(Outer) = 1 + 3pad + 8 + 1 + 3pad = 16
```

## Tools for Inspection

```bash
# GCC/Clang: dump struct layout
g++ -fdump-lang-class -c file.cpp

# Clang-specific: very readable output
clang++ -Xclang -fdump-record-layouts -c file.cpp
```

Many IDEs and online tools (e.g., `godbolt.org`) also display struct layouts.

## Common Pitfalls

- **Serializing a raw struct** with `fwrite(&s, sizeof(s), 1, f)`: padding bytes have indeterminate values and will pollute the output. Zero-initialize or pack the struct first.
- **Comparing structs with `memcmp`**: padding bytes may differ even when all named fields are equal.
- **Cross-platform ABIs**: field sizes and alignment rules differ between 32/64-bit and between compilers. Never rely on a specific layout when communicating across compilation boundaries without an explicit ABI contract.

> **Interview answer:** The compiler inserts padding between struct members to satisfy each member's alignment requirement, and adds tail padding so the struct size is a multiple of its largest member's alignment. Reordering fields from largest to smallest typically eliminates most padding.
