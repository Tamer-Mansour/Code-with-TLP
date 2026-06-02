# What Is Memory Alignment and Why It Exists

Memory alignment is one of those low-level concepts that separates engineers who write code from engineers who understand what the hardware is actually doing. It affects performance, correctness, and portability — and it shows up constantly in systems, OS, and embedded interviews.

## The Hardware Reality

Modern CPUs do not read memory one byte at a time. They read it in fixed-width chunks called **words** — typically 4 or 8 bytes on 32-bit and 64-bit architectures respectively. The memory bus is physically wired to transfer data aligned to these natural boundaries.

When a value sits at an address that is a multiple of its size, the CPU can retrieve it in a single memory operation. When it does not, one of two things happens:

- **Hardware trap / fault** — some architectures (SPARC, older ARM) raise an exception on misaligned access.
- **Silent double-fetch** — x86/x64 silently performs two memory reads and stitches the result together in hardware, at a throughput penalty.

## Alignment Defined

An object of type `T` with `sizeof(T) == N` is **aligned** when its address is an integer multiple of its **alignment requirement** — typically `N` itself for fundamental types, up to a platform maximum (usually 16 bytes for SIMD types).

```cpp
#include <cstdint>

// On a typical 64-bit platform:
// char  → size 1, align 1 → any address
// short → size 2, align 2 → address divisible by 2
// int   → size 4, align 4 → address divisible by 4
// long  → size 8, align 8 → address divisible by 8

int x;          // Compiler places x at an address % 4 == 0
double d;       // Compiler places d at an address % 8 == 0
```

## Why the Compiler Pads Structs

When you combine members of different sizes into a struct, the compiler inserts **padding bytes** so that each member satisfies its alignment requirement. The struct itself is then sized to a multiple of its largest member's alignment, ensuring that arrays of the struct work correctly.

```cpp
struct Bad {
    char  a;    // offset 0, size 1
    // 3 bytes padding inserted here
    int   b;    // offset 4, size 4
    char  c;    // offset 8, size 1
    // 3 bytes padding inserted here (tail padding)
};
// sizeof(Bad) == 12, not 6
```

## Alignment on the Stack and Heap

- **Stack**: The compiler adjusts `alloca` and local variable layout automatically. The ABI guarantees the stack pointer is aligned (commonly to 16 bytes) at function entry.
- **Heap**: `malloc` and `new` return memory aligned to `alignof(std::max_align_t)` — enough for any fundamental type. For types requiring stricter alignment (e.g., SIMD vectors), use `std::aligned_alloc` or `operator new` with an alignment argument (C++17).

```cpp
#include <cstdlib>
// Allocate 64 bytes aligned to a 32-byte boundary (for AVX)
void* buf = std::aligned_alloc(32, 64);
```

## Common Pitfalls

- **Casting pointers without checking alignment**: `reinterpret_cast<int*>(char_ptr)` is undefined behavior if `char_ptr` is not 4-byte aligned.
- **`#pragma pack` without knowing the cost**: Disabling padding speeds up serialization size but can cause misaligned accesses on architectures that do not tolerate them.
- **Assuming `sizeof` equals the sum of members**: Always account for padding.

## Quick Reference Table

| Type (64-bit Linux/Windows) | Size | Alignment |
|-----------------------------|------|-----------|
| `char`                      | 1    | 1         |
| `short`                     | 2    | 2         |
| `int`                       | 4    | 4         |
| `float`                     | 4    | 4         |
| `long` (Linux)              | 8    | 8         |
| `long` (Windows)            | 4    | 4         |
| `long long`                 | 8    | 8         |
| `double`                    | 8    | 8         |
| pointer                     | 8    | 8         |

> **Interview answer:** Alignment ensures each object's address is a multiple of its size so the CPU can fetch it in one memory transaction. The compiler satisfies this automatically by inserting padding bytes between struct members and at the end of the struct.
