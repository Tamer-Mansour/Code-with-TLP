# Fundamental Types and Their Sizes (sizeof, fixed-width ints)

Understanding type sizes is non-negotiable in systems programming. A `char` on one platform may be signed or unsigned. An `int` might be 16, 32, or 64 bits depending on the ABI. Getting this wrong corrupts data, breaks protocols, and creates subtle security vulnerabilities.

## The Built-in Type Zoo

C++ inherits C's primitive types and adds a few of its own. The standard guarantees *minimum* sizes, not exact ones.

| Type | Minimum bits | Typical (LP64 Linux/macOS) | Typical (LLP64 Windows) |
|------|-------------|---------------------------|------------------------|
| `char` | 8 | 8 | 8 |
| `short` | 16 | 16 | 16 |
| `int` | 16 | 32 | 32 |
| `long` | 32 | **64** | **32** |
| `long long` | 64 | 64 | 64 |
| `float` | — | 32 (IEEE 754) | 32 |
| `double` | — | 64 (IEEE 754) | 64 |
| `void*` | — | 64 | 64 |

The `long` discrepancy between Linux and Windows is the #1 portability trap in cross-platform C++ code.

## Using sizeof at Compile Time

`sizeof` returns the size in **bytes** as a `std::size_t` (an unsigned type). It is evaluated at compile time and never generates a function call.

```cpp
#include <cstdio>

int main() {
    printf("char:      %zu bytes\n", sizeof(char));       // always 1
    printf("short:     %zu bytes\n", sizeof(short));      // >= 2
    printf("int:       %zu bytes\n", sizeof(int));        // >= 2, usually 4
    printf("long:      %zu bytes\n", sizeof(long));       // 4 on Win, 8 on Linux
    printf("long long: %zu bytes\n", sizeof(long long));  // always >= 8
    printf("double:    %zu bytes\n", sizeof(double));     // usually 8
    printf("void*:     %zu bytes\n", sizeof(void*));      // pointer width
}
```

`sizeof` works on expressions too — it evaluates the *type*, not the value, so side effects never occur:

```cpp
int arr[10];
printf("%zu elements\n", sizeof(arr) / sizeof(arr[0]));  // 10
```

## Fixed-Width Integer Types (`<cstdint>`)

When you need exact widths — network packets, file formats, hardware registers — use the fixed-width types from `<cstdint>`:

```cpp
#include <cstdint>

int8_t   a = -100;       // exactly 8-bit signed
uint8_t  b = 255;        // exactly 8-bit unsigned
int16_t  c = 0x1234;     // exactly 16-bit signed
uint32_t d = 0xDEADBEEF; // exactly 32-bit unsigned
int64_t  e = -1LL;       // exactly 64-bit signed
uint64_t f = UINT64_MAX; // exactly 64-bit unsigned
```

The standard also provides `_least` and `_fast` variants:

- `int_least32_t` — smallest type with at least 32 bits (always available)
- `int_fast32_t` — fastest type with at least 32 bits (may be 64-bit)

### Printing Fixed-Width Types

Use the `PRId32`, `PRIu64`, etc. macros from `<cinttypes>` to get the correct format specifier on every platform:

```cpp
#include <cinttypes>
#include <cstdio>

uint64_t reg = 0xFFFFFFFFFFFFFFFFULL;
printf("Register: 0x%" PRIx64 "\n", reg);  // safe on every platform
```

## Alignment and Padding

Types have alignment requirements that affect struct layout:

```cpp
struct Bad {
    char  a;    // 1 byte, then 3 bytes padding
    int   b;    // 4 bytes (needs 4-byte alignment)
    char  c;    // 1 byte, then 7 bytes padding on 64-bit
    long long d;// 8 bytes
}; // sizeof(Bad) = 24 on typical 64-bit

struct Good {
    long long d;// 8 bytes
    int   b;    // 4 bytes
    char  a;    // 1 byte
    char  c;    // 1 byte
    // 2 bytes padding
}; // sizeof(Good) = 16
```

Use `static_assert` to catch surprises at compile time:

```cpp
static_assert(sizeof(uint32_t) == 4, "uint32_t must be exactly 4 bytes");
static_assert(alignof(double) == 8, "double must be 8-byte aligned");
```

## Common Pitfalls

- Using `int` for array indices in 64-bit code — it silently truncates on arrays larger than 2 GB. Prefer `std::size_t` or `ptrdiff_t`.
- Comparing `sizeof` result (unsigned) with a signed integer — the signed value is converted to unsigned, turning `-1` into a huge number.
- Assuming `long` is 64-bit on Windows — it is only 32-bit (LLP64 model).

**Interview answer:** "Built-in type sizes are only guaranteed as minimums by the C++ standard. For exact widths use `<cstdint>` types like `uint32_t`. Use `sizeof` to inspect sizes at compile time and `static_assert` to enforce them."
