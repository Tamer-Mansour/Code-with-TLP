# Direct Memory Access (DMA): Offloading the CPU

Copying a 1 MB network packet byte-by-byte through the CPU is wasteful. DMA solves this by letting devices read from and write to main memory directly, without stalling the CPU for each byte.

## The Problem DMA Solves

Without DMA, a disk read works like this:

1. CPU issues a "read sector" command to the disk controller.
2. Disk controller signals "byte ready" repeatedly (interrupt or polling).
3. CPU reads one byte from the data register, writes it to a RAM buffer.
4. Repeat 512 times for a single sector — thousands of times for a file.

At 4 GHz with PCIe, the bus round-trip overhead alone can consume hundreds of cycles per byte. DMA eliminates step 2–4 from the CPU's to-do list.

## What a DMA Controller Does

A **DMA controller (DMAC)** is a hardware unit that can autonomously perform memory-to-device, device-to-memory, and memory-to-memory transfers. It has its own bus master capability — it can issue read/write transactions on the system bus independently of the CPU.

Modern systems embed DMA controllers directly inside each peripheral (the NIC, SATA controller, USB host) rather than using a shared, central DMAC. These are often called **bus-mastering DMA** or simply **device DMA engines**.

## DMA Descriptor Rings

High-performance devices use **descriptor rings**: circular arrays of small structs in RAM. Each descriptor tells the DMA engine where one buffer lives and how large it is.

```c
// Simplified NIC RX descriptor (e.g., Intel i210)
struct rx_desc {
    uint64_t buf_phys_addr;   // physical address of the receive buffer
    uint16_t length;          // filled in by NIC after reception
    uint16_t checksum;
    uint8_t  status;          // bit 0 = DD (Descriptor Done)
    uint8_t  errors;
    uint16_t vlan_tag;
} __attribute__((packed));
```

The driver allocates a ring of these descriptors in physically-contiguous (or IOMMU-mapped) memory, writes their base address into an MMIO register, and the NIC's DMA engine walks the ring automatically as packets arrive.

## Types of DMA

| Type | Description | Example |
|---|---|---|
| **Memory-to-device** | CPU prepares data in RAM; device reads it via DMA | NIC TX, GPU command buffer |
| **Device-to-memory** | Device writes data into RAM; CPU reads results | NIC RX, disk read |
| **Memory-to-memory** | DMAC copies between two RAM regions | ARM PL080 DMAC, GPU blit |
| **Scatter-gather** | Single transfer spans discontiguous buffers | Linux `scatterlist`, virtio |

Scatter-gather DMA is critical for zero-copy networking: the OS can hand the NIC a list of page addresses (possibly discontiguous) and the NIC assembles or disassembles the packet without requiring one huge contiguous buffer.

## Physical Addresses and the IOMMU

DMA engines operate on **physical addresses** (or IOVA — I/O Virtual Addresses if an IOMMU is present). The driver must:

1. Allocate a DMA-capable buffer.
2. Get its **bus address** (physical or IOVA).
3. Write that address into a device descriptor or register.

On Linux:

```c
// Allocate coherent DMA memory (cached by neither CPU nor device)
dma_addr_t dma_handle;
void *cpu_addr = dma_alloc_coherent(dev, size, &dma_handle, GFP_KERNEL);

// Give the bus address to the device
writel((uint32_t)dma_handle, mmio_base + TX_BUF_ADDR_LO);
writel((uint32_t)(dma_handle >> 32), mmio_base + TX_BUF_ADDR_HI);
```

`dma_alloc_coherent` ensures:
- The buffer is in a DMA-reachable memory zone.
- Cache coherence is maintained (either hardware-coherent or software-flushed).
- On IOMMU-enabled systems, an IOVA is created and returned.

## The IOMMU: DMA Security

Without an IOMMU, a compromised device driver (or a malicious PCIe card) could issue DMA writes to any physical address, overwriting kernel code. The **IOMMU (I/O Memory Management Unit)** interposes between the device bus and RAM, translating IOVAs to physical addresses and enforcing access permissions — isolating devices from one another and from the kernel.

```
Device --> DMA request (IOVA 0x1000) --> IOMMU --> Physical 0xABC1000 (permitted)
Device --> DMA request (IOVA 0x9000) --> IOMMU --> FAULT (not mapped)
```

Linux uses `intel_iommu` (VT-d) or `arm_smmu` for this.

> **Interview answer:** DMA lets a peripheral read from or write to main memory autonomously, without CPU involvement per byte. The CPU sets up a descriptor with the buffer's physical address and length, issues a "start" command, and the DMA engine performs the transfer. When done, it raises an interrupt so the CPU processes the result.
