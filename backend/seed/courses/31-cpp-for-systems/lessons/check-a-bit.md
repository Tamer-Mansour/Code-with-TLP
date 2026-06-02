# Check Whether a Bit Is Set

Reading the state of a specific bit is the "query" side of bit manipulation. It appears constantly in polling loops, interrupt handlers, and status-register checks.

## The Pattern

```cpp
bool is_set = (value >> n) & 1u;
```

or equivalently:

```cpp
bool is_set = (value & (1u << n)) != 0;
```

Both idioms are common; the second is slightly easier to read because the mask is explicit.

## How It Works

### Approach 1: Shift then mask

Shift the target bit down to position 0, then AND with 1:

```
value    = 0b10110100
n        = 5
value >> 5 = 0b00000101
& 1        = 0b00000001   → 1 (bit 5 was set)
```

### Approach 2: Mask then compare

Build a mask for bit `n`, AND it with value, and check for non-zero:

```
value    = 0b10110100
mask     = 0b00100000   (1u << 5)
& mask   = 0b00100000   → non-zero → bit is set
```

## Concrete Example: UART Status Poll

```cpp
#include <cstdint>

constexpr uint32_t UART_RX_READY = (1u << 0);
constexpr uint32_t UART_TX_EMPTY = (1u << 1);
constexpr uint32_t UART_OVERRUN  = (1u << 3);

volatile uint32_t* UART_STATUS = reinterpret_cast<volatile uint32_t*>(0x40011004);

char read_uart_byte() {
    // Wait until RX buffer has data
    while ((*UART_STATUS & UART_RX_READY) == 0) {
        // spin
    }

    if (*UART_STATUS & UART_OVERRUN) {
        handle_overrun_error();
    }

    return *reinterpret_cast<volatile char*>(0x40011008);
}
```

## Checking Multiple Bits

To verify that **all** bits in a mask are set:

```cpp
uint32_t required = (1u << 2) | (1u << 4) | (1u << 7);
bool all_set = (value & required) == required;
```

To verify that **any** bit in a mask is set:

```cpp
bool any_set = (value & required) != 0;
```

## Extracting a Multi-Bit Field

When a register encodes a numeric field spanning several bits, shift and mask together:

```cpp
// Bits [5:3] hold a 3-bit priority field
constexpr uint32_t PRIO_SHIFT = 3;
constexpr uint32_t PRIO_MASK  = 0x7;   // 0b111

uint32_t priority = (reg >> PRIO_SHIFT) & PRIO_MASK;
```

## Boolean Conversion Pitfall

In C++, `(value & mask)` yields an integer, not a bool. When you assign to `bool`, any nonzero value converts to `true`. But comparing with `== 1` can be wrong:

```cpp
uint8_t flags = 0b00001100;
// Wrong: (flags & 0x04) is 4, not 1
if ((flags & 0x04) == 1) { ... }  // never true!

// Correct:
if ((flags & 0x04) != 0) { ... }
// or:
if (flags & 0x04) { ... }   // implicit non-zero check
```

## Summary Table

| Goal | Expression |
|------|-----------|
| Is bit `n` set? | `(value >> n) & 1u` |
| Is bit `n` clear? | `!((value >> n) & 1u)` |
| Are all bits in mask set? | `(value & mask) == mask` |
| Is any bit in mask set? | `(value & mask) != 0` |
| Extract field at offset `s`, width `w` | `(value >> s) & ((1u << w) - 1)` |

> **Interview answer:** "To test bit `n`, AND the value with the mask `1u << n` and compare to 0: `(value & (1u << n)) != 0`. A non-zero result means the bit is set. To check multiple bits, build a combined mask and test whether `(value & mask) == mask` for all-set, or `!= 0` for any-set."
