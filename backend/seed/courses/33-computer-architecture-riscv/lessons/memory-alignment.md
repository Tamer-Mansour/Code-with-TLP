# Memory Alignment and Padding

Memory alignment is the requirement that a value of a given type be stored at an address that is a multiple of that type's size (or alignment requirement). Violating alignment can cause a bus fault on strict architectures or a silent performance penalty on permissive ones.

## Why Alignment Exists

CPUs read memory in fixed-width transactions aligned to natural boundaries. A 32-bit load unit typically fetches from addresses that are multiples of 4. If a `uint32_t` spans two such windows (e.g., it starts at address `0x03`), the CPU must either:

1. Issue two memory reads and reassemble the pieces (slow), or
2. Raise a hardware exception (fault on ARM, MIPS, SPARC in strict mode).

x86 tolerates misaligned accesses in hardware but with a measurable penalty. ARM in its default ABI mode and most embedded cores require alignment.

## Natural Alignment Rule

A type with size N bytes must start at an address divisible by N:

| Type          | Size  | Alignment requirement |
|---------------|-------|-----------------------|
| `uint8_t`     | 1     | 1 (any address)       |
| `uint16_t`    | 2     | 2                     |
| `uint32_t`    | 4     | 4                     |
| `uint64_t`    | 8     | 8                     |
| `float`       | 4     | 4                     |
| `double`      | 8     | 8                     |
| pointer (64-bit)| 8   | 8                     |

## Padding in Structures

The compiler inserts invisible **padding bytes** between struct fields to satisfy alignment. This is why `sizeof(struct)` can be larger than the sum of its field sizes.

```c
struct Misaligned {
    uint8_t  a;   // offset 0, size 1
                  // 3 bytes padding here
    uint32_t b;   // offset 4, size 4
    uint8_t  c;   // offset 8, size 1
                  // 3 bytes padding here (tail padding to align next element)
};
// sizeof(struct Misaligned) = 12, not 6
```

Memory layout:

```
Offset: 0    1    2    3    4    5    6    7    8    9   10   11
        [ a ][ pad ][ pad ][ pad ][ b b b b  ][ c ][ pad ][ pad ][ pad ]
```

## Checking Alignment at Runtime

```c
#include <stdint.h>
#include <stdbool.h>

bool is_aligned(const void *ptr, size_t alignment) {
    return ((uintptr_t)ptr % alignment) == 0;
}

// Check that a double pointer is 8-byte aligned
double x;
printf("aligned: %s\n", is_aligned(&x, 8) ? "yes" : "no");
```

## Querying Alignment with `alignof`

C11 and C++ provide `alignof` (or `_Alignof`) to query the alignment requirement of a type:

```c
#include <stdalign.h>
#include <stdio.h>

printf("alignof(char)   = %zu\n", alignof(char));    // 1
printf("alignof(int)    = %zu\n", alignof(int));     // 4
printf("alignof(double) = %zu\n", alignof(double));  // 8
```

## Specifying Alignment

You can request stricter alignment for SIMD operations or cache-line alignment:

```c
// C11
_Alignas(64) uint8_t cache_line_buf[64];

// GCC/Clang attribute
int __attribute__((aligned(16))) simd_array[4];

// MSVC
__declspec(align(16)) int simd_array[4];
```

## Tail Padding and the Struct Size Rule

The compiler also adds **tail padding** at the end of a struct so that an array of structs keeps each element properly aligned:

```c
struct Example {
    uint32_t x;   // offset 0
    uint8_t  y;   // offset 4
    // 3 bytes tail padding
};
// sizeof(struct Example) = 8, not 5
// An array Example arr[2] places arr[1].x at offset 8 — correctly aligned.
```

## Performance Implications

- Aligned accesses fit in one cache line in most cases; misaligned accesses can split across two cache lines, doubling the memory bus traffic.
- SIMD intrinsics (SSE, AVX, NEON) often have both aligned (`_mm_load_ps`) and unaligned (`_mm_loadu_ps`) variants; the aligned version is faster.
- Heap allocators typically return pointers aligned to at least `max_align_t` (usually 16 bytes).

> **Interview answer:** Memory alignment requires that an N-byte type is stored at an address divisible by N. The compiler inserts invisible padding bytes in structs to enforce this. Violations on strict architectures cause bus faults; on x86 they cause a performance penalty. Use `alignof` to query requirements and `__attribute__((aligned(N)))` to override them.
