# alignof, alignas, and Over-Alignment

C++11 added two keywords — `alignof` and `alignas` — that let you query and control alignment directly in portable, standard C++. Before these, developers relied on compiler extensions (`__alignof__`, `__attribute__((aligned(N)))`). Today the standard keywords are preferred.

## `alignof` — Query Alignment Requirements

`alignof(T)` returns the alignment requirement of type `T` as a `std::size_t`. It is a compile-time constant expression.

```cpp
#include <cstddef>
#include <cstdio>

printf("char   align = %zu\n", alignof(char));    // 1
printf("int    align = %zu\n", alignof(int));     // 4
printf("double align = %zu\n", alignof(double));  // 8

struct S { char a; double b; };
printf("S      align = %zu\n", alignof(S));       // 8 (largest member)
printf("S      size  = %zu\n", sizeof(S));        // 16
```

`alignof` applied to an array type gives the alignment of the element type, not the whole array. `alignof` applied to a reference type gives the alignment of the referenced type.

### `std::alignment_of<T>` (type trait)

```cpp
#include <type_traits>
static_assert(std::alignment_of<double>::value == 8);
// C++17 helper variable:
static_assert(std::alignment_of_v<double> == 8);
```

Both are equivalent to `alignof(T)`; the trait is useful in template metaprogramming contexts.

## `alignas` — Specify Alignment Requirements

`alignas(N)` increases the alignment of a variable or type. `N` must be a power of two and must not be less than the type's natural alignment.

```cpp
// Force a local buffer to be 64-byte aligned (cache-line aligned)
alignas(64) char buf[256];

// Over-align a struct for SIMD (AVX requires 32-byte alignment)
struct alignas(32) Vec8f {
    float data[8];
};

static_assert(alignof(Vec8f) == 32);
static_assert(sizeof(Vec8f)  == 32);
```

`alignas` can appear on:
- A **variable** declaration (including `static` and `thread_local`)
- A **type** definition (`struct`, `class`, `union`)
- A **data member** declaration

## Over-Alignment

**Over-alignment** means requesting an alignment stricter than `alignof(std::max_align_t)` (typically 8 or 16). The standard guarantees `new`/`delete` handle over-aligned types correctly since C++17.

```cpp
// C++17: operator new with alignment
struct alignas(64) CacheLine {
    char data[64];
};

// new correctly forwards the alignment:
CacheLine* p = new CacheLine;   // allocated at a 64-byte boundary
delete p;
```

Before C++17 you needed `_aligned_malloc` (MSVC) or `posix_memalign` / `aligned_alloc` (POSIX) plus a custom deleter.

```cpp
// C11 / POSIX heap allocation with alignment
void* raw = std::aligned_alloc(64, sizeof(CacheLine));
auto* cl  = new(raw) CacheLine{};   // placement new
cl->~CacheLine();
std::free(raw);
```

## Practical Use Cases

| Scenario | Alignment Needed | Why |
|---|---|---|
| SSE (128-bit SIMD) | 16 bytes | `movaps` instruction requirement |
| AVX (256-bit SIMD) | 32 bytes | `vmovaps` instruction requirement |
| AVX-512 | 64 bytes | `zmm` register width |
| Cache-line padding | 64 bytes | Prevent false sharing |
| DMA buffers | Page size (4096) | Hardware DMA controller constraint |

## Common Mistakes

```cpp
// ERROR: alignas cannot reduce natural alignment
struct alignas(1) Broken {
    double x;   // natural align is 8 — compiler ignores alignas(1) or warns
};

// ERROR: alignas value must be a power of 2
alignas(6) int bad;   // ill-formed
```

Specifying multiple `alignas` on the same declaration is legal; the strictest one wins.

```cpp
alignas(16) alignas(32) float v[8];   // alignment = 32
```

## Checking at Compile Time

```cpp
static_assert(alignof(Vec8f) == 32, "Vec8f must be 32-byte aligned for AVX");
```

Always add `static_assert` to over-aligned types in production code so a refactor cannot silently break the requirement.

> **Interview answer:** `alignof(T)` queries the alignment requirement of a type at compile time; `alignas(N)` imposes a stricter alignment on a variable or type. Over-alignment beyond `max_align_t` is supported in C++17 by `new`/`delete` automatically routing through the aligned allocation path.
