# Quiz: I/O Systems, Memory-Mapped I/O, and DMA

**Q1. Which statement correctly distinguishes port-mapped I/O from memory-mapped I/O?**

- [ ] Port-mapped I/O uses normal load/store instructions; memory-mapped I/O uses `IN`/`OUT` instructions.
- [x] Port-mapped I/O uses dedicated `IN`/`OUT` instructions and a separate I/O address space; memory-mapped I/O places registers in the physical memory map and uses normal load/store instructions.
- [ ] Both share the same address space but port-mapped I/O requires a special `volatile` keyword.
- [ ] Memory-mapped I/O is x86-specific; port-mapped I/O works on all architectures.

_Port-mapped I/O is the x86-specific mechanism using `IN`/`OUT`. MMIO is the universal approach used by ARM, RISC-V, and all modern PCIe devices._

---

**Q2. A driver writes a new buffer address to a device register, then immediately writes a "start DMA" command. On a weakly-ordered CPU (ARM), what can go wrong without a memory barrier?**

- [ ] The CPU will raise a page fault because the register is non-cacheable.
- [ ] The DMA transfer will complete twice due to write buffering.
- [x] The start command may arrive at the device before the address register write, causing the DMA engine to fetch data from a wrong or stale address.
- [ ] Nothing; ARM guarantees strict write ordering for MMIO regions by default.

_Weakly-ordered architectures permit write reordering. A `wmb()` (write memory barrier) before the command write ensures the address is visible to the device first._

---

**Q3. After a device-to-memory (RX) DMA transfer completes, a driver on a non-coherent ARM platform reads the receive buffer and gets old data. What is the most likely cause?**

- [ ] The IOMMU blocked the DMA transfer, so no data was written.
- [ ] The DMA engine wrote to the wrong physical address.
- [x] The CPU's cache still holds stale lines from a previous read of that buffer region; the driver did not invalidate the cache before reading.
- [ ] The driver used `dma_alloc_coherent` which always returns uncacheable memory, so the data is invalid.

_On non-coherent platforms, after device-to-memory DMA, call `dma_sync_single_for_cpu(..., DMA_FROM_DEVICE)` to invalidate stale cache lines before reading the buffer._

---

**Q4. What is the primary security benefit of an IOMMU?**

- [ ] It encrypts all DMA transfers between the device and RAM.
- [ ] It compresses data on the bus to reduce bandwidth.
- [ ] It ensures cache coherence between the CPU and the DMA engine.
- [x] It restricts each device to only the physical memory pages explicitly mapped for it, preventing a malicious or buggy device from overwriting arbitrary physical memory.

_Without an IOMMU, a compromised PCIe card can DMA-write to any physical address, including kernel text. The IOMMU enforces per-device address translation and access control._

---

**Q5. Which DMA memory type should a driver use for a shared descriptor ring that both the CPU and device read and write continuously?**

- [x] `dma_alloc_coherent` — returns always-consistent memory (hardware coherent or uncacheable), so no explicit cache sync is needed.
- [ ] `dma_map_single` with `DMA_FROM_DEVICE` — this is for large RX data buffers only.
- [ ] `vmalloc` followed by `virt_to_phys` — sufficient for any DMA use case.
- [ ] `kmalloc(GFP_ATOMIC)` without any DMA API calls — DMA works directly with any kernel pointer.

_Descriptor rings need always-current visibility to both CPU and device. `dma_alloc_coherent` guarantees this; streaming mappings require explicit sync calls which are impractical for tightly-coupled rings._

---

**Q6. What does interrupt coalescing do in a high-throughput NIC driver?**

- [ ] It splits one large interrupt into many small interrupts to reduce ISR execution time.
- [ ] It ensures every DMA transfer generates exactly two interrupts: one on start, one on completion.
- [ ] It disables interrupts entirely and uses polling (NAPI) for all packet processing.
- [x] It delays raising a completion interrupt until N DMA transfers finish or a timer expires, allowing the ISR to process multiple completions per interrupt and reducing interrupt overhead.

_Coalescing trades a small latency increase for significantly lower per-packet interrupt cost, which is critical at line rates of 25–400 Gbps._
