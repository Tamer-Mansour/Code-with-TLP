# Clear a Bit with a Mask

Clearing a bit forces it to 0 while leaving every other bit intact. The idiom is slightly more involved than setting because we need a mask that is 0 in exactly one position and 1 everywhere else.

## The Pattern

```cpp
value &= ~(1u << n);
```

Two steps happen here:

1. `1u << n` builds a mask with only bit `n` set.
2. `~(...)` flips every bit of that mask, producing a word that is 0 at bit `n` and 1 everywhere else.
3. AND with the original value: bits ANDed with 1 survive unchanged; bit `n` ANDed with 0 becomes 0.

## Mask Visualization

For `n = 3` on an 8-bit value:

```
  1u << 3    = 0000 1000
~(1u << 3)   = 1111 0111   ← clear mask

  1010 1011   (original)
& 1111 0111   (clear mask)
= 1010 0011   (bit 3 cleared)
```

## Concrete Example

```cpp
#include <cstdint>

volatile uint32_t* CTRL_REG = reinterpret_cast<volatile uint32_t*>(0x40020004);

constexpr uint32_t POWER_EN_BIT = 6;

void disable_power() {
    *CTRL_REG &= ~(1u << POWER_EN_BIT);
}
```

## Clearing Multiple Bits

Combine the individual masks before complementing:

```cpp
constexpr uint8_t MASK_BITS_1_AND_5 = (1u << 1) | (1u << 5);

uint8_t status = 0b11100111;
status &= ~MASK_BITS_1_AND_5;   // clears bits 1 and 5
// result: 0b11000101
```

## Named Bit-Field Constants

A common firmware pattern pairs a "set" constant with a "clear" constant derived from it:

```cpp
constexpr uint32_t TIMER_START     = (1u << 0);
constexpr uint32_t TIMER_INTERRUPT = (1u << 1);
constexpr uint32_t TIMER_ENABLE    = (1u << 4);

// Enable timer, clear start and interrupt flags first
uint32_t cfg = *TIMER_REG;
cfg &= ~(TIMER_START | TIMER_INTERRUPT);  // clear two flags
cfg |= TIMER_ENABLE;                      // set enable
*TIMER_REG = cfg;
```

## Do Not Use XOR to Clear

A common mistake is using XOR to "clear" a bit:

```cpp
value ^= (1u << n);   // WRONG for clearing — this TOGGLES, not clears
```

If the bit was already 0, XOR sets it to 1. AND with the complement mask always clears regardless of the current state.

## Width Pitfall (same as setting)

For 64-bit registers, use `1ULL`:

```cpp
uint64_t reg = some_value;
reg &= ~(1ULL << 48);   // correct; ~(1u << 48) is UB
```

## Read-Modify-Write and Atomicity

Like setting, clearing via `&=` is not atomic. On multiprocessor or interrupt-driven code:

```cpp
std::atomic<uint32_t> flags;
flags.fetch_and(~(1u << 3), std::memory_order_relaxed);
```

> **Interview answer:** "To clear bit `n`, AND the value with the bitwise complement of the mask: `value &= ~(1u << n)`. The complement flips the single-bit mask to all-ones-with-one-zero, and AND with 0 forces that bit off while preserving everything else."
