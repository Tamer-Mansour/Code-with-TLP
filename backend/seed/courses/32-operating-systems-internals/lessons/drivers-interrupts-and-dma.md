# How Drivers Use Interrupts and DMA

Two mechanisms make high-performance device I/O possible without burning CPU cycles in busy loops: **interrupts** let the hardware signal the CPU when it needs attention, and **DMA** lets the hardware move data directly to/from memory without CPU involvement.

## Interrupts in a Driver

### Requesting an IRQ

A driver registers an interrupt handler with `request_irq()`:

```c
int err = request_irq(dev->irq,          /* IRQ line number    */
                      my_irq_handler,    /* handler function   */
                      IRQF_SHARED,       /* flags              */
                      "my_driver",       /* name in /proc/interrupts */
                      dev);             /* cookie passed back */
if (err) {
    dev_err(&pdev->dev, "Cannot claim IRQ %d\n", dev->irq);
    return err;
}
```

### The Interrupt Handler

Interrupt handlers run with interrupts **disabled** on the current CPU. They must be short and must **never sleep**.

```c
static irqreturn_t my_irq_handler(int irq, void *data)
{
    struct my_dev *dev = data;
    u32 status = readl(dev->base + REG_STATUS);

    if (!(status & IRQ_PENDING))
        return IRQ_NONE;   /* shared IRQ, not ours */

    /* Acknowledge the interrupt */
    writel(status, dev->base + REG_STATUS);

    /* Defer heavy work to a tasklet or workqueue */
    tasklet_schedule(&dev->tasklet);

    return IRQ_HANDLED;
}
```

### Top Half vs Bottom Half

| Aspect | Top Half (ISR) | Bottom Half (tasklet / workqueue) |
|---|---|---|
| Runs in | Interrupt context | Softirq / process context |
| Can sleep? | No | Workqueue: yes; tasklet: no |
| Latency | Immediate | Deferred |
| Purpose | Acknowledge HW, schedule deferred work | Process data, wake up waiters |

The split keeps interrupt latency low while allowing complex processing later.

## Direct Memory Access (DMA)

### Why DMA?

Without DMA, the CPU copies every byte between a kernel buffer and the device FIFO — wasting cycles proportional to transfer size. DMA engines are dedicated hardware that perform this copy autonomously, signaling completion via an interrupt.

### The DMA API

```c
/* Allocate a coherent (cache-safe) DMA buffer */
dma_addr_t dma_handle;
void *kbuf = dma_alloc_coherent(&pdev->dev, BUF_SIZE,
                                 &dma_handle, GFP_KERNEL);
/* dma_handle is the physical bus address given to the device */

/* Program the device DMA registers */
writel(lower_32_bits(dma_handle), dev->base + REG_DMA_ADDR_LO);
writel(upper_32_bits(dma_handle), dev->base + REG_DMA_ADDR_HI);
writel(BUF_SIZE,                  dev->base + REG_DMA_LEN);
writel(CMD_DMA_START,             dev->base + REG_CMD);

/* Later, in IRQ handler: DMA complete, data is in kbuf */
```

### Coherent vs Streaming DMA

| Type | Use case | Cache handling |
|---|---|---|
| Coherent (`dma_alloc_coherent`) | Long-lived buffers (descriptor rings) | Always cache-safe |
| Streaming (`dma_map_single`) | One-shot transfers of existing buffers | Must sync with `dma_sync_*` |

```c
/* Streaming: map an existing kernel buffer for DMA */
dma_addr_t dma_handle = dma_map_single(&pdev->dev, kbuf,
                                        size, DMA_FROM_DEVICE);
if (dma_mapping_error(&pdev->dev, dma_handle))
    return -ENOMEM;

/* ... start DMA ... wait for IRQ ... */

/* Unmap before CPU accesses the buffer */
dma_unmap_single(&pdev->dev, dma_handle, size, DMA_FROM_DEVICE);
```

### IOMMU

On modern systems an IOMMU sits between the bus and RAM. The device sees *IOVA* (I/O Virtual Addresses), not physical addresses. The kernel's DMA API handles this transparently — another reason never to program physical addresses directly.

## Worked Flow: NIC Receive

```
1. Driver posts RX descriptors pointing to DMA buffers.
2. NIC receives packet, DMAs payload into buffer, writes descriptor.
3. NIC raises interrupt.
4. ISR (top half): clears interrupt, schedules NAPI poll.
5. NAPI poll (bottom half): reads descriptors, hands skbs to network stack.
6. Driver reposts empty descriptors for next packets.
```

## Common Pitfalls

- **Freeing DMA buffers before unmap** — causes IOMMU faults and silent data corruption.
- **Sleeping in an ISR** — results in kernel panic (`BUG: scheduling while atomic`).
- **Forgetting `free_irq()`** on module unload — the IRQ remains registered and the handler dereferences freed memory on the next interrupt.
- **Cache coherency on ARM** — without `dma_sync_for_cpu`, the CPU may read stale cache lines after a DMA write.

## Interview Answer

> **Q: Why split interrupt handling into a top half and a bottom half?**
>
> **Interview answer:** The top half runs with interrupts disabled and must be as short as possible to maintain system responsiveness; it acknowledges the hardware and schedules a bottom half (tasklet or workqueue) that runs with interrupts re-enabled and can do heavier, potentially sleeping, work.
