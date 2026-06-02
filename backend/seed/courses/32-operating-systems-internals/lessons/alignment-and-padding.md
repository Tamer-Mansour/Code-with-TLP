# Memory Alignment and Struct Padding

Modern CPUs load and store data most efficiently when values are stored at addresses that are multiples of their size — this is called **natural alignment**. When you mix types of different sizes in a struct, the compiler inserts invisible **padding bytes** to satisfy alignment requirements. Ignoring this leads to surprises: structs larger than you expect, wasted memory, and potential performance hits.

## What Is Alignment?

A data type's **alignment requirement** is the address boundary it must start on:

| Type | Typical size | Typical alignment |
|---|---|---|
| `char` | 1 byte | 1 byte |
| `short` | 2 bytes | 2 bytes |
| `int` | 4 bytes | 4 bytes |
| `float` | 4 bytes | 4 bytes |
| `double` | 8 bytes | 8 bytes |
| `pointer` | 8 bytes (64-bit) | 8 bytes |

A misaligned load (e.g., reading a 4-byte `int` from an odd address) causes either a hardware fault (ARM, SPARC) or a silent performance penalty (x86 fetches extra cache lines). The compiler prevents misalignment by inserting padding.

## Padding Inside Structs

The compiler adds padding **after each member** to ensure the next member starts at its required alignment boundary.

```c
struct Bad {
    char  a;   // offset 0, size 1
    // 3 bytes padding here (to align 'b' to offset 4)
    int   b;   // offset 4, size 4
    char  c;   // offset 8, size 1
    // 3 bytes padding here (to align struct size to 4)
};
// sizeof(struct Bad) == 12
```

```c
struct Good {
    int   b;   // offset 0, size 4
    char  a;   // offset 4, size 1
    char  c;   // offset 5, size 1
    // 2 bytes padding (to align struct to 4)
};
// sizeof(struct Good) == 8
```

By reordering members from **largest to smallest**, you minimize padding and reduce the struct size.

## Trailing Padding

The compiler also adds **trailing padding** at the end of a struct so that an array of that struct keeps every element correctly aligned:

```c
struct Example {
    int  x;    // offset 0
    char y;    // offset 4
               // 3 bytes trailing padding
};
// sizeof(struct Example) == 8, not 5!

struct Example arr[3];
// arr[1] starts at offset 8 (correctly aligned)
```

## Verifying with offsetof and sizeof

```c
#include <stddef.h>
#include <stdio.h>

struct S {
    char  a;
    int   b;
    short c;
};

int main(void) {
    printf("sizeof(S)       = %zu\n", sizeof(struct S));
    printf("offsetof(S, a)  = %zu\n", offsetof(struct S, a));
    printf("offsetof(S, b)  = %zu\n", offsetof(struct S, b));
    printf("offsetof(S, c)  = %zu\n", offsetof(struct S, c));
}
/* Output (typical x86-64):
   sizeof(S)       = 12
   offsetof(S, a)  = 0
   offsetof(S, b)  = 4
   offsetof(S, c)  = 8
*/
```

## Disabling Padding with __attribute__((packed))

You can force the compiler to pack members without padding:

```c
struct Packed {
    char  a;
    int   b;
    char  c;
} __attribute__((packed));
// sizeof(struct Packed) == 6 (no padding)
```

Packed structs save memory and are useful for network protocol headers, but unaligned accesses may be slower or fault on non-x86 architectures. Use them only when you fully understand the implications.

## Alignment in C11 and C++11

```c
// Specify explicit alignment
struct alignas(16) Vector4 {
    float x, y, z, w;   // 16 bytes total, 16-byte aligned (SIMD-friendly)
};

// Query alignment
_Alignof(double)   // C11: returns 8 on most platforms
alignof(double)    // C++11 equivalent
```

## Key Rules to Remember

- Members are placed in declaration order; the compiler adds padding, not the programmer.
- The struct's size is always a multiple of its **largest member's alignment**.
- Reorder members (largest first) to eliminate unnecessary padding.
- Use `sizeof` and `offsetof` to verify your assumptions — never guess.

## Interview Answer

> "The compiler inserts padding bytes between struct members so each field starts at an address that is a multiple of its size (its alignment requirement). You can minimize padding by ordering members from largest to smallest. The struct's total size is rounded up to a multiple of its most-aligned member."
