# Bytes, Words, and Byte-Addressable Memory

Before an OS can manage memory it must speak the language of memory addressing. That language is built on bytes, words, and the concept of addressability.

## The Byte

A **byte** is 8 bits. It is the smallest unit that has its own address on virtually every modern architecture. A single byte can represent 256 values (0–255 unsigned, or −128 to 127 signed).

```
Bit positions:   7  6  5  4  3  2  1  0
Example byte:    0  1  0  1  1  0  1  1   = 0x5B = 91 decimal
```

## Words

A **word** is the natural integer size that a CPU handles most efficiently — matching the width of general-purpose registers and the data bus. Word size varies by architecture:

| Architecture | Word size |
|---|---|
| 8086 | 16 bits (2 bytes) |
| x86 (IA-32) | 32 bits (4 bytes) |
| x86-64, ARM64 | 64 bits (8 bytes) |
| AVR (Arduino) | 8 bits (1 byte) |

The word size determines the maximum value an integer register can hold without overflow and, historically, the maximum directly addressable physical memory (a 32-bit address bus limits RAM to 4 GB).

Note: on x86, Intel's documentation still calls 16 bits a "word", 32 bits a "doubleword" (DWORD), and 64 bits a "quadword" (QWORD) — this is a historical naming artifact from the 8086 era.

## Byte-Addressable Memory

Modern systems are **byte-addressable**: every byte of RAM has a unique numeric address, and the address space is a flat array of bytes.

```
Address:   0x0000  0x0001  0x0002  0x0003  0x0004 ...
Content:   [ 0x41 ][ 0x42 ][ 0x43 ][ 0x00 ][ 0xFF ] ...
```

A 32-bit address bus provides 2³² = 4,294,967,296 addressable bytes = 4 GB of address space. A 64-bit bus could address 2⁶⁴ bytes = 16 exabytes — far more than any current physical RAM.

## Multi-Byte Values in Memory

When a multi-byte value (int, float, pointer) is stored, consecutive bytes are used starting at the base address. Reading or writing a 4-byte integer at address `A` touches bytes `A`, `A+1`, `A+2`, `A+3`.

```c
uint32_t x = 0xDEADBEEF;
// Stored at address 0x1000:
// Addr: 0x1000 0x1001 0x1002 0x1003
// Bytes (little-endian): EF   BE   AD   DE
```

(The byte order within those slots is endianness — covered in the next lesson.)

## Alignment

Most CPUs require or prefer that multi-byte values be stored at addresses that are multiples of their size. This is called **alignment**.

| Type | Size | Natural alignment |
|---|---|---|
| `char` | 1 byte | Any address |
| `short` | 2 bytes | Multiple of 2 |
| `int` | 4 bytes | Multiple of 4 |
| `double` | 8 bytes | Multiple of 8 |
| Cache line | 64 bytes | Multiple of 64 |

An unaligned access on ARM will raise a fault. On x86 it succeeds but may be slower (the CPU may issue two memory bus transactions). The OS allocates pages (4 KB, 4-KB aligned) and the C runtime ensures `malloc` returns 8- or 16-byte aligned memory.

```c
// Checking alignment in C
#include <stdint.h>
uintptr_t addr = (uintptr_t)ptr;
if (addr % sizeof(uint32_t) == 0) {
    // ptr is 4-byte aligned — safe for uint32_t access
}
```

## Common Pitfalls

- **Confusing address and content** — address 0x1000 is the location; the byte at that address could be any value 0x00–0xFF.
- **Off-by-one in size calculations** — a 32-bit integer occupies bytes at addresses N, N+1, N+2, N+3 (four bytes total, last byte at N+3, not N+4).
- **Pointer arithmetic in C** — `ptr + 1` advances by `sizeof(*ptr)` bytes, not by 1 byte. `(char *)ptr + 1` advances by 1 byte.

```c
int arr[3] = {10, 20, 30};
int *p = arr;
p++;              // p now points to arr[1] (advanced by 4 bytes on a 32-bit int system)
char *cp = (char *)arr;
cp++;             // cp now points to the second BYTE of arr[0]
```

> **Interview answer:** Memory is byte-addressable — every byte has a unique address. A word is the CPU's natural integer width (64 bits on modern x86). Alignment means a multi-byte value's address must be a multiple of its size; misalignment causes faults on strict architectures and performance penalties on x86.
