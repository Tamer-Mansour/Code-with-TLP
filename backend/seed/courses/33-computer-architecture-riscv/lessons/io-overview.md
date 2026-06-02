# How the CPU Communicates with Devices

Modern computers are far more than just processors and memory. A CPU must talk to keyboards, displays, network cards, storage controllers, and dozens of other peripherals. Understanding how that communication works is fundamental to systems programming, embedded development, and writing performant device drivers.

## The I/O Problem

The CPU operates on data in registers and memory. Peripherals operate on signals, buffers, and hardware state. Bridging that gap requires a well-defined interface — a way for software to tell hardware what to do and for hardware to signal back when something happens.

There are two classical approaches:

| Approach | Mechanism | Common On |
|---|---|---|
| Memory-Mapped I/O (MMIO) | Device registers appear as regular memory addresses | ARM, RISC-V, x86 (PCI) |
| Port-Mapped I/O (PMIO) | Separate `IN`/`OUT` instructions with a dedicated I/O address space | x86 legacy devices |

Both approaches map device control registers to some addressable location. The difference is *which* address space that is.

## Device Registers

Every peripheral exposes a small set of registers:

- **Control register** — software writes here to configure or command the device.
- **Status register** — hardware writes here; software reads it to know if the device is ready, busy, or has errored.
- **Data register** — the actual payload, e.g., one byte of UART serial data.

Think of a UART (serial port) as a concrete example:

```c
// Hypothetical MMIO UART at base address 0x10000000
#define UART_BASE   0x10000000UL
#define UART_DATA   (*(volatile uint8_t *)(UART_BASE + 0x00))
#define UART_STATUS (*(volatile uint8_t *)(UART_BASE + 0x04))
#define UART_TXREADY  (1 << 0)

void uart_putc(char c) {
    while (!(UART_STATUS & UART_TXREADY))
        ; // spin until transmitter is ready
    UART_DATA = c;
}
```

Notice `volatile` — this prevents the compiler from caching the read in a register across loop iterations.

## Three I/O Transfer Strategies

How does the CPU know when data is ready or when the device needs attention?

1. **Programmed I/O / Polling** — The CPU repeatedly reads the status register in a tight loop. Simple but wastes cycles.
2. **Interrupt-Driven I/O** — The device raises an interrupt line when it needs service; the CPU finishes its current instruction and jumps to an interrupt handler. CPU is free to do real work between I/O events.
3. **Direct Memory Access (DMA)** — A dedicated DMA controller transfers a whole block of data between device and RAM without per-byte CPU involvement. The CPU just programs the DMA and gets a single interrupt when the entire transfer is done.

## Why This Matters for RISC-V

RISC-V has no privileged I/O instructions — all I/O is memory-mapped. The platform specification (e.g., SiFive boards) defines a physical address map such as:

```
0x02000000  CLINT (timer/software interrupts)
0x0C000000  PLIC  (Platform-Level Interrupt Controller)
0x10000000  UART0
0x10001000  UART1
```

Bare-metal RISC-V programs simply load/store to those addresses; the Memory Management Unit (MMU) or physical address decoding routes the transaction to the correct peripheral.

## Common Pitfalls

- **Forgetting `volatile`** — The compiler may optimize away repeated reads of a status register, causing your polling loop to never see the device become ready.
- **Byte ordering** — Device registers often have a fixed endianness; mismatching with the CPU causes silent data corruption.
- **Address alignment** — Many device registers require natural alignment (a 32-bit register must be accessed at a 4-byte-aligned address).
- **Missing memory barriers** — On weakly-ordered architectures, stores to device registers may reorder relative to each other; use `fence` (RISC-V) or `dmb` (ARM) where required.

> **Interview answer:** The CPU communicates with devices either through memory-mapped I/O (device registers appear as ordinary memory addresses, accessed with normal load/store instructions) or port-mapped I/O (a separate address space accessed with special IN/OUT instructions). RISC-V uses exclusively memory-mapped I/O.
