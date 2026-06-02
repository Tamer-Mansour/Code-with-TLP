# Set a Bit with a Mask

Setting a specific bit means forcing it to 1 while leaving every other bit unchanged. This is one of the most common operations in register-level firmware and driver code.

## The Pattern

```cpp
value |= (1u << n);
```

OR with a mask that has exactly bit `n` set. Any bit ORed with 1 becomes 1; any bit ORed with 0 stays the same.

## Building the Mask

The expression `1u << n` creates a mask with only bit `n` set:

| `n` | `1u << n` (binary, 8-bit) |
|-----|--------------------------|
| 0 | `0000 0001` |
| 3 | `0000 1000` |
| 7 | `1000 0000` |

Using `1u` (unsigned) rather than `1` avoids signed-integer shift undefined behavior when `n` approaches the type width.

## Concrete Example

```cpp
#include <cstdint>

// Hardware GPIO output register
volatile uint32_t* GPIO_OUT = reinterpret_cast<volatile uint32_t*>(0x40010000);

void enable_pin(int pin) {
    *GPIO_OUT |= (1u << pin);  // set the bit for that pin
}
```

Suppose `*GPIO_OUT` is currently `0b00001010` and `pin = 5`:

```
  0000 0000 0000 0000 0000 0000 0000 1010   (current)
| 0000 0000 0000 0000 0000 0000 0010 0000   (mask: 1 << 5)
= 0000 0000 0000 0000 0000 0000 0010 1010   (result)
```

Bit 5 is now 1; bits 1 and 3 are unchanged.

## Setting Multiple Bits at Once

Combine masks with OR before applying:

```cpp
// Set bits 0, 2, and 5 simultaneously
uint8_t flags = 0;
flags |= (1u << 0) | (1u << 2) | (1u << 5);
// flags = 0b00100101
```

## Named Constants Make Intent Clear

In real firmware, avoid magic numbers:

```cpp
constexpr uint32_t UART_TX_ENABLE  = (1u << 3);
constexpr uint32_t UART_RX_ENABLE  = (1u << 4);
constexpr uint32_t UART_LOOPBACK   = (1u << 7);

uint32_t ctrl = 0;
ctrl |= UART_TX_ENABLE | UART_RX_ENABLE;
```

This is self-documenting, diff-friendly, and compiles to the exact same machine code.

## Read-Modify-Write Caution

On hardware registers the sequence `read → modify → write` must be atomic if an interrupt or another core can access the same register. In C++, `|=` is not atomic. Use `std::atomic` or a hardware-specific lock if that matters.

```cpp
#include <atomic>
std::atomic<uint32_t> shared_flags{0};
shared_flags.fetch_or(1u << 4, std::memory_order_relaxed);
```

## Common Pitfall: Wrong Width

```cpp
uint64_t reg = 0;
reg |= (1 << 40);   // Bug! 1 is int (32-bit); shift >= 32 is UB on most platforms
reg |= (1ULL << 40); // Correct: 64-bit literal
```

Always match the literal suffix to the register width: `1u` for 32-bit, `1ULL` for 64-bit.

> **Interview answer:** "To set bit `n`, OR the value with the mask `1u << n`. OR leaves 0-masked bits unchanged and forces 1-masked bits to 1, so exactly one bit changes."
