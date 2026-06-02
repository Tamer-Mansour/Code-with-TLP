# Memory-Mapped I/O in RISC-V

Memory-Mapped I/O (MMIO) is the dominant I/O mechanism in RISC-V systems. Unlike x86, which provides dedicated `IN`/`OUT` port instructions, RISC-V uses ordinary load and store instructions to communicate with hardware peripherals. The hardware decodes the address bus and routes transactions to the appropriate device register instead of DRAM.

## Why MMIO?

- **ISA simplicity.** No special I/O instructions are needed; `LB`, `LH`, `LW`, `LD`, `SB`, `SH`, `SW`, `SD` all work.
- **Uniform access model.** Pointers to device registers look exactly like pointers to memory — critical for C drivers.
- **Cache coherency.** Devices appear in the same address space, so the same protection and virtual-memory mechanisms apply.

## How It Works

The physical address space is partitioned between DRAM and MMIO regions. When a store or load reaches the memory bus with a MMIO address, a hardware interconnect (crossbar or AXI bus fabric) routes the transaction to the peripheral rather than DRAM.

```
CPU  ──load/store──►  Bus Fabric  ──► DRAM       (if addr in RAM range)
                                  ──► UART regs  (if addr = 0x1000_0000)
                                  ──► GPIO regs  (if addr = 0x1001_0000)
```

## Volatile and Ordering

Two critical rules for MMIO in C:

1. **Use `volatile`** so the compiler never caches a device-register read in a CPU register or eliminates a "redundant" write.
2. **Use `fence` instructions** to prevent the CPU's out-of-order engine from reordering MMIO accesses with respect to each other or to regular memory.

```c
// Correct MMIO read in C
#define UART_BASE 0x10000000UL

volatile uint8_t *uart_dr = (volatile uint8_t *)UART_BASE;

// Write a byte to the transmit data register
*uart_dr = 'A';

// fence ensures the store completes before any subsequent MMIO read
asm volatile("fence o,i" ::: "memory");
```

## RISC-V Fence Variants

| Instruction | Meaning |
|---|---|
| `fence` | Full fence — all preceding memory ops complete before any subsequent ops |
| `fence r,r` | Load-load ordering only |
| `fence w,w` | Store-store ordering only |
| `fence.i` | Instruction-fetch fence (synchronize instruction cache with data writes) |

For device drivers the common idiom is `fence` (no modifiers) or `fence io,io`, which covers all I/O read/write ordering needs.

## Platform-Level Interrupt Controller (PLIC)

MMIO is also how the OS programs interrupt controllers. The PLIC lives at a fixed MMIO base address (e.g., `0x0C00_0000` on QEMU virt). Software enables interrupts, sets priorities, and claims/completes interrupts purely via loads and stores to PLIC registers.

```c
#define PLIC_BASE      0x0C000000UL
#define PLIC_PRIORITY  (PLIC_BASE + 0x000000)
#define PLIC_ENABLE    (PLIC_BASE + 0x002000)
#define PLIC_CLAIM     (PLIC_BASE + 0x200004)

// Enable UART interrupt (source 10) for hart 0
volatile uint32_t *en = (volatile uint32_t *)PLIC_ENABLE;
*en |= (1u << 10);
```

## Common Pitfalls

- **Forgetting `volatile`.** The compiler may optimize away repeated reads of a status register, causing infinite waits.
- **Missing `fence`.** Without ordering, a store to a "start DMA" register might reach the device after the CPU has already checked the "DMA done" flag.
- **Wrong access width.** Many device registers require exactly 32-bit or 8-bit accesses; a 16-bit load to a 32-bit register can produce undefined behavior.

## Interview Answer

> "RISC-V uses ordinary load/store instructions to access device registers — this is MMIO. Pointers to MMIO addresses must be `volatile` to prevent compiler optimization, and `fence` instructions must bracket accesses to preserve ordering in the out-of-order CPU pipeline."
