# Fixed-Width Integer Types and Their Sizes

Before `<stdint.h>` was standardised in C99, developers wrote `unsigned long` and hoped it was 32 bits — a hope that failed on 64-bit platforms. Fixed-width integer types eliminate that ambiguity and are mandatory in embedded systems, hardware register maps, and TLM payload definitions.

## The Standard Fixed-Width Types

Defined in `<stdint.h>` (C) and `<cstdint>` (C++):

| Type | Width | Range (unsigned) | Typical use |
|---|---|---|---|
| `uint8_t` / `int8_t` | 8 bits | 0 – 255 | Byte buffers, register bytes |
| `uint16_t` / `int16_t` | 16 bits | 0 – 65 535 | Halfword registers, ADC samples |
| `uint32_t` / `int32_t` | 32 bits | 0 – 4 294 967 295 | Word registers, addresses on 32-bit targets |
| `uint64_t` / `int64_t` | 64 bits | 0 – 1.8×10¹⁹ | Timestamps, 64-bit addresses |

These types are guaranteed to be exactly N bits wide on every conforming platform.

## Minimum-Width and Fastest Types

`<stdint.h>` also provides:

- `uint_leastN_t` — smallest type with at least N bits (always available).
- `uint_fastN_t` — fastest type with at least N bits (may be wider, e.g., `uint_fast8_t` is often 32 bits on 32-bit processors for performance).

For hardware interfaces, use the exact-width types. Use the fast variants only in pure computation where exact width does not matter.

## Pointer-Sized Integer Types

| Type | Width | Use |
|---|---|---|
| `uintptr_t` | Platform pointer width | Safely cast a pointer to an integer |
| `intptr_t` | Platform pointer width (signed) | Signed pointer arithmetic |
| `ptrdiff_t` | Platform pointer difference | Result of subtracting two pointers |
| `size_t` | Platform address width (unsigned) | `sizeof`, `malloc`, array index |

Always use `uintptr_t` when you need to store a pointer value in an integer — never `uint32_t`, which silently truncates on 64-bit systems.

## Platform-Dependent Types to Avoid in Hardware Code

| Type | Problem |
|---|---|
| `int` | 16 bits on some embedded compilers, 32 or 64 on desktops |
| `long` | 32 bits on Windows 64-bit, 64 bits on Linux 64-bit (LP64 model) |
| `unsigned long long` | Always 64 bits in C99, but verbose — use `uint64_t` instead |

## Worked Example: Defining a Register Map

```c
#include <stdint.h>
#include <stddef.h>

typedef struct {
    volatile uint32_t CTRL;      /* offset 0x00 */
    volatile uint32_t STATUS;    /* offset 0x04 */
    volatile uint8_t  DATA[16];  /* offset 0x08, byte-accessible FIFO */
    volatile uint32_t _reserved; /* offset 0x18 */
    volatile uint16_t IRQ_MASK;  /* offset 0x1C */
    volatile uint16_t IRQ_STAT;  /* offset 0x1E */
} MyPeriphRegs;

/* Verify layout at compile time */
_Static_assert(offsetof(MyPeriphRegs, IRQ_MASK) == 0x1C,
               "IRQ_MASK offset mismatch");
```

Every field uses a fixed-width type so the layout is identical on a 32-bit embedded target and on a 64-bit host running a SystemC virtual platform.

## Format Specifiers

When printing fixed-width integers use the macros from `<inttypes.h>`:

```c
#include <inttypes.h>

uint32_t reg = 0xDEADBEEF;
printf("reg = 0x%" PRIx32 "\n", reg);   /* correct on any platform */
printf("reg = 0x%x\n", reg);            /* may warn on some platforms */
```

## Bit-Field Widths

You can declare struct bit-fields alongside fixed-width types:

```c
typedef struct {
    uint32_t enable   : 1;
    uint32_t mode     : 3;
    uint32_t reserved : 28;
} CtrlReg;
```

But remember: the layout of bit-fields is implementation-defined. For portable hardware register access, prefer masks and shifts over bit-fields.

## Common Pitfalls

- Using `int` or `long` in hardware-facing code — their sizes are platform-dependent.
- Assuming `sizeof(pointer) == 4` — this is false on 64-bit hosts running 32-bit TLM models.
- Printing a `uint64_t` with `%lu` instead of `PRIu64` — silently wrong on Windows.

## Interview Answer

> "Fixed-width integer types like `uint32_t` from `<stdint.h>` guarantee exact bit widths on every platform, which is essential for memory-mapped register maps and TLM payloads. Never use `int` or `long` in hardware-facing code because their widths are platform-dependent. Use `uintptr_t` for pointer-to-integer conversions."
