# Bit Masks and Flag Fields in Hardware Registers

Hardware registers pack multiple control and status fields into a single integer. Knowing how to define, read, and write these fields without disturbing adjacent bits is the core skill of driver and firmware development.

## Why Registers Use Bit Fields

A 32-bit control register on a microcontroller might encode:

- Bits 0-1: clock source selection (2-bit enum)
- Bit 2: module enable
- Bits 3-5: prescaler value
- Bits 8-11: interrupt priority
- Bit 31: software reset

Packing state this way minimizes silicon, keeps related config in one bus transaction, and makes atomic register updates possible.

## Defining Masks and Shifts

The clearest pattern uses two constants per field: a shift and a mask.

```cpp
// Clock Source field: bits [1:0]
constexpr uint32_t CLK_SRC_SHIFT = 0;
constexpr uint32_t CLK_SRC_MASK  = 0x3u;   // 0b11

// Prescaler field: bits [5:3]
constexpr uint32_t PRESCALER_SHIFT = 3;
constexpr uint32_t PRESCALER_MASK  = 0x7u;  // 0b111

// Module enable: bit 2
constexpr uint32_t MODULE_EN = (1u << 2);
```

### Reading a Field

```cpp
volatile uint32_t* CTRL = reinterpret_cast<volatile uint32_t*>(0x40023800);

uint32_t clk_src  = (*CTRL >> CLK_SRC_SHIFT)  & CLK_SRC_MASK;
uint32_t prescale = (*CTRL >> PRESCALER_SHIFT) & PRESCALER_MASK;
bool     enabled  = (*CTRL & MODULE_EN) != 0;
```

### Writing a Field (Read-Modify-Write)

```cpp
void set_prescaler(uint32_t value) {
    uint32_t reg = *CTRL;
    reg &= ~(PRESCALER_MASK << PRESCALER_SHIFT);   // clear the field
    reg |=  (value & PRESCALER_MASK) << PRESCALER_SHIFT; // write new value
    *CTRL = reg;
}
```

Always AND the new value with its mask before shifting in — this prevents a caller from accidentally corrupting adjacent fields.

## Enum-Class Flags

For single-bit flags used as a bitfield, a scoped enum with explicit underlying type avoids magic numbers:

```cpp
#include <cstdint>

enum class UartCtrl : uint32_t {
    TxEnable    = 1u << 0,
    RxEnable    = 1u << 1,
    Loopback    = 1u << 3,
    FifoEnable  = 1u << 4,
    ParityOdd   = 1u << 7,
};

// Combine with bitwise OR (requires overloading or a cast)
uint32_t cfg = static_cast<uint32_t>(UartCtrl::TxEnable)
             | static_cast<uint32_t>(UartCtrl::RxEnable);
```

Some teams define operator overloads for `|`, `&`, `~` on their flag enums to make the syntax cleaner.

## The C++ `std::bitset` Alternative

For software flags where performance is not critical, `std::bitset<N>` offers named access:

```cpp
#include <bitset>
std::bitset<32> flags;
flags.set(4);
flags.reset(2);
bool active = flags.test(4);
```

`std::bitset` is not suitable for memory-mapped I/O because it does not guarantee the underlying memory layout or volatile semantics.

## Bit-Field Struct (Use Carefully)

C and C++ allow struct bit-field syntax:

```cpp
struct UartCtrl {
    uint32_t tx_enable : 1;
    uint32_t rx_enable : 1;
    uint32_t reserved  : 1;
    uint32_t loopback  : 1;
    uint32_t fifo_en   : 1;
    uint32_t           : 2;  // padding
    uint32_t parity    : 1;
};
```

- **Pro:** Readable, direct field access.
- **Con:** Bit ordering and padding are implementation-defined. Never rely on this layout for hardware register access across compilers or architectures. Use explicit shift/mask instead.

## Worked Example: GPIO Pin Mode Register

A common GPIO mode register stores 2 bits per pin. For a 16-pin port that uses a 32-bit register:

```cpp
constexpr uint32_t pin_mode_shift(int pin) { return pin * 2; }
constexpr uint32_t pin_mode_mask = 0x3u;

enum class PinMode : uint32_t { Input = 0, Output = 1, AltFunc = 2, Analog = 3 };

void set_pin_mode(volatile uint32_t* moder, int pin, PinMode mode) {
    uint32_t reg = *moder;
    reg &= ~(pin_mode_mask << pin_mode_shift(pin));
    reg |=  (static_cast<uint32_t>(mode) << pin_mode_shift(pin));
    *moder = reg;
}
```

## Summary

| Task | Code Pattern |
|------|-------------|
| Define single-bit flag | `constexpr uint32_t FLAG = (1u << n);` |
| Define multi-bit field | `constexpr uint32_t MASK = 0x7u; constexpr uint32_t SHIFT = 3;` |
| Read field | `(reg >> SHIFT) & MASK` |
| Write field | `reg = (reg & ~(MASK << SHIFT)) \| ((val & MASK) << SHIFT)` |

> **Interview answer:** "A hardware register is just an integer. Use shift and mask constants to isolate fields. To write a field: clear the target bits with `&= ~(mask << shift)`, then OR in the new value with `|= (val & mask) << shift`. Always AND the value with its mask to prevent overflow into adjacent fields."
