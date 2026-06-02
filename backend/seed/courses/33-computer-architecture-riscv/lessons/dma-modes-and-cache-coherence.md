# DMA Modes and Cache Coherence Concerns

DMA is powerful, but it introduces one of the trickiest correctness problems in systems programming: **cache coherence**. Because the DMA controller bypasses the CPU's cache hierarchy and writes directly to physical RAM, the CPU's caches may hold stale data after a DMA fill — or the DMAC may read stale data before a DMA drain.

## The Cache Coherence Problem

Modern CPUs use write-back caches. A write from the CPU updates the cache line and marks it dirty; the update reaches RAM lazily. Meanwhile, the DMAC reads and writes physical RAM directly:

```
Scenario 1: DMA write (device → RAM), CPU reads stale cache

  CPU writes to buf[0..511] → values go into L1 cache (dirty)
  CPU programs DMAC to read buf → DMAC reads OLD values from RAM (cache not flushed!)
  NIC transmits wrong data.

Scenario 2: CPU reads after DMA fill

  DMAC fills buf[0..511] in RAM with fresh data from NIC.
  CPU reads buf[0] → L1 hit — returns STALE old value (cache not invalidated!)
  Application processes wrong data.
```

## The Four Operations

Correct DMA usage requires four well-defined cache maintenance operations:

| Operation | Direction | Cache Action Before DMA | Cache Action After DMA |
|---|---|---|---|
| **DMA write** (device → RAM) | Inbound | Invalidate cache lines covering the buffer | (none needed) |
| **DMA read** (RAM → device) | Outbound | Flush (write-back) dirty cache lines to RAM | (none needed) |

More precisely:

- **Before DMA write (device → RAM):** Invalidate the buffer's cache lines so the CPU will re-read from RAM after the transfer. Do NOT flush first — any dirty CPU data in that range would corrupt the incoming DMA data.
- **Before DMA read (RAM → device):** Flush dirty cache lines so the DMAC reads the CPU's latest values from RAM.

In Linux kernel drivers:

```c
#include <linux/dma-mapping.h>

// Allocate a DMA-coherent buffer (always coherent, no explicit maintenance needed)
void *buf = dma_alloc_coherent(dev, 4096, &dma_addr, GFP_KERNEL);

// ---- OR use streaming mappings (more common for I/O buffers) ----

// Before DMAC reads from this buffer (RAM → device)
dma_sync_single_for_device(dev, dma_handle, size, DMA_TO_DEVICE);

// After DMAC writes into this buffer (device → RAM), before CPU reads
dma_sync_single_for_cpu(dev, dma_handle, size, DMA_FROM_DEVICE);
```

## Hardware Solutions: IOMMU and Cache-Coherent DMA

Many modern SoCs include hardware that makes DMA transparent to software:

### IOMMU (Input-Output Memory Management Unit)

An IOMMU sits between the DMAC and the memory bus. It provides:
- **Address translation** — The DMAC uses virtual (I/O virtual) addresses; the IOMMU translates to physical addresses. Isolates devices from each other (security).
- **Protection** — Prevents a rogue or buggy DMA engine from writing to arbitrary RAM.
- **Not cache coherence** — The IOMMU does not automatically keep caches coherent.

### Hardware Cache-Coherent Interconnects

ARM's CCI (Cache Coherent Interconnect) and ACE (AXI Coherency Extensions) allow DMA masters to participate in the cache coherence protocol. Transfers to/from a coherent DMAC automatically snoop CPU caches, making software cache maintenance unnecessary. This is the model on high-end ARM SoCs (e.g., Apple Silicon, Qualcomm Snapdragon).

RISC-V platforms using TileLink or CHI interconnects can also achieve hardware coherence, though simpler RISC-V boards (e.g., SiFive HiFive) require explicit software cache flushing.

## DMA Transfer Modes Recap

The three bus arbitration modes interact with cache coherence:

| Mode | How DMAC Shares the Bus | Cache Coherence Impact |
|---|---|---|
| **Burst** | Holds bus for full transfer | CPU cannot snoop bus; software maintenance required |
| **Cycle Stealing** | Steals one bus cycle at a time | Partial visibility; still requires software maintenance on non-coherent systems |
| **Transparent** | Only runs when CPU bus is idle | CPU unaffected but slower DMA throughput |

## Worked Example: Receiving a Network Packet (Non-Coherent System)

```c
#define PACKET_BUF_SIZE 1518
static uint8_t rx_packet[PACKET_BUF_SIZE] __attribute__((aligned(64)));

void start_nic_rx_dma(void) {
    // 1. Invalidate cache lines covering rx_packet
    //    so stale CPU data doesn't pollute incoming DMA data
    dcache_invalidate_range((uintptr_t)rx_packet, PACKET_BUF_SIZE);

    // 2. Program DMAC
    DMAC_DST   = (uint32_t)(uintptr_t)rx_packet;
    DMAC_SRC   = NIC_RX_FIFO_ADDR;
    DMAC_COUNT = PACKET_BUF_SIZE;
    DMAC_CTRL  = DMAC_CTRL_START | DMAC_CTRL_IRQ_EN;
}

void dma_done_isr(void) {
    // DMA has filled rx_packet in RAM.
    // Cache lines are (hopefully) already invalid.
    // Now it is safe to hand the buffer to the network stack.
    DMAC_STATUS = 1;           // acknowledge interrupt
    network_stack_rx(rx_packet, PACKET_BUF_SIZE);
}
```

If you forget step 1 and some cache lines covering `rx_packet` happen to be dirty, the invalidate at the start would discard those dirty lines without writing them back — which is correct here (we want clean lines so the DMA data is visible). If instead those dirty lines existed because you had other important data there, you would have a bug; always use a dedicated, purpose-specific DMA buffer.

## Double Buffering

High-throughput drivers use two (or more) buffers so the DMAC can fill one while the CPU processes the other:

```
  Buffer A: CPU processing (read only, safe)
  Buffer B: DMAC filling (write only by DMAC)
  On DMA completion: swap roles of A and B
```

This eliminates the DMA/CPU contention window.

## Common Pitfalls

- **Invalidating without flushing dirty lines first** — If the CPU wrote to part of the DMA buffer and those lines are dirty, invalidating discards the writes. Use flush before DMA-out, invalidate before DMA-in.
- **Buffer on the stack** — Stack frames are reused; a stale cache line from a previous call can make its way into a "new" DMA buffer. Use static or heap allocation with proper alignment.
- **Partial cache line overlap** — If the DMA buffer does not start/end on a cache-line boundary, invalidating it will also invalidate neighboring data, causing data corruption in adjacent variables. Align DMA buffers to the cache line size (typically 64 bytes on modern CPUs).

> **Interview answer:** DMA bypasses the CPU cache and writes directly to physical RAM, so after a DMA fill the CPU's cache may hold stale data. The fix is software cache maintenance: invalidate cache lines covering the receive buffer before starting the DMA so the CPU is forced to re-read from RAM after the transfer. For transmit DMA, flush dirty cache lines to RAM before the DMAC reads them. Hardware-coherent interconnects (ARM CCI, Apple Silicon) make this transparent.
