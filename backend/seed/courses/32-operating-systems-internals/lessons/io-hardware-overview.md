# I/O Hardware: Controllers, Ports, and Registers

Every peripheral — disk, NIC, GPU, keyboard — connects to the CPU through a chain of hardware abstractions. Understanding that chain is foundational for OS and embedded development interviews.

## The Three-Layer View

```
CPU  <-->  Bus  <-->  I/O Controller  <-->  Device
```

The **CPU** issues read/write commands. The **bus** (PCIe, USB, SATA) carries those signals. The **I/O controller** translates bus transactions into the device's native protocol. The **device** performs the physical work (spinning a platter, transmitting a packet, lighting a pixel).

## I/O Controllers

An I/O controller is a purpose-built chip (or FPGA) that sits between the bus and the device. It exposes a small set of **registers** to the CPU:

| Register Type | Purpose |
|---|---|
| **Data register** | Holds bytes to write to or read from the device |
| **Status register** | Reports device state (busy, error, ready, etc.) |
| **Control register** | Accepts commands (start, reset, interrupt enable) |
| **Address register** | Specifies where in device memory to operate |

These registers are the only "knobs" the CPU has. All driver code ultimately boils down to reading and writing them.

## Ports vs. Addresses — A Preview

Registers are exposed to the CPU in one of two ways:

- **Port-mapped I/O (PMIO):** registers live in a separate I/O address space; CPU uses special `IN`/`OUT` instructions.
- **Memory-mapped I/O (MMIO):** registers appear as ordinary physical addresses; CPU uses normal `LD`/`ST` instructions.

The next two lessons cover each approach in depth.

## Polling vs. Interrupt-Driven I/O

Once the driver writes a command to the control register, the device starts working. The CPU then has two options:

**Polling (busy-wait):** the CPU loops, repeatedly reading the status register until the "done" bit is set. Simple but wastes CPU cycles.

```c
// Polling loop example
volatile uint32_t *status_reg = (uint32_t *)0xFEA00004;
while ((*status_reg & STATUS_DONE) == 0)
    ; // spin
```

**Interrupt-driven:** the CPU issues the command and continues other work. When the device finishes, it asserts an interrupt line; the CPU saves state and jumps to the interrupt service routine (ISR).

Most production drivers use interrupts (or DMA + interrupt) for throughput, and polling only for very short expected wait times (< a few microseconds).

## The Role of the Bus

Modern systems use **PCIe** as the primary peripheral bus. PCIe is a packet-switched, full-duplex, point-to-point serial fabric. Legacy ISA/PCI buses were shared; PCIe lanes are not. The PCIe **root complex** (part of the CPU die or chipset) bridges the processor's memory fabric to the PCIe hierarchy.

Legacy x86 systems also have the **LPC** (Low Pin Count) bus for slow peripherals like the real-time clock and TPM, and the **SMBus** for power management ICs.

## Common Pitfall: Forgetting `volatile`

Device registers can change asynchronously. Without `volatile`, a compiler may cache a register read in a CPU register, breaking the polling loop above. Always declare device-register pointers as `volatile uint32_t *`.

## Worked Example: Reading a UART Status Register

A 16550 UART exposes its Line Status Register (LSR) at offset 5 from its base address. Bit 0 ("Data Ready") is set when a received byte is waiting.

```c
#define UART_BASE   0x3F8          // COM1 base port (x86 port-mapped)
#define UART_LSR    (UART_BASE + 5)

static inline int uart_data_ready(void) {
    return inb(UART_LSR) & 0x01;  // bit 0 = DR
}
```

The same logic applies to MMIO UARTs (common on ARM SoCs) — only the access mechanism changes.

> **Interview answer:** An I/O controller exposes a small set of data, status, and control registers to the CPU. The CPU driver reads and writes these registers — either via dedicated I/O port instructions or via memory-mapped addresses — to command the device and observe its state.
