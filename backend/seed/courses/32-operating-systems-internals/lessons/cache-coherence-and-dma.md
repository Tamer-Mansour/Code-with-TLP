# Cache Coherence Problems With DMA

DMA is fast, but it introduces a subtle class of bugs: the CPU's caches may hold stale or dirty data that conflicts with what the DMA engine writes or reads. Getting this right is one of the harder parts of driver development.

## The Stale-Read Problem (Device Writes, CPU Reads)

Scenario: a NIC receives a packet and DMA-writes it to a RAM buffer. The CPU then reads the buffer.

```
RAM[0x1000..0x1400]: NIC wrote fresh packet data
CPU cache line covering 0x1000: still holds old (stale) data from a previous read
```

If the CPU's cache is not invalidated before the driver reads the buffer, the driver sees the old data — a silent, catastrophic bug.

**Fix:** after DMA-from-device completes, **invalidate** the relevant cache lines so the CPU is forced to re-fetch from RAM.

```c
// Linux non-coherent DMA path
dma_sync_single_for_cpu(dev, bus_addr, len, DMA_FROM_DEVICE);
// Now the CPU can safely read buf[]
```

## The Dirty-Write Problem (CPU Writes, Device Reads)

Scenario: the CPU builds a transmit packet in a buffer. The NIC's DMA engine then reads it.

```
CPU writes to TX buf[0..1500] → data sits in CPU cache, not yet in RAM
NIC DMA reads from RAM[bus_addr..bus_addr+1500] → reads stale zeros
```

If the CPU's dirty cache lines are not flushed to RAM before the NIC starts reading, the NIC transmits garbage.

**Fix:** before handing the buffer to the device, **flush (clean)** the cache lines to RAM.

```c
// Linux non-coherent DMA path
dma_sync_single_for_device(dev, bus_addr, len, DMA_TO_DEVICE);
writel(CMD_TX_START, mmio + REG_CMD);  // now safe to start NIC
```

## Coherent vs. Non-Coherent DMA

| Mode | Cache handling | Typical use |
|---|---|---|
| **Coherent (consistent)** | Hardware keeps caches in sync automatically | Descriptor rings, control structures |
| **Non-coherent (streaming)** | Software must flush/invalidate explicitly | Large data buffers (RX/TX payloads) |

`dma_alloc_coherent()` returns a buffer that is coherent — either uncacheable memory, or a region maintained by a hardware cache-coherence interconnect (e.g., ARM CCI-550, Intel QPI). Accesses to it are always correct, but potentially slower than cached RAM.

`dma_map_single()` / `dma_unmap_single()` set up a streaming (non-coherent) mapping. The driver must call the appropriate sync functions around CPU or device accesses:

```c
// Map a pre-allocated buffer for device-to-CPU (RX)
bus_addr = dma_map_single(dev, cpu_buf, len, DMA_FROM_DEVICE);

// ... device fills buffer via DMA ...

// Before CPU reads: invalidate cache
dma_sync_single_for_cpu(dev, bus_addr, len, DMA_FROM_DEVICE);
process_data(cpu_buf);

// If reusing: sync back to device before next DMA
dma_sync_single_for_device(dev, bus_addr, len, DMA_FROM_DEVICE);

// When done: unmap
dma_unmap_single(dev, bus_addr, len, DMA_FROM_DEVICE);
```

## The Bouncing Problem and Bounce Buffers

Some 32-bit DMA engines cannot address RAM above 4 GB (`DMA_BIT_MASK(32)`). On a system with 16 GB of RAM, a buffer allocated with `GFP_KERNEL` might land in high memory.

The kernel allocates a **bounce buffer** in the low 4 GB zone, copies data to/from it on behalf of the driver:

```
High RAM buffer (CPU view) <--> [kernel copy] <--> Low RAM bounce buffer <--> Device DMA
```

Bounce buffers hurt performance significantly. Drivers should declare their DMA mask correctly:

```c
if (dma_set_mask_and_coherent(dev, DMA_BIT_MASK(64)))
    dev_warn(dev, "64-bit DMA not available; falling back to 32-bit\n");
```

## IOMMU and Cache Coherence

When an IOMMU is present, IOVAs map to physical pages. The IOMMU does not solve cache coherence — the CPU caches are still indexed by physical address, and if the CPU has dirty data for that physical page, the device will read stale bytes. The IOMMU enforces access control, not cache synchronization.

## Coherence on x86 vs. ARM

- **x86**: The MESI cache protocol propagates writes to any bus master including PCIe devices (via the root complex snoop filter). Most x86 systems support **hardware coherence** for PCIe DMA, making explicit cache flushes unnecessary. `dma_alloc_coherent` still marks memory uncacheable by default for correctness and portability.
- **ARM (non-coherent)**: Many ARM SoCs do not wire the I/O coherency fabric to all peripherals. DMA regions are typically uncacheable or require explicit `DCCIVAC` (Data Cache Clean and Invalidate by VA) instructions. The Linux DMA API handles this if used correctly.

## Summary of Rules

1. Use `dma_alloc_coherent` for shared control structures (descriptors, rings).
2. Use `dma_map_single` / `dma_map_sg` for large data buffers; always call sync functions.
3. Never access a buffer with the CPU while the device has DMA ownership.
4. Always `dma_unmap_*` before freeing the buffer.

> **Interview answer:** DMA bypasses the CPU cache, so if the CPU has dirty cached lines the device reads stale data (flush needed), or if the device writes and the CPU has stale lines the CPU reads old data (invalidate needed). The Linux DMA API's `dma_sync_single_for_cpu/device` functions issue the required cache operations, while `dma_alloc_coherent` avoids the problem by using uncacheable or hardware-coherent memory.
