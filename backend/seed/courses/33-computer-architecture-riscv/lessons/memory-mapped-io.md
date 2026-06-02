# Memory-Mapped I/O Explained

Memory-Mapped I/O (MMIO) is the dominant I/O paradigm on modern processors. The core idea is elegant: assign each device register a physical address in the same address space that the CPU uses for RAM. A load or store to that address talks to the device, not to memory.

## How MMIO Works

When the CPU issues a load instruction to address `0x10000000`, the memory bus (or interconnect fabric) routes the transaction. The hardware address decoder checks whether that address falls in a RAM range or a device range:

```
Physical Address Map (simplified RISC-V board)
┌─────────────────────────────────┐
│ 0x00000000 – 0x0FFFFFFF  DRAM   │
│ 0x10000000 – 0x100000FF  UART0  │
│ 0x10001000 – 0x100010FF  GPIO   │
│ 0x20000000 – 0x200FFFFF  SPI    │
└─────────────────────────────────┘
```

If the address belongs to UART0, the bus routes the transaction to the UART peripheral, which responds with the current value of its register.

## Accessing MMIO in C

MMIO registers are accessed via pointer dereferences. The `volatile` qualifier is critical:

```c
#include <stdint.h>

// Base address of a RISC-V UART (e.g., SiFive FE310)
#define UART0_BASE  0x10013000UL

// Register offsets (bytes)
#define UART_TXDATA  0x00   // Transmit data register
#define UART_RXDATA  0x04   // Receive data register
#define UART_TXCTRL  0x08   // Transmit control
#define UART_RXCTRL  0x0C   // Receive control
#define UART_IE      0x10   // Interrupt enable
#define UART_IP      0x14   // Interrupt pending
#define UART_DIV     0x18   // Baud rate divisor

// Typed pointer to the UART register block
typedef struct {
    volatile uint32_t txdata;
    volatile uint32_t rxdata;
    volatile uint32_t txctrl;
    volatile uint32_t rxctrl;
    volatile uint32_t ie;
    volatile uint32_t ip;
    volatile uint32_t div;
} UART_t;

#define UART0  ((UART_t *) UART0_BASE)

// Send one character
void uart_send(char c) {
    // Bit 31 of txdata = full flag; wait until not full
    while (UART0->txdata & (1u << 31))
        ;
    UART0->txdata = (uint32_t)c;
}
```

## Why `volatile` Is Non-Negotiable

Without `volatile`, the compiler is allowed to assume that memory does not change between reads unless the program writes to it. A polling loop like:

```c
while (UART0->txdata & (1u << 31))
    ; // wait for TX buffer to empty
```

could be "optimized" to read `txdata` once, cache the result, and loop forever (or not at all) because the compiler sees no write to that address in the loop body. `volatile` forces a fresh load on every iteration.

## The Role of the MMU

On systems with virtual memory, the OS maps physical MMIO regions into kernel virtual address space with special page table attributes:

- **Non-cacheable** — Reads must go all the way to the device; stale cache lines must never be returned.
- **Strongly-ordered** — Accesses must not be reordered by the memory subsystem.
- **Non-executable** — Code should never run from device memory.

In Linux, `ioremap()` performs this mapping:

```c
void __iomem *base = ioremap(0x10013000, 0x1000);
uint32_t val = readl(base + UART_TXDATA);  // safe accessor
iounmap(base);
```

## Memory Barriers and Fences

On architectures with relaxed memory ordering (including RISC-V with its RVWMO model), stores to different MMIO registers may arrive at the device out of order. Use a fence to enforce ordering:

```asm
# RISC-V: ensure prior stores to device are visible before proceeding
fence ow, ow   # order: output (store) → output (store)
```

In C with GCC:

```c
// Ensure all prior writes reach the device before the next write
__sync_synchronize();
```

## MMIO vs RAM: Summary of Differences

| Property | RAM | MMIO |
|---|---|---|
| Caching | Cached (write-back or write-through) | Non-cacheable |
| Access semantics | Load returns last stored value | Side effects possible (e.g., clears an interrupt) |
| Volatile required | No (usually) | Yes, always |
| Prefetch allowed | Yes | No |
| Address space | Shared with devices | Shared with RAM |

## Common Pitfalls

- **Reading a status register clears it** — Some interrupt-pending registers auto-clear on read. Reading them twice gives different results.
- **Wrong access width** — Accessing a 32-bit register with a byte load may return garbage or be a no-op depending on the peripheral.
- **Unaligned access** — MMIO registers almost always require natural alignment.

> **Interview answer:** Memory-mapped I/O places device registers at specific physical addresses so the CPU can read/write them with ordinary load/store instructions. Registers must be accessed through `volatile` pointers to prevent compiler optimizations from caching device state, and the memory region must be mapped as non-cacheable to prevent hardware caches from interfering.
