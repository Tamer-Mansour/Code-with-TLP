# Quiz: Device Drivers

Test your understanding of device driver concepts from this module.

---

**Q1. Which kernel data structure maps user-space file operations (open, read, write) to driver functions?**

- [ ] `struct device_driver`
- [x] `struct file_operations`
- [ ] `struct block_device_operations`
- [ ] `struct bus_type`

The `file_operations` structure is a vtable of function pointers registered by a character driver. The kernel calls the appropriate pointer when user space invokes a syscall on the device file.

---

**Q2. An interrupt handler calls `mutex_lock()` on a mutex that is currently held by a sleeping process. What happens?**

- [ ] The interrupt handler preempts the sleeping process and acquires the mutex.
- [ ] The mutex is silently skipped and the handler continues.
- [x] A deadlock occurs because the ISR cannot sleep, and the sleeping process cannot be woken while the CPU handles the interrupt.
- [ ] The kernel automatically converts the mutex to a spinlock.

ISRs run with local interrupts disabled. `mutex_lock()` tries to sleep when the mutex is unavailable, but sleeping in interrupt context is illegal — this is a classic interrupt-context deadlock.

---

**Q3. What is the correct DMA API call to allocate a cache-coherent buffer suitable for long-lived DMA descriptor rings?**

- [ ] `kmalloc()` with `GFP_DMA`
- [ ] `dma_map_single()`
- [x] `dma_alloc_coherent()`
- [ ] `vmalloc()`

`dma_alloc_coherent()` allocates memory that is guaranteed cache-coherent between CPU and device at all times. `dma_map_single()` maps an existing buffer for a single DMA operation and requires explicit sync calls.

---

**Q4. A driver's `probe()` function requests IRQ 42. The module is then unloaded without calling `free_irq()`. What is the most likely outcome?**

- [ ] The kernel automatically frees the IRQ on module unload.
- [ ] IRQ 42 is disabled permanently until the next reboot.
- [x] The next interrupt on IRQ 42 calls the freed handler, causing a kernel crash or memory corruption.
- [ ] `rmmod` fails with `-EBUSY` and prevents the unload.

The IRQ handler pointer still points to the now-freed module's code. When hardware raises IRQ 42, the kernel jumps to freed memory — a use-after-free in interrupt context, almost certainly causing a kernel oops or silent data corruption.

---

**Q5. What distinguishes a block device from a character device in Linux?**

- [ ] Block devices use interrupts; character devices use polling.
- [ ] Block devices can only be opened by root; character devices can be opened by any user.
- [ ] Character devices are faster because they bypass the VFS.
- [x] Block devices expose randomly addressable fixed-size blocks backed by the page cache; character devices expose a sequential byte stream without kernel buffering.

The page cache and I/O scheduler sit on top of block devices, enabling filesystems and efficient buffering. Character devices bypass these layers, making them suitable for streaming data like serial ports.

---

**Q6. What does NAPI do when a NIC receives packets at a very high rate?**

- [ ] It raises a separate interrupt for every packet to minimize latency.
- [ ] It drops packets above a configurable threshold to protect the CPU.
- [x] It disables NIC interrupts after the first packet and polls the RX queue in a loop until empty, then re-enables interrupts.
- [ ] It offloads packet processing to a dedicated kernel thread that runs at real-time priority.

NAPI is a hybrid interrupt/polling scheme. The first packet triggers an interrupt; subsequent packets are collected by polling without additional interrupts. This prevents interrupt storms at high packet rates while still sleeping (interrupt-driven) at low rates.
