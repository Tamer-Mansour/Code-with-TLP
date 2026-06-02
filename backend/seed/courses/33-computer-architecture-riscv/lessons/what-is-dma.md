# What Is Direct Memory Access (DMA)?

Even with interrupt-driven I/O, every byte transferred between a device and RAM still passes through the CPU: the ISR reads from the device register, stores into a buffer, increments a pointer, and repeats. For transferring a 512-byte disk sector, that is 512 load-store pairs — potentially thousands of instructions. DMA eliminates this overhead entirely.

## The Core Idea

A **DMA controller (DMAC)** is a small, dedicated processor whose sole job is moving data between a device and system memory. The CPU programs the DMAC once, then steps aside. The DMAC takes over the memory bus and copies the data autonomously. When it finishes, it raises a single interrupt to notify the CPU.

```
Without DMA (CPU-driven):
  CPU: read byte from device → store to RAM → read → store → ... (N iterations)
  Device data path: Device → CPU register → RAM

With DMA:
  CPU: program DMAC (source, destination, count) → do other work
  DMA: Device → RAM (directly, N bytes, no CPU involvement)
  DMA: raise interrupt when done
  CPU: handle completion interrupt once
```

## DMA Transfer Anatomy

A DMA transfer is described by three parameters the CPU writes into the DMAC's configuration registers:

1. **Source address** — Where to read from (device FIFO register address for device→RAM, or a RAM address for RAM→device).
2. **Destination address** — Where to write (a RAM buffer address for device→RAM).
3. **Transfer count** — How many units (bytes, half-words, or words) to move.

```c
// Hypothetical DMA controller register map
#define DMAC_BASE       0x20000000UL
#define DMAC_SRC        (*(volatile uint32_t *)(DMAC_BASE + 0x00))
#define DMAC_DST        (*(volatile uint32_t *)(DMAC_BASE + 0x04))
#define DMAC_COUNT      (*(volatile uint32_t *)(DMAC_BASE + 0x08))
#define DMAC_CTRL       (*(volatile uint32_t *)(DMAC_BASE + 0x0C))
#define DMAC_STATUS     (*(volatile uint32_t *)(DMAC_BASE + 0x10))

#define DMAC_CTRL_START  (1u << 0)
#define DMAC_CTRL_IRQ_EN (1u << 1)
#define DMAC_STATUS_DONE (1u << 0)

static uint8_t rx_buffer[512];

// Initiate DMA transfer: read 512 bytes from UART FIFO to rx_buffer
void start_uart_dma_rx(void) {
    DMAC_SRC   = 0x10013000UL;          // UART RX data register
    DMAC_DST   = (uint32_t)rx_buffer;   // destination in RAM
    DMAC_COUNT = 512;                   // 512 bytes
    DMAC_CTRL  = DMAC_CTRL_START | DMAC_CTRL_IRQ_EN;
    // CPU is now free; DMA runs independently
}

// DMA completion interrupt handler
void dma_done_isr(void) {
    DMAC_STATUS = DMAC_STATUS_DONE;     // W1C: acknowledge
    process_received_data(rx_buffer, 512);
}
```

## DMA Bus Mastering

On a shared memory bus, both the CPU and the DMAC need exclusive access to RAM for each transaction. Three schemes manage this:

1. **Burst mode** — DMAC seizes the bus for the entire transfer. The CPU is locked out until done. Simple but can starve the CPU on large transfers.
2. **Cycle stealing** — DMAC steals individual bus cycles when the CPU is not using the bus (e.g., during an internal pipeline stall). Interleaved with CPU access; adds latency to the transfer.
3. **Transparent mode** — DMAC only runs when it detects the CPU is not using the bus. No CPU slowdown but lower DMA bandwidth.

Modern systems use a more sophisticated interconnect (AXI, PCIe) where multiple bus masters coexist simultaneously. The interconnect arbitrates between them.

## Real-World DMA Applications

| Use Case | Transfer Direction | Typical Size |
|---|---|---|
| Disk / NVMe read | Storage → RAM | 4 KB – 128 KB pages |
| Network packet receive | NIC → RAM | 64 B – 9 KB (jumbo frames) |
| Network packet transmit | RAM → NIC | 64 B – 9 KB |
| Audio playback | RAM → DAC FIFO | 1 KB – 64 KB ring buffer |
| USB bulk transfer | USB controller ↔ RAM | Variable |
| GPU texture upload | RAM → GPU VRAM | Megabytes |

## DMA Descriptors (Scatter-Gather)

For fragmented data (e.g., a network packet spread across non-contiguous RAM pages), the DMAC supports **scatter-gather** mode. The CPU builds a linked list of **DMA descriptors** in RAM, each containing a source address, destination address, and count:

```c
typedef struct dma_desc {
    uint32_t src;
    uint32_t dst;
    uint32_t len;
    uint32_t next;  // address of next descriptor, or 0 for end
} DMADesc;

DMADesc descs[3] = {
    { 0x10013000, (uint32_t)&buf[0],    256, (uint32_t)&descs[1] },
    { 0x10013000, (uint32_t)&buf[256],  256, (uint32_t)&descs[2] },
    { 0x10013000, (uint32_t)&buf[512],  256, 0 },
};
// Point DMAC to head of list; it walks the chain autonomously
DMAC_DESC_PTR = (uint32_t)&descs[0];
DMAC_CTRL     = DMAC_CTRL_SG_MODE | DMAC_CTRL_START;
```

## Common Pitfalls

- **Buffer still allocated on the stack** — The CPU function returns and the stack frame is deallocated while the DMAC is still writing to it. Always use statically or heap-allocated DMA buffers.
- **Cache coherence** — The DMAC writes directly to RAM, bypassing the CPU's cache. The CPU may read stale cached data after a DMA fill (covered in the next lesson).
- **Alignment requirements** — Most DMACs require source/destination addresses and transfer counts to be naturally aligned.

> **Interview answer:** DMA offloads bulk memory transfers from the CPU to a dedicated DMA controller. The CPU programs the source address, destination address, and byte count, then resumes other work. The DMAC transfers the data directly over the memory bus and raises a single interrupt on completion, freeing the CPU from per-byte involvement and dramatically increasing I/O throughput.
