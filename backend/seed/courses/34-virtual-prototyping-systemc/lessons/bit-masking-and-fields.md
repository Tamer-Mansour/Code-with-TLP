# Bit Masks and Extracting Bit Fields

Hardware registers pack multiple configuration fields into a single word. Extracting or modifying one field without disturbing the others requires a disciplined mask-and-shift pattern.

## Anatomy of a Mask

A **bit mask** is a value with 1s in the positions of interest and 0s everywhere else.

```
Register word (32-bit):  0xA5C3'1F2B
Mask for bits 11:8:      0x0000'0F00
                                ^^^^  four bits isolated
```

The mask for a contiguous field starting at bit `lo` with width `w` is:

```cpp
uint32_t mask = ((1u << w) - 1u) << lo;
```

For example, a 4-bit field at bit position 8:

```cpp
uint32_t mask = ((1u << 4) - 1u) << 8;
//             = 0xF << 8
//             = 0x0000'0F00
```

## Extracting a Field

**Step 1:** AND with the mask to zero out all other bits.
**Step 2:** Right-shift by `lo` to move the field to bit 0.

```cpp
uint32_t reg   = 0xA5C3'1F2Bu;
uint32_t lo    = 8;
uint32_t w     = 4;
uint32_t mask  = ((1u << w) - 1u) << lo;

uint32_t field = (reg & mask) >> lo;   // 0x2 (bits 11:8 of 0x1F2B = 0xF → wait, let's verify)
```

Worked step-by-step:

```
reg  = 0x....1F2B = 0001 1111 0010 1011
mask = 0x00000F00 = 0000 0000 0000 1111 0000 0000  (bits 11:8)
AND  =             0000 0000 0000 0010 0000 0000  = 0x0000'0200
>> 8 =             0x00000002  → field value = 2
```

## Inserting a Field (Read-Modify-Write)

```cpp
void set_field(volatile uint32_t* reg, uint32_t lo, uint32_t w, uint32_t val) {
    uint32_t mask = ((1u << w) - 1u) << lo;
    *reg = (*reg & ~mask)            // clear the field
         | ((val << lo) & mask);    // insert new value
}
```

The `~mask` clears the field; `val << lo` positions the new value; the AND with `mask` prevents a too-large `val` from corrupting adjacent bits.

## Named Macros and Inline Functions

Raw numeric offsets in application code become unreadable. Common practice in embedded firmware is to define named constants:

```cpp
// GPIO control register layout
#define GPIO_MODE_POS  0u
#define GPIO_MODE_MSK  (0x3u << GPIO_MODE_POS)   // bits 1:0
#define GPIO_SPEED_POS 2u
#define GPIO_SPEED_MSK (0x3u << GPIO_SPEED_POS)  // bits 3:2
#define GPIO_PULL_POS  4u
#define GPIO_PULL_MSK  (0x3u << GPIO_PULL_POS)   // bits 5:4

// Read mode field
uint32_t mode = (GPIOA->CR & GPIO_MODE_MSK) >> GPIO_MODE_POS;

// Set speed to 2
GPIOA->CR = (GPIOA->CR & ~GPIO_SPEED_MSK)
           | ((2u << GPIO_SPEED_POS) & GPIO_SPEED_MSK);
```

In C++ you can wrap the same logic in a constexpr helper and leverage type safety.

## Common Single-Bit Tests

| Intent | Expression |
|--------|-----------|
| Test bit N | `(reg >> N) & 1u` |
| Test bit N | `(reg & (1u << N)) != 0` |
| Isolate low byte | `reg & 0xFFu` |
| Isolate high byte of 16-bit | `(reg >> 8) & 0xFFu` |

## Pitfalls

- **Shift amount >= width of type** is undefined behaviour in C/C++. Use `uint64_t` shifts when the field could reach bit 31+ in a 32-bit word.
- **Signed types and right shift**: always extract into an unsigned variable, then cast to signed if the field is two's complement.
- **Not masking the inserted value**: if `val` is wider than `w` bits and you omit the `& mask` step, you silently corrupt adjacent fields.

## Worked Example — UART Baud Rate Divisor

A UART BRR register encodes integer divisor in bits 15:4 and fraction in bits 3:0.

```cpp
constexpr uint32_t BRR_FRAC_POS = 0;
constexpr uint32_t BRR_FRAC_MSK = 0xFu;
constexpr uint32_t BRR_MANT_POS = 4;
constexpr uint32_t BRR_MANT_MSK = 0xFFF0u;

uint32_t mantissa = 26;
uint32_t fraction =  3;

uint32_t brr = ((mantissa << BRR_MANT_POS) & BRR_MANT_MSK)
             | ((fraction  << BRR_FRAC_POS) & BRR_FRAC_MSK);
// brr = 0x01A3
```

**Interview answer:** "I build the mask as `((1u << width) - 1) << lsb`, AND the register with it, then right-shift by `lsb`. Insertion uses AND with the inverted mask to clear, then OR with the shifted new value."
