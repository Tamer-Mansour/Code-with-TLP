# Interview Drill: Memory-Mapped I/O and DMA

This lesson presents the most frequently asked MMIO and DMA questions in systems-level interviews, with crisp one-to-two sentence answers you can deliver confidently.

---

**Q: What is the difference between port-mapped I/O and memory-mapped I/O?**

> Port-mapped I/O (PMIO) places device registers in a separate 16-bit I/O address space, accessed via the `IN`/`OUT` instructions — an x86-only mechanism. Memory-mapped I/O (MMIO) assigns device registers physical addresses in the normal memory map, reached with ordinary load/store instructions; it works on any ISA and supports a much larger register space.

---

**Q: Why must MMIO regions be marked non-cacheable?**

> Device registers can change asynchronously (e.g., a status bit set by hardware). If the CPU caches a register read, subsequent reads return the cached value instead of the real current state, causing the driver to miss status changes. Marking the region non-cacheable or as Device memory forces every access to go to the physical bus.

---

**Q: What is DMA and why is it useful?**

> Direct Memory Access lets a peripheral read from or write to main memory autonomously, without the CPU moving each byte. The CPU programs a descriptor with the buffer's physical address, triggers the transfer, then does other work. The device raises an interrupt when done. DMA dramatically improves throughput and reduces CPU load for bulk data transfers.

---

**Q: Walk me through a complete DMA receive (device-to-memory) transfer.**

> 1. Driver allocates and pins a buffer; gets its bus (physical/IOVA) address.
> 2. Driver writes bus address and length into device MMIO registers (or a descriptor).
> 3. Driver issues a `wmb()` then writes the start command to the command register.
> 4. Device DMA engine writes data to RAM over the bus — CPU is free.
> 5. Device asserts an interrupt when done.
> 6. ISR reads status register, acknowledges interrupt, calls `dma_sync_single_for_cpu()`.
> 7. Driver thread wakes up, reads data from the buffer.

---

**Q: What happens if the CPU has dirty cache lines for a DMA TX buffer when the device starts reading?**

> The device DMA engine reads from RAM directly — it does not see CPU cache contents. If the CPU wrote new data to a TX buffer but those writes sit in cache and have not been flushed (written back) to RAM, the device reads the old stale bytes and transmits garbage. The fix is to call `dma_sync_single_for_device()` (which issues a cache flush/clean) before triggering the device.

---

**Q: What is an IOMMU and what security problem does it solve?**

> An IOMMU sits between the device bus and physical RAM. It translates I/O Virtual Addresses (IOVAs) to physical addresses and enforces access permissions. Without it, a malicious or buggy device could DMA-write to any physical address — including kernel code pages. The IOMMU restricts each device to only the physical pages the OS has explicitly mapped for it.

---

**Q: What is a DMA descriptor ring?**

> A descriptor ring is a circular array of small structs in RAM, each holding the bus address, length, and flags for one DMA buffer. The device's DMA engine walks the ring in a producer-consumer loop: the driver posts descriptors, the device consumes them asynchronously, and sets a "done" bit when finished. This avoids a round-trip MMIO write per transfer and enables pipelining many buffers at once.

---

**Q: What is `ioremap()` and why is it necessary?**

> After firmware assigns a physical address range to a device's MMIO registers, the kernel must create a virtual address mapping before its code can dereference a pointer to them. `ioremap(phys, size)` creates a non-cacheable kernel virtual mapping for the given physical range and returns the virtual base. The driver uses that virtual address with `readl()`/`writel()` to access registers safely.

---

**Q: What is interrupt coalescing in the context of DMA?**

> Instead of raising one interrupt per completed DMA transfer (which could be millions per second on a 100 Gbps NIC), the device defers the interrupt until either N completions accumulate or a timer expires. The ISR then processes all pending completions in a batch, reducing interrupt overhead at the cost of a small increase in per-transfer latency.

---

**Q: Explain the purpose of `wmb()` before writing a DMA start command.**

> Modern CPUs and bus fabrics can reorder memory writes. If the start command reaches the device before the address/length registers (posted earlier by the driver), the device begins a transfer without knowing where to write — resulting in data corruption or a bus fault. A write memory barrier (`wmb()`) ensures all preceding writes are globally visible before the barrier completes, making it safe to issue the start command immediately after.
