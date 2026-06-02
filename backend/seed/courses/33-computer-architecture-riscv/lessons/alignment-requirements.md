# Alignment Requirements and Misaligned Access

Memory alignment refers to the requirement that multi-byte values be stored at addresses that are multiples of their size. RISC-V's base ISA allows implementations to handle misalignment in different ways — making it a critical topic for portability and performance.

## The Alignment Rules

A naturally aligned access means the effective address is a multiple of the data size:

| Instruction | Width | Required alignment |
|---|---|---|
| `LB` / `SB` | 1 byte | Any address (always aligned) |
| `LH` / `SH` | 2 bytes | Address divisible by 2 |
| `LW` / `SW` | 4 bytes | Address divisible by 4 |
| `LD` / `SD` | 8 bytes | Address divisible by 8 |

Examples of aligned vs misaligned:

```
Address 0x1000: ALIGNED for LB, LH, LW, LD
Address 0x1001: ALIGNED for LB only
Address 0x1002: ALIGNED for LB, LH only
Address 0x1004: ALIGNED for LB, LH, LW only
```

## How RISC-V Handles Misaligned Accesses

Unlike ARM Cortex-M (which generates a hard fault on misalignment) or x86 (which always handles it in hardware), RISC-V gives implementations a **choice**:

1. **Hardware support**: The implementation handles misaligned accesses transparently. This is common in high-performance RISC-V cores (e.g., SiFive U-series). Performance may still degrade.

2. **Trap to software**: The implementation raises a misaligned-address exception. The OS or runtime emulates the access in software. This is common in embedded cores to save silicon area.

You cannot tell from source code which behavior your hardware uses — this is an implementation detail not visible in the ISA.

## Performance Cost of Misalignment

Even when supported in hardware, misaligned accesses are slower:

- A misaligned 4-byte load that spans a cache line boundary may require **two cache reads** and a merge.
- A misaligned 8-byte load across a DRAM page boundary may stall for an additional memory access.

```
Cache line boundary (64 bytes)
|--- 60 bytes ---|--- 4 bytes ---|
                  ^
         LW starting here is misaligned across the cache line boundary
         → requires reading two cache lines
```

## C-Level Alignment: Struct Padding

C compilers automatically insert **padding bytes** to ensure struct fields are naturally aligned:

```c
struct Example {
    char  a;      // offset 0, size 1
    // 1 byte padding
    short b;      // offset 2, size 2
    // 0 bytes padding
    int   c;      // offset 4, size 4
    char  d;      // offset 8, size 1
    // 3 bytes padding
    int   e;      // offset 12, size 4
};
// Total: 16 bytes (not 12)
```

You can verify with:

```c
#include <stddef.h>
printf("%zu\n", offsetof(struct Example, c));  // prints 4
```

## Packed Structs: The Danger Zone

Using `__attribute__((packed))` in GCC removes padding:

```c
struct __attribute__((packed)) Packed {
    char a;   // offset 0
    int  b;   // offset 1  ← MISALIGNED!
};
```

Reading `b` via a pointer dereference may:
- Work correctly on RISC-V with hardware misalignment support
- Trap on embedded RISC-V (e.g., QEMU virt platform)
- Trigger undefined behavior in C (even if the hardware handles it)

## Detecting Misalignment at Runtime

```c
// Check if a pointer is aligned to N bytes (N must be power of 2)
#define IS_ALIGNED(ptr, N) (((uintptr_t)(ptr) & ((N)-1)) == 0)

int* p = get_pointer();
if (!IS_ALIGNED(p, 4)) {
    // handle misaligned case
}
```

## Worked Example: Stack Misalignment

RISC-V ABI requires the stack pointer (`sp`) to be **16-byte aligned** at function calls. If you manually adjust `sp` by an odd amount:

```asm
addi  sp, sp, -12    # BAD: sp is now not 16-byte aligned
sd    ra, 0(sp)      # SD requires 8-byte alignment — may be fine
                     # but a nested call will break ABI rules
```

> **Interview answer:** RISC-V's base ISA requires natural alignment (address divisible by access width) but allows implementations to either handle misaligned accesses in hardware or trap to software. Misalignment always carries a performance cost and, in packed structs, can cause undefined behavior in C.
