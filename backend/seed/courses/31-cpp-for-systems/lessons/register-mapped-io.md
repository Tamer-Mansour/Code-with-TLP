# Modeling Memory-Mapped I/O with volatile

Memory-mapped I/O (MMIO) is the dominant technique for communicating with hardware peripherals in embedded and OS code. A peripheral's registers appear at fixed physical addresses; reading and writing those addresses controls the hardware.

## The Fundamental Pattern

Cast a raw integer address to a `volatile` pointer, then dereference to read or write:

```cpp
volatile uint32_t* const UART_DR = reinterpret_cast<volatile uint32_t*>(0x4000'C000);

*UART_DR = 'A';              // write: sends byte to UART
uint32_t rx = *UART_DR;     // read: receives byte from UART
```

Both `volatile` and `const` on the pointer:
- `volatile` — re-issue load/store every time (no caching by compiler)
- `const` — the pointer itself is fixed (the address never changes)

## Struct Overlay Model

For peripherals with multiple registers, define a C-style struct whose layout matches the hardware register map:

```cpp
struct UART_Periph {
    volatile uint32_t DR;    // 0x000 data register
    volatile uint32_t SR;    // 0x004 status register
    volatile uint32_t BRR;   // 0x008 baud rate register
    volatile uint32_t CR1;   // 0x00C control register 1
    volatile uint32_t CR2;   // 0x010 control register 2
};

UART_Periph* const UART1 = reinterpret_cast<UART_Periph*>(0x4001'3800);

void uart_send_byte(uint8_t b) {
    while (!(UART1->SR & (1u << 7))) {}   // wait for TXE (TX empty) bit
    UART1->DR = b;
}

uint8_t uart_recv_byte() {
    while (!(UART1->SR & (1u << 5))) {}   // wait for RXNE (RX not empty) bit
    return (uint8_t)UART1->DR;
}
```

The struct layout must match the hardware exactly. Use `static_assert` to guard against padding:

```cpp
static_assert(offsetof(UART_Periph, BRR) == 8,  "Layout mismatch");
static_assert(offsetof(UART_Periph, CR1) == 12, "Layout mismatch");
```

If the hardware has reserved gaps, use explicit padding members:

```cpp
struct DMA_Channel {
    volatile uint32_t CCR;
    volatile uint32_t CNDTR;
    volatile uint32_t CPAR;
    volatile uint32_t CMAR;
    uint32_t          RESERVED;   // not volatile — never accessed
};
```

## Bit-Field Access

Bit fields in structs are tempting for register modeling but **volatile bit fields have implementation-defined behavior** in C++. The safer pattern uses explicit masks and shifts:

```cpp
// Prefer masks over bit fields for hardware registers
constexpr uint32_t CR1_UE   = 1u << 13;   // UART enable
constexpr uint32_t CR1_TE   = 1u << 3;    // transmitter enable
constexpr uint32_t CR1_RE   = 1u << 2;    // receiver enable

void uart_enable() {
    UART1->CR1 |= CR1_UE | CR1_TE | CR1_RE;
}
```

Read-modify-write on MMIO (`|=`, `&=`) issues a load then a store — two separate bus transactions. For registers where intermediate states cause side effects, always write the full value at once.

## Memory Barriers and CPU Ordering

`volatile` prevents compiler reordering of volatile accesses relative to each other, but not CPU reordering. On weakly ordered architectures (ARM, POWER), you may need explicit barriers between MMIO accesses:

```cpp
// ARM: data memory barrier before and after critical MMIO sequences
UART1->CR1 = value;
__DSB();            // data synchronization barrier
UART1->SR;          // dummy read to flush write buffer
```

On x86, the strong memory model means most MMIO drivers don't need explicit barriers for correctness (but still use `volatile` to defeat the compiler).

## C++ Wrappers for MMIO

A lightweight C++ wrapper improves safety without overhead:

```cpp
template<uint32_t ADDR>
struct Reg32 {
    static volatile uint32_t& ref() {
        return *reinterpret_cast<volatile uint32_t*>(ADDR);
    }
    static void set(uint32_t v)   { ref() = v; }
    static uint32_t get()         { return ref(); }
    static void set_bits(uint32_t mask)   { ref() |= mask; }
    static void clear_bits(uint32_t mask) { ref() &= ~mask; }
};

using UART1_SR = Reg32<0x4001'3804>;

while (!(UART1_SR::get() & (1u << 7))) {}
```

This approach is zero-overhead (all inlined), type-safe (address is a compile-time constant), and self-documenting.

> **Interview answer:** "Model MMIO by casting a hardware address to a `volatile` struct pointer. `volatile` forces every register read and write to generate actual load/store instructions. Use masks and shifts rather than bit fields, and add memory barriers when the CPU's memory model requires them for ordering between register accesses."
