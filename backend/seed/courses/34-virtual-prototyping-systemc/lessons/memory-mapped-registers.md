# Memory-Mapped Registers Explained

Every peripheral on a microcontroller — GPIO, UART, SPI, timers, ADC — is controlled by writing to and reading from **memory-mapped registers**. They look like ordinary variables in C, but each read or write causes a real hardware action.

## The Core Idea

In memory-mapped I/O (MMIO), peripheral control registers are placed at fixed addresses in the same address space as RAM and flash. The CPU uses identical load/store instructions to access them. There is no special I/O instruction (unlike x86 `IN`/`OUT`).

```
Address Space (32-bit ARM example)
0x00000000  ┌─────────┐
            │  Flash  │  (firmware code)
0x20000000  ├─────────┤
            │  SRAM   │  (stack, heap, variables)
0x40000000  ├─────────┤
            │ Periph  │  ← memory-mapped registers live here
0xE0000000  ├─────────┤
            │  SCS    │  (Cortex-M system control)
0xFFFFFFFF  └─────────┘
```

A write to `0x40020018` might set a GPIO output high. A read from `0x40011004` might return the current ADC conversion result.

## The `volatile` Keyword

Hardware registers can change at any moment — due to an interrupt, a DMA transfer, or the peripheral's own logic. The compiler must never cache their values in a register or optimise away a read/write. That is what `volatile` enforces.

```c
// WRONG — compiler may optimise the loop away entirely
uint32_t *status_reg = (uint32_t *)0x40013000;
while (*status_reg == 0) { /* wait */ }

// CORRECT — volatile forces every access to hit the bus
volatile uint32_t *status_reg = (volatile uint32_t *)0x40013000;
while (*status_reg == 0) { /* wait */ }
```

Without `volatile`, the compiler sees a loop that never modifies `*status_reg` and assumes it can never change — it either infinite-loops on the first check or optimises the loop out entirely.

## Bit Fields and Masks

Peripheral registers pack multiple settings into a single 32-bit word. Firmware uses bitwise operations to set, clear, or test individual bits without disturbing the rest.

```c
#define GPIOA_BASE   0x48000000UL
#define GPIOA_MODER  (*(volatile uint32_t *)(GPIOA_BASE + 0x00))
#define GPIOA_ODR    (*(volatile uint32_t *)(GPIOA_BASE + 0x14))

// Set PA5 as output (MODER[11:10] = 0b01)
GPIOA_MODER &= ~(0x3UL << 10);   // clear bits 11:10
GPIOA_MODER |=  (0x1UL << 10);   // set  bits 11:10 to 01

// Toggle PA5
GPIOA_ODR ^= (1UL << 5);
```

Read-Modify-Write (RMW) is the standard pattern: read the current register value, modify only the target bits, write it back. Skipping the read half can accidentally clear bits that other code depends on.

## Struct-Based Register Access

Most vendor HALs use C structs that map cleanly onto a peripheral's register block:

```c
typedef struct {
    volatile uint32_t MODER;   // offset 0x00
    volatile uint32_t OTYPER;  // offset 0x04
    volatile uint32_t OSPEEDR; // offset 0x08
    volatile uint32_t PUPDR;   // offset 0x0C
    volatile uint32_t IDR;     // offset 0x10
    volatile uint32_t ODR;     // offset 0x14
    volatile uint32_t BSRR;    // offset 0x18
    volatile uint32_t LCKR;    // offset 0x1C
    volatile uint32_t AFR[2];  // offset 0x20
} GPIO_TypeDef;

#define GPIOA  ((GPIO_TypeDef *)0x48000000UL)

// Now access registers with named fields
GPIOA->ODR |= (1UL << 5);
```

This approach is self-documenting and eliminates magic number offsets throughout the codebase.

## Write-Only and Clear-on-Read Registers

Some registers have special hardware semantics:

- **Write-only:** Reading returns zero or undefined data. Do not RMW — just write.
- **Clear-on-read:** A status bit clears automatically when you read the register. Reading it twice returns different values. Cache the result in a local variable if you need to test multiple bits.
- **Write-1-to-clear (W1C):** Write a `1` to a bit to acknowledge/clear it. Write a `0` to leave it unchanged. Common for interrupt status registers.

```c
// W1C example: clear UART overrun flag by writing 1 to that bit
USART1->ICR = USART_ICR_ORECF;   // writing 0 to other bits leaves them unchanged
```

## Common Pitfalls

- **Missing `volatile`.** The single most common embedded C bug. The symptom is code that works at `-O0` but breaks at `-O2`.
- **Incorrect offset.** Off-by-one in the struct or wrong base address causes writes to land on the wrong register. Always cross-reference the datasheet.
- **Byte vs word access.** Some peripheral registers require 32-bit word access; byte access has undefined behaviour. Compiler struct padding can introduce silent alignment issues.

> **Interview answer:** Memory-mapped I/O places peripheral control registers at specific addresses in the CPU's address space; firmware reads and writes those addresses like variables, but must mark them `volatile` to prevent the compiler from caching or optimising away the accesses.
