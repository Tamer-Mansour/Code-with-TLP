# Memory-Mapped I/O Deep Dive

MMIO is the dominant I/O paradigm on all modern platforms. This lesson goes below the surface: how physical addresses reach device registers, how the OS manages those mappings, and what happens if you get it wrong.

## How MMIO Addresses Are Assigned

At boot, firmware (UEFI/BIOS) surveys all PCIe devices, reads their **Base Address Registers (BARs)**, and assigns non-overlapping physical address ranges. The OS inherits this layout, records it in the firmware resource tables (ACPI `_CRS`, device tree `reg` properties, or `/proc/iomem` on Linux).

A simplified PCIe BAR setup flow:

```
1. Firmware writes 0xFFFFFFFF to BAR → device reports required size.
2. Firmware writes the allocated base address to BAR.
3. Device registers now appear at [base, base + size).
4. OS calls ioremap(base, size) to create a virtual mapping.
```

## ioremap and Virtual Addresses

User processes operate on virtual addresses; the kernel does too. After the OS knows the physical base of a device's registers, it calls `ioremap()` to create a kernel virtual mapping:

```c
// Linux kernel driver snippet
#define MY_DEV_BAR0_PHYS  0xF0000000UL
#define MY_DEV_BAR0_SIZE  0x1000        // 4 KB

void __iomem *base;

base = ioremap(MY_DEV_BAR0_PHYS, MY_DEV_BAR0_SIZE);
if (!base)
    return -ENOMEM;

// Now read a 32-bit status register at offset 0x10
uint32_t status = readl(base + 0x10);

// Write a command register at offset 0x04
writel(0x00000001, base + 0x04);

iounmap(base);
```

`readl` / `writel` (and `readb`, `readw`, `writeb`, `writew`) are the correct Linux accessors. They:
- Issue the right-width bus transaction.
- Include any necessary memory barriers for the architecture.
- Work portably across x86 and ARM without sprinkling `volatile` everywhere manually.

## Memory Attributes and Caching

The MMU page table entry for an MMIO region must have the **right memory type**. On ARM, the options most relevant to MMIO are:

| Memory Type | Caching | Reordering | Use case |
|---|---|---|---|
| Normal Cacheable | Yes | Yes | RAM |
| Normal Non-cacheable | No | Permitted | Rare |
| Device-nGnRnE | No | Strictly ordered | High-risk device regs |
| Device-nGnRE | No | Gather+reorder allowed | Most peripheral regs |

On x86, the MTRR (Memory Type Range Register) or PAT (Page Attribute Table) marks the physical range as **UC** (uncacheable) or **WC** (write-combining, for framebuffers).

Linux `ioremap()` applies the correct defaults; drivers should not bypass it.

## Write Combining — A Practical Optimization

For **framebuffers and descriptor rings**, write-combining (WC) allows the CPU to batch multiple small writes into larger bus transactions, dramatically improving throughput. The CPU may reorder and merge writes within a WC region.

```c
// Mark a framebuffer region as write-combining
base = ioremap_wc(fb_phys, fb_size);

// Flush combined writes before signalling the GPU
wmb();  // write memory barrier
writel(RENDER_START, mmio_base + GPU_CMD_REG);
```

Never use WC on control/status registers — reordering can cause incorrect device behavior.

## Barriers and Ordering

Modern CPUs and buses can reorder memory transactions. For device registers, ordering matters: you must not post a "start DMA" command before writing the descriptor address.

```c
writel(desc_phys_addr, base + DESC_ADDR_REG);
wmb();                          // ensure the address is visible before the command
writel(DMA_START, base + CMD_REG);
```

- `rmb()` — read memory barrier (ensure prior reads complete before subsequent reads).
- `wmb()` — write memory barrier (ensure prior writes are observed before subsequent writes).
- `mb()` — full barrier (both reads and writes).

On x86, the strong memory model means `wmb()` compiles to nothing (a compile barrier only); on ARM it emits a `DSB ST` or `DMB OSHST` instruction.

## Common Bugs

- **Forgetting `volatile` (or using raw pointers instead of `readl`/`writel`):** the compiler elides "redundant" register reads.
- **Caching an MMIO region as Normal:** stale cached values masquerade as real device state.
- **Missing write barrier before a trigger register:** the command arrives before the descriptor address, corrupting DMA.
- **Using the wrong access width:** many devices require 32-bit accesses only; a byte access may trigger a bus fault or be ignored.

> **Interview answer:** MMIO maps device control registers into the physical address space. The OS uses `ioremap()` to create a kernel virtual mapping with the correct non-cacheable memory attributes, then uses barrier-aware accessors (`readl`/`writel`) to safely read and write registers. The key pitfalls are caching and memory ordering.
