# Bit Manipulation Primer: Masks, Shifts, and Flags

OS kernels, device drivers, and network stacks are dense with bit manipulation. Status registers, permission bits, packet headers, and page table entries are all packed into individual bits of integers. Reading and writing those bits without disturbing others is a fundamental skill.

## The Six Bitwise Operators

| Operator | C symbol | Effect |
|---|---|---|
| AND | `&` | 1 only if both bits are 1 |
| OR | `\|` | 1 if either bit is 1 |
| XOR | `^` | 1 if bits differ |
| NOT (complement) | `~` | Flip every bit |
| Left shift | `<<` | Shift bits left, fill with 0s |
| Right shift | `>>` | Shift bits right (logical: fill 0s; arithmetic: fill sign bit) |

```c
uint8_t a = 0b10110101;  // 0xB5 = 181
uint8_t b = 0b01101100;  // 0x6C = 108

a & b  == 0b00100100  // AND  — bits both set
a | b  == 0b11111101  // OR   — either set
a ^ b  == 0b11011001  // XOR  — bits that differ
~a     == 0b01001010  // NOT  — all flipped (for uint8_t)
a << 2 == 0b11010100  // left shift by 2 (low bits zeroed)
a >> 1 == 0b01011010  // right shift by 1 (unsigned: high bit zeroed)
```

## Bit Masks

A **mask** is an integer with specific bits set to 1, used to isolate, set, clear, or toggle target bits in another value.

### Set a bit (OR with mask)
```c
uint8_t flags = 0b00000000;
flags |= (1 << 3);   // set bit 3 → 0b00001000
```

### Clear a bit (AND with inverted mask)
```c
flags &= ~(1 << 3);  // clear bit 3 → 0b00000000
```

### Toggle a bit (XOR with mask)
```c
flags ^= (1 << 3);   // toggle bit 3
```

### Test a bit (AND, check non-zero)
```c
if (flags & (1 << 3)) {
    // bit 3 is set
}
```

## Extracting a Multi-Bit Field

Many hardware registers pack multiple fields into a single word. To extract bits [5:3] (3 bits starting at position 3):

```c
uint8_t reg = 0b10111010;  // 0xBA
uint8_t field = (reg >> 3) & 0b111;  // shift down then mask to 3 bits
// reg >> 3 = 0b00010111
// & 0b111  = 0b00000111 = 7
```

General formula: `(value >> start_bit) & ((1 << num_bits) - 1)`

## Packing a Multi-Bit Field

```c
uint8_t reg = 0b10000010;  // existing register value
uint8_t new_val = 0b101;   // 3-bit value to insert at bits [5:3]

// Clear the target field, then OR in the new value
reg = (reg & ~(0b111 << 3)) | ((new_val & 0b111) << 3);
// ~(0b111 << 3) = ~0b00111000 = 0b11000111
// reg & mask     = 0b10000010
// new_val << 3   = 0b00101000
// result         = 0b10101010
```

## Real-World Examples

### Linux file permission bits (mode_t)
```c
// S_IRUSR = 0400 = bit 8: owner read
// S_IWUSR = 0200 = bit 7: owner write
// S_IXUSR = 0100 = bit 6: owner execute
mode_t mode = 0644;  // rw-r--r--
if (mode & S_IRUSR) { /* owner can read */ }
```

### x86 RFLAGS register
```c
#define CF_FLAG (1 << 0)   // Carry flag
#define ZF_FLAG (1 << 6)   // Zero flag
#define SF_FLAG (1 << 7)   // Sign flag
#define OF_FLAG (1 << 11)  // Overflow flag

uint64_t rflags = get_rflags();
if (rflags & ZF_FLAG) { /* last result was zero */ }
```

### Network port (packed in a uint16_t big-endian)
```c
uint16_t header = 0x1F90;  // port 8080 in network byte order
uint16_t port = ntohs(header);  // convert to host byte order → 8080
```

## Common Pitfalls

- **Using `int` instead of `unsigned`** for right shift — arithmetic right shift on signed integers fills with the sign bit, not zero. Always use `unsigned` types for bit manipulation.
- **Operator precedence** — `&` has lower precedence than `==`. Always parenthesize: `if ((flags & MASK) == MASK)` not `if (flags & MASK == MASK)`.
- **Shifting by the type's width** — `1 << 32` on a 32-bit `int` is undefined behavior in C. Use `1u << 31` for the highest bit of a `uint32_t`.
- **Forgetting the mask when extracting** — `reg >> 3` without ANDing with a mask leaves the upper bits in the result.

> **Interview answer:** Bit manipulation uses AND to clear/test bits, OR to set bits, XOR to toggle bits, and shifts to move fields to/from bit position 0. To extract a k-bit field starting at bit n: `(value >> n) & ((1 << k) - 1)`. To write it back: clear the field with `& ~(mask << n)` then OR in the new value shifted up by n.
