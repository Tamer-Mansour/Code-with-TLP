# Unions and Bit-Fields for Register Maps

Microcontroller and FPGA peripherals expose hardware registers as memory-mapped I/O. Accessing them requires precise control over every bit's position. C++ `union` and bit-fields are the canonical tools for this — when used carefully.

## Unions — One Memory Location, Multiple Interpretations

A `union` overlays all its members at the same starting address. Its size equals the size of the largest member (rounded to the largest alignment).

```cpp
union U {
    uint32_t raw;    // 4 bytes
    float    f;      // 4 bytes
    uint8_t  bytes[4];
};
// sizeof(U) == 4, alignof(U) == 4
```

Only one member is the **active** member at a time. Reading a member other than the one last written is **undefined behavior in C++** (though gcc/clang deliberately define it as an extension and the C standard allows it).

### Hardware Register Union Pattern

```cpp
// UART control register (32-bit, memory-mapped)
union UartControl {
    uint32_t raw;       // for atomic read/write of the whole register
    struct {
        uint32_t enable     : 1;   // bit  0
        uint32_t tx_enable  : 1;   // bit  1
        uint32_t rx_enable  : 1;   // bit  2
        uint32_t parity_en  : 1;   // bit  3
        uint32_t parity_sel : 2;   // bits 4-5
        uint32_t reserved   : 26;  // bits 6-31
    } bits;
};

volatile UartControl* uart_ctrl =
    reinterpret_cast<volatile UartControl*>(0x40011000);

// Enable TX and RX without disturbing other bits:
uart_ctrl->bits.tx_enable = 1;
uart_ctrl->bits.rx_enable = 1;

// Read the whole register at once:
uint32_t snapshot = uart_ctrl->raw;
```

`volatile` is mandatory for memory-mapped I/O; without it the compiler may cache the value in a register and miss hardware-driven changes.

## Bit-Fields — Syntax and Rules

A bit-field member has the form `type name : width;` where width is a non-negative integer constant.

```cpp
struct Flags {
    unsigned int ready   : 1;   // 1 bit
    unsigned int mode    : 3;   // 3 bits (values 0-7)
    unsigned int channel : 4;   // 4 bits (values 0-15)
    unsigned int         : 8;   // 8 unnamed bits (reserved/padding)
    unsigned int irq     : 1;   // next bit
};
```

### What the Standard Leaves Implementation-Defined

Bit-fields are notoriously under-specified by the C++ standard:

| Property | Defined by |
|---|---|
| Bit ordering within a storage unit | Implementation |
| Whether a bit-field can straddle a storage unit boundary | Implementation |
| Signedness of plain `int` bit-field | Implementation |
| Alignment of the struct holding bit-fields | Implementation |

This means a struct with bit-fields is **not portable across different compilers or architectures** as a hardware register map without compiler-specific attributes.

### GCC/Clang Behavior (x86/ARM, little-endian)

GCC and Clang lay out bit-fields starting from the **least-significant bit** of the storage unit and filling upward. For the UART example above, `enable` occupies bit 0 of the 32-bit word, matching a little-endian register where bit 0 is the physically lowest bit.

```cpp
// Verify with a static assertion:
static_assert(sizeof(UartControl) == 4,
              "UartControl must be exactly one 32-bit register");
```

## Unnamed Zero-Width Bit-Fields

A zero-width unnamed bit-field forces alignment to the next storage unit boundary:

```cpp
struct Split {
    uint8_t  a : 4;
    uint8_t    : 0;   // skip to next uint8_t boundary
    uint8_t  b : 4;
};
// sizeof(Split) == 2 — a and b are in separate bytes
```

## Practical Register-Map Template

```cpp
#pragma pack(push, 1)  // ensure no inter-field padding surprises

struct GpioRegs {
    union {
        uint32_t raw;
        struct {
            uint32_t pin0_out  : 1;
            uint32_t pin1_out  : 1;
            uint32_t pin2_out  : 1;
            uint32_t pin3_out  : 1;
            uint32_t reserved  : 28;
        } bits;
    } data_out;   // offset 0

    union {
        uint32_t raw;
        struct {
            uint32_t pin0_dir  : 1;   // 0=input, 1=output
            uint32_t pin1_dir  : 1;
            uint32_t pin2_dir  : 1;
            uint32_t pin3_dir  : 1;
            uint32_t reserved  : 28;
        } bits;
    } direction;  // offset 4
};

#pragma pack(pop)

static_assert(sizeof(GpioRegs) == 8);
static_assert(offsetof(GpioRegs, direction) == 4);
```

## Pitfalls

- **Atomicity**: modifying a single bit-field field compiles to a read-modify-write of the entire storage unit. Other threads can observe a torn value unless the whole unit is written atomically.
- **`&` of a bit-field is forbidden**: bit-fields have no addressable storage unit address.
- **Portability**: always add `static_assert` guards and test on your target compiler/architecture.

> **Interview answer:** In embedded systems, a `union` containing a `uint32_t` and a bit-field struct gives you both atomic whole-register access via the integer member and named bit-field access via the struct. The `volatile` qualifier prevents the compiler from caching the register value, and `static_assert` on size and offsets catches portability issues at compile time.
