# Toggle a Bit with XOR

Toggling flips a bit: if it was 0 it becomes 1, and if it was 1 it becomes 0. XOR is the natural operator for this because XOR with 1 always inverts while XOR with 0 always preserves.

## The Pattern

```cpp
value ^= (1u << n);
```

## Why XOR Works

The XOR truth table for one bit:

| Bit | Mask | Result |
|-----|------|--------|
| 0 | 0 | 0 (unchanged) |
| 1 | 0 | 1 (unchanged) |
| 0 | 1 | 1 (toggled) |
| 1 | 1 | 0 (toggled) |

XOR with 1 flips; XOR with 0 preserves. The mask `1u << n` places a 1 at position `n` and 0s everywhere else, so only bit `n` is affected.

## Worked Example

```cpp
#include <cstdint>

uint8_t led_state = 0b00000000;

// Toggle LED on pin 3 each time this is called
void blink_led() {
    led_state ^= (1u << 3);
    write_gpio(led_state);
}
```

Successive calls cycle the register:

```
Call 1: 0000 0000 ^ 0000 1000 = 0000 1000  (LED on)
Call 2: 0000 1000 ^ 0000 1000 = 0000 0000  (LED off)
Call 3: 0000 0000 ^ 0000 1000 = 0000 1000  (LED on)
```

## Toggling Multiple Bits

XOR multiple positions in one operation:

```cpp
uint8_t flags = 0b11001100;
flags ^= (1u << 0) | (1u << 2) | (1u << 6);
// toggles bits 0, 2, 6
// 1100 1100
// ^ 0100 0101
// = 1000 1001
```

## Self-Inverse Property

Applying the same XOR twice restores the original value:

```cpp
uint32_t original = 0xDEADBEEF;
uint32_t mask     = 0x0000FF00;
uint32_t modified = original ^ mask;
uint32_t restored = modified ^ mask;   // == original
```

This property underlies XOR-swap, simple stream ciphers, and parity calculations.

## XOR Swap (Interview Classic)

```cpp
void swap_no_temp(int& a, int& b) {
    a ^= b;
    b ^= a;
    a ^= b;
}
```

> **Caution:** this is undefined behavior if `a` and `b` alias the same object. Use `std::swap` in practice.

## Toggle vs. Set vs. Clear

| Goal | Operation |
|------|-----------|
| Force to 1 | `value \|= mask` |
| Force to 0 | `value &= ~mask` |
| Flip | `value ^= mask` |

Toggle is appropriate when you do not know or do not care about the current state — you just want it to change. Use set or clear when you need a guaranteed final state.

## Practical Use: Status Register Flip

Some hardware status bits are cleared by writing 1 to them (write-1-to-clear). Others toggle. Always consult the datasheet, but when a toggle is called for:

```cpp
constexpr uint32_t TX_COMPLETE_FLAG = (1u << 5);

// Acknowledge TX complete interrupt by toggling the flag
*STATUS_REG ^= TX_COMPLETE_FLAG;
```

> **Interview answer:** "Toggle bit `n` with `value ^= (1u << n)`. XOR with 1 always flips a bit, and XOR with 0 always preserves it, so the single-bit mask affects only the target position. Applying the same mask twice restores the original."
