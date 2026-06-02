# The DMA Transfer Flow and Completion Interrupt

Understanding the precise sequence of a DMA transfer — from driver setup to interrupt handler — is what separates candidates who have read about DMA from those who have written drivers. Walk through each step carefully.

## The Complete Flow (Device-to-Memory Example: Disk Read)

### Step 1 — Driver Allocates a Buffer

The driver allocates a physically contiguous (or IOMMU-mapped) buffer and pins it in memory so the OS won't page it out during the transfer.

```c
dma_addr_t bus_addr;
void *buf = dma_alloc_coherent(dev, SECTOR_SIZE, &bus_addr, GFP_KERNEL);
```

### Step 2 — Driver Programs the DMA Engine

The driver writes the bus address, transfer length, and direction into the device's MMIO registers (or a descriptor in memory).

```c
writel((uint32_t) bus_addr,         mmio + REG_DMA_ADDR_LO);
writel((uint32_t)(bus_addr >> 32),  mmio + REG_DMA_ADDR_HI);
writel(SECTOR_SIZE,                 mmio + REG_DMA_LEN);
writel(CMD_READ | CMD_IRQ_ENABLE,   mmio + REG_CMD);   // kick off + enable IRQ
```

A **write memory barrier** (`wmb()`) before the command write ensures the address and length registers are visible to the device before it sees the start command.

### Step 3 — Device Performs the Transfer

The device's DMA engine independently issues bus-master read/write transactions:

```
NIC/Disk DMA engine  --[bus write]--> RAM[bus_addr .. bus_addr + len]
```

The CPU is free to run other threads. No CPU cycles are consumed by the data movement itself.

### Step 4 — Device Raises an Interrupt

When the last byte is transferred, the device asserts its interrupt line. The CPU's interrupt controller (APIC on x86, GIC on ARM) arbitrates and delivers the interrupt to a CPU.

### Step 5 — CPU Executes the ISR

The processor saves the current register state, looks up the Interrupt Descriptor Table (IDT on x86) or interrupt vector table, and branches to the **Interrupt Service Routine (ISR)**.

```c
// Simplified ISR (runs in interrupt context — no sleeping!)
irqreturn_t my_dma_isr(int irq, void *dev_id) {
    struct my_device *dev = dev_id;
    uint32_t status = readl(dev->mmio + REG_STATUS);

    if (!(status & STATUS_DMA_DONE))
        return IRQ_NONE;   // not our interrupt

    // Acknowledge to device (clear interrupt flag)
    writel(STATUS_DMA_DONE, dev->mmio + REG_STATUS_CLR);

    // Invalidate CPU caches if not coherent DMA
    dma_sync_single_for_cpu(dev->dma_dev, dev->bus_addr,
                            dev->xfer_len, DMA_FROM_DEVICE);

    // Wake up waiting thread
    complete(&dev->dma_done);
    return IRQ_HANDLED;
}
```

### Step 6 — Driver Processes the Data

The thread that submitted the request (blocked on `wait_for_completion`) wakes up and processes the data now sitting in `buf`.

## Timeline Visualization

```
Time --->

CPU:     [setup desc] [issue cmd] [other work ....] [ISR] [process data]
Bus:                              [DMA write burst ...]
Device:                [read cmd] [transfer ........] [assert IRQ]
```

The CPU's "other work" window is the efficiency gain DMA provides.

## Interrupt Coalescing

High-throughput devices (NICs at 100 Gbps) can generate millions of interrupts per second if every DMA transfer raises one. **Interrupt coalescing** (also called *interrupt moderation*) batches completions:

- The device waits until N transfers complete **or** T microseconds elapse, then raises a single interrupt.
- The ISR walks the descriptor ring and processes all completed entries at once.
- Reduces ISR overhead at the cost of slightly increased latency for individual transfers.

Linux `ethtool -C` configures coalescing parameters for NICs.

## Common Bugs

- **Not issuing `wmb()` before the command write:** the device sees the start command before the address register, causing a corrupt transfer or bus error.
- **Not calling `dma_sync_single_for_cpu()` after a non-coherent transfer:** CPU reads stale cache lines instead of the newly DMA'd data.
- **Double-freeing the DMA buffer before the transfer completes:** if the buffer is recycled while the device is still writing to it, memory corruption follows.
- **Forgetting to acknowledge the interrupt in the ISR:** the interrupt line stays asserted, the CPU loops in the ISR forever (interrupt storm).

> **Interview answer:** A DMA transfer has six stages: allocate a pinned buffer, program the device with the bus address and length, let the device transfer data autonomously over the bus, receive a completion interrupt, run the ISR to acknowledge and sync caches, then process the result. The CPU is idle during the actual data movement.
