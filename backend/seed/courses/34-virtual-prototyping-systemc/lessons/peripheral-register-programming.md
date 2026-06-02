# Programming a Peripheral via Its Registers

Every peripheral in an embedded system — whether real silicon or a virtual model — exposes its behavior through a set of memory-mapped registers. Understanding how to read, write, and sequence those registers is the foundational skill of embedded software engineering.

## Memory-Mapped I/O

In most embedded architectures, peripheral registers appear at fixed addresses in the same address space as RAM and ROM. There is no special I/O instruction; you use ordinary loads and stores:

```c
#define UART0_BASE   0x40004000U
#define UART0_DR     (*(volatile uint32_t *)(UART0_BASE + 0x000))
#define UART0_FR     (*(volatile uint32_t *)(UART0_BASE + 0x018))
#define UART0_IBRD   (*(volatile uint32_t *)(UART0_BASE + 0x024))
#define UART0_FBRD   (*(volatile uint32_t *)(UART0_BASE + 0x028))
#define UART0_LCR_H  (*(volatile uint32_t *)(UART0_BASE + 0x02C))
#define UART0_CR     (*(volatile uint32_t *)(UART0_BASE + 0x030))
```

The `volatile` qualifier tells the compiler that reads and writes have side effects — it must not cache the value in a register or reorder accesses. Omitting `volatile` is one of the most dangerous bugs in embedded C.

## The Peripheral Header Pattern

Production code encapsulates registers in a struct:

```c
typedef struct {
    volatile uint32_t DR;      // 0x000  Data register
    volatile uint32_t RSR;     // 0x004  Receive status / error clear
    uint32_t          _res0[4];// 0x008..0x014  Reserved
    volatile uint32_t FR;      // 0x018  Flag register
    uint32_t          _res1[2];// 0x01C..0x020  Reserved
    volatile uint32_t IBRD;    // 0x024  Integer baud-rate divisor
    volatile uint32_t FBRD;    // 0x028  Fractional baud-rate divisor
    volatile uint32_t LCR_H;   // 0x02C  Line control
    volatile uint32_t CR;      // 0x030  Control
    volatile uint32_t IFLS;    // 0x034  Interrupt FIFO level select
    volatile uint32_t IMSC;    // 0x038  Interrupt mask set/clear
    volatile uint32_t RIS;     // 0x03C  Raw interrupt status
    volatile uint32_t MIS;     // 0x040  Masked interrupt status
    volatile uint32_t ICR;     // 0x044  Interrupt clear
} UART_Regs;

#define UART0  ((UART_Regs *) 0x40004000U)
```

Then access is clean and type-safe:

```c
UART0->IBRD = 26;
UART0->FBRD = 3;
```

## The Initialization Sequence

Peripheral initialization almost always follows a prescribed **sequence**. Deviating from it causes hard-to-debug failures. The ARM PL011 UART initialization sequence illustrates the pattern:

```c
void uart_init(uint32_t f_clk, uint32_t baud) {
    // 1. Disable the UART before changing configuration
    UART0->CR &= ~(1u << 0);   // UARTEN = 0

    // 2. Wait for any ongoing transmission to finish
    while (UART0->FR & (1u << 3));  // BUSY flag

    // 3. Flush the FIFOs
    UART0->LCR_H &= ~(1u << 4);    // FEN = 0

    // 4. Set baud-rate divisors
    uint32_t brd16  = f_clk / (16 * baud);
    uint32_t brd_frac= (uint32_t)(((double)f_clk / (16.0 * baud) - brd16) * 64 + 0.5);
    UART0->IBRD = brd16;
    UART0->FBRD = brd_frac;

    // 5. Set line control: 8N1, FIFOs enabled
    UART0->LCR_H = (3u << 5) |   // WLEN = 11 (8 bits)
                   (1u << 4);     // FEN  = 1 (enable FIFOs)

    // 6. Enable TX, RX, and the UART
    UART0->CR = (1u << 9) |       // TXE
                (1u << 8) |       // RXE
                (1u << 0);        // UARTEN
}
```

Notice: disable first, configure, then enable. This prevents the peripheral from acting on partial configuration during setup.

## Read-Modify-Write and Atomic Access

When you need to change only some bits of a register, use a read-modify-write:

```c
// Set bits 3 and 5 without disturbing others
REG |= (1u << 3) | (1u << 5);

// Clear bit 7
REG &= ~(1u << 7);

// Change bits [5:4] to 0b10
REG = (REG & ~(0x3u << 4)) | (0x2u << 4);
```

Some peripherals provide dedicated **set** and **clear** registers (e.g., STM32 GPIO `BSRR`) that allow atomic single-bit manipulation without read-modify-write — critical in interrupt-driven code.

## Write-1-to-Clear (W1C) Registers

Many status and interrupt registers use a **W1C** access convention: to clear a flag, write a `1` to its bit position (not a `0`). Writing `0` has no effect:

```c
// Clear the receive overrun flag (bit 3) — W1C
UART0->RSR = (1u << 3);

// WRONG: this would clear ALL flags, including ones you haven't handled
// UART0->RSR = 0xFFFFFFFF;
```

## Reserved Bits

Always write `0` to reserved bits and mask them out when reading. Hardware may use reserved bits for undocumented features, or they may be tied to power/reset state. Writing arbitrary values to reserved bits can corrupt peripheral state or violate chip errata rules.

## Worked Example: Enabling a GPIO Pin as Output

Using the register-struct pattern on a hypothetical GPIO port:

```c
typedef struct {
    volatile uint32_t DDR;  // direction: 1 = output
    volatile uint32_t ODR;  // output data
    volatile uint32_t IDR;  // input data (read-only)
    volatile uint32_t PUR;  // pull-up enable
} GPIO_Regs;

#define GPIOA  ((GPIO_Regs *) 0x40020000U)

void gpio_set_output(uint8_t pin) {
    GPIOA->DDR |= (1u << pin);   // set direction = output
    GPIOA->ODR &= ~(1u << pin);  // initialise to LOW
}

void gpio_write(uint8_t pin, bool val) {
    if (val)
        GPIOA->ODR |=  (1u << pin);
    else
        GPIOA->ODR &= ~(1u << pin);
}
```

## Common Pitfalls

- **Missing `volatile`** — the compiler may cache register reads, leading to stale values.
- **Wrong initialization order** — writing to configuration registers while the peripheral is enabled can latch incorrect values.
- **Ignoring reserved bits** — reading and re-writing a register without masking reserved bits may corrupt state.
- **Confusing W1C with write-0-to-clear** — some peripherals use the opposite convention; always check the reference manual.
- **Byte vs. word access** — some registers only respond correctly to 32-bit aligned word access; byte or half-word access may behave unexpectedly.

> **Interview answer:** Peripheral registers are memory-mapped; you access them with `volatile` pointers. The critical rules are: always `volatile`, follow the datasheet init sequence (disable, configure, enable), use read-modify-write for individual bits, write 0 to reserved bits, and understand the W1C vs. W0C flag-clearing convention.
