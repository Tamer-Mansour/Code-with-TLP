# Quiz: Memory-Mapped I/O and DMA

**Q1. Why must device registers accessed via MMIO be declared `volatile` in C?**
- [ ] To tell the linker to place them in a special memory section.
- [ ] To prevent the CPU from executing instructions at those addresses.
- [x] To prevent the compiler from caching the register value in a CPU register across reads, since the hardware can change the value independently.
- [ ] To ensure the addresses are always aligned to a 4-byte boundary.

`volatile` forces the compiler to issue a fresh load instruction on every read and a store on every write, which is essential when the value can change due to hardware activity outside the compiler's knowledge.

---

**Q2. A RISC-V embedded program needs to control a GPIO peripheral. Which instruction does it use to write to the GPIO output register?**
- [ ] `OUT DX, AL` — the x86 I/O port instruction.
- [ ] `MMIO` — a dedicated RISC-V memory-mapped instruction.
- [x] `sw` (store word) to the physical address defined in the platform's memory map.
- [ ] `fence` to synchronize the peripheral.

RISC-V has no dedicated I/O instructions; all peripheral access is through ordinary load/store instructions (`lw`, `sw`, etc.) to the memory-mapped address of the device register.

---

**Q3. What is the purpose of a Write-1-to-Clear (W1C) register?**
- [ ] Writing a `1` to a bit sets it; writing `0` clears it.
- [ ] Writing any value replaces the entire register contents.
- [x] Writing a `1` to a bit clears only that bit, leaving other bits unchanged — used to acknowledge individual interrupt flags.
- [ ] The register can only be cleared by a hardware reset.

W1C lets a driver acknowledge one interrupt source (by writing `1` to its bit) without accidentally clearing other pending interrupt bits that it has not yet handled.

---

**Q4. In which scenario does DMA provide the greatest benefit over CPU-driven I/O?**
- [ ] When reading a single byte from a UART at 9600 baud.
- [x] When transferring a large block of data (e.g., a 64 KB disk sector) between a storage controller and RAM.
- [ ] When reading a keyboard scancode after a key press.
- [ ] When polling a GPIO pin every millisecond.

DMA's overhead (programming the controller, one completion interrupt) is amortized over the entire transfer. For a single byte or rare events, that overhead outweighs the benefit. For large bulk transfers, DMA saves thousands of CPU load/store cycles.

---

**Q5. After a DMA controller fills a receive buffer in RAM, why might the CPU read stale data from that buffer?**
- [ ] The DMA controller has not notified the PLIC yet.
- [ ] The CPU cannot read memory that was written by a DMA controller.
- [x] The CPU's cache may hold old values for those addresses; the DMA wrote to physical RAM, bypassing the cache.
- [ ] The buffer must be in non-cacheable memory for DMA to work at all.

The DMA controller writes directly to physical RAM without going through the CPU cache hierarchy. If the CPU has cached any of those addresses, it will see stale values. The driver must invalidate those cache lines after the DMA transfer completes.

---

**Q6. What is the key advantage of Port-Mapped I/O (PMIO) over Memory-Mapped I/O (MMIO)?**
- [x] The I/O address space is completely separate from RAM, so device registers can never alias valid memory addresses, and hardware access can be controlled via the x86 I/O Permission Bitmap.
- [ ] PMIO is supported on all modern architectures including ARM and RISC-V.
- [ ] PMIO allows access to more device registers because the port space is 32 bits wide.
- [ ] PMIO registers do not require `volatile` qualifiers and are automatically cache-coherent.

The clean separation between I/O ports and memory addresses is PMIO's defining advantage. The x86 IOPB provides fine-grained per-port privilege control. However, PMIO is limited to x86, has only 65,536 ports, and modern peripherals on all architectures use MMIO.
