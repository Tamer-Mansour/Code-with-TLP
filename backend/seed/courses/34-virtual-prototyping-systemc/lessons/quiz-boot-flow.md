# Quiz: Boot Flow and Bring-Up in a VP

Test your understanding of the VP boot sequence, from reset vector through Linux handoff.

---

**Q1. What is the reset vector?**

- [ ] The last address the CPU reads before shutdown
- [x] The address the CPU's program counter is set to immediately after reset
- [ ] The base address of DRAM
- [ ] The entry point of the Linux kernel

The reset vector is architecture-defined and hardwired (or strapped) — it is the very first address the CPU fetches an instruction from after reset. For ARM Cortex-A CPUs it is commonly `0x00000000` or a high-vector variant.

---

**Q2. In a loosely timed VP, what is the most common approach to loading the kernel image before simulation starts?**

- [ ] The CPU ISS reads the kernel from a simulated SD card model
- [ ] The kernel is compiled directly into the VP binary
- [x] The host platform code pre-loads the binary into the DRAM model during elaboration
- [ ] U-Boot downloads the kernel via a simulated TFTP session

Pre-loading at elaboration time skips storage peripheral simulation, dramatically reducing the complexity needed to get Linux running for the first time. Storage simulation can be added incrementally later.

---

**Q3. On ARMv8 (AArch64), which register must hold the DTB physical address when the bootloader jumps to the Linux kernel?**

- [ ] x1
- [ ] x30 (link register)
- [ ] sp (stack pointer)
- [x] x0

The ARM64 Linux boot protocol specifies that x0 must contain the physical address of the flattened device tree (DTB/FDT). Registers x1, x2, and x3 must be zero (reserved). Violating this convention causes the kernel to read the DTB from the wrong location and crash.

---

**Q4. Why is the GIC (Generic Interrupt Controller) required to boot Linux, even if no peripherals generate interrupts?**

- [ ] The GIC manages DRAM refresh cycles
- [ ] U-Boot requires GIC registers to relocate itself
- [x] The ARM Generic Timer delivers its interrupt through the GIC, which drives the kernel scheduler tick
- [ ] Linux reads the GIC ID register to detect the CPU core count

Without the GIC, the timer IRQ is never delivered to the CPU. The Linux kernel's `schedule()` function is driven by the timer tick (jiffies), so a missing or broken GIC causes the kernel to freeze after `start_kernel()` completes its non-preemptible initialization.

---

**Q5. What is the primary purpose of VP boot checkpointing?**

- [ ] To compress the DRAM model to save disk space
- [ ] To record cycle-accurate timing of the boot sequence
- [x] To save the full simulation state after boot so subsequent runs can skip the boot sequence entirely
- [ ] To verify that the DTB matches the hardware model

Checkpointing saves all memory and register state at a post-boot snapshot point. Restoring a checkpoint allows a developer or CI system to start executing test software immediately without repeating the multi-minute simulation of the boot sequence.

---

**Q6. Which of the following is NOT required as a minimum model to boot Linux to a shell prompt in a VP?**

- [ ] CPU ISS
- [ ] Flat DRAM model
- [x] DMA controller
- [ ] UART (serial console)

The DMA controller can be a stub that returns zero and absorbs writes; Linux will gracefully fall back to PIO if DMA is unavailable, or simply not load DMA-dependent drivers. The CPU ISS, DRAM, and UART are all essential — without them, there is nothing to execute, no memory for the kernel, and no way to observe output.
