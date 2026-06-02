# Interview Drill: Device Driver Questions

This lesson collects the highest-frequency device driver questions from system-programming and kernel-engineering interviews. For each question, a crisp one-line answer is provided, followed by the depth an interviewer expects.

---

## Q1: What is the difference between a character device and a block device?

**One-liner:** A character device streams bytes sequentially with no kernel buffer cache; a block device exposes randomly addressable fixed-size blocks backed by the page cache and I/O scheduler.

**Depth:** Filesystems can only be placed on block devices because they need random access and cache coherency. Block drivers must implement a request queue and handle `bio` structures, while character drivers implement `file_operations` directly.

---

## Q2: Why must interrupt handlers never sleep?

**One-liner:** IRQ handlers run with interrupts disabled on the local CPU; calling any sleeping primitive would deadlock because the scheduler cannot run to wake the thread.

**Depth:** If an ISR calls `mutex_lock()` and the mutex is held by a sleeping thread, the sleeping thread can never be scheduled (its wake-up interrupt is blocked), causing a deadlock. Use spinlocks in ISRs and defer blocking work to a workqueue.

---

## Q3: What is the difference between `copy_to_user` and a direct pointer dereference?

**One-liner:** `copy_to_user` validates the user-space pointer and handles page faults safely via the kernel's exception table; a direct dereference can crash the kernel or be exploited.

**Depth:** User pointers can be NULL, point to kernel space (an attack), or reference pages that are swapped out. `copy_to_user` returns a non-zero byte count on partial failure, allowing the driver to return `-EFAULT` cleanly.

---

## Q4: What is DMA and why does it need a separate API?

**One-liner:** DMA lets hardware transfer data directly to/from RAM without CPU involvement; the DMA API handles cache coherency and IOMMU address translation transparently.

**Depth:** On systems with virtual memory and caches, a physical address given directly to a device may point to stale cache lines. `dma_map_*` and `dma_sync_*` perform necessary cache flushes/invalidations and, when an IOMMU is present, map a device-visible I/O address (IOVA) to the correct physical page.

---

## Q5: What is the purpose of `probe()` and `remove()` in the driver model?

**One-liner:** `probe()` is called when the kernel binds a driver to a device (initialize hardware, allocate resources); `remove()` is called on unbind (release all resources).

**Depth:** The pairing must be symmetrical. Every IRQ requested, memory region reserved, and DMA buffer allocated in `probe()` must be freed in `remove()`. Failing to do so causes resource leaks that appear only during hot-unplug.

---

## Q6: What is the difference between a spinlock and a mutex in driver code?

**One-liner:** A spinlock busy-waits without sleeping and is safe in interrupt context; a mutex sleeps while waiting and can only be used in process context.

**Depth:** Use a spinlock when the critical section is very short and the code can run in ISR context. Use a mutex for longer critical sections in process context (e.g., `read()`/`write()` handlers). Mixing them incorrectly — a mutex locked in an ISR — causes a deadlock.

---

## Q7: What is a kernel module's `vermagic` and why does it matter?

**One-liner:** `vermagic` is a string embedding the kernel version and ABI configuration; the kernel checks it on `insmod` to prevent loading a module compiled against an incompatible kernel.

**Depth:** Even minor changes to kernel data structures (adding a field to `struct task_struct`) change the ABI. A module compiled before the change would access wrong offsets, causing silent corruption or crashes.

---

## Q8: How does NAPI improve NIC driver performance?

**One-liner:** NAPI disables NIC interrupts after the first packet and polls until the RX queue is empty, then re-enables interrupts — trading latency for throughput at high packet rates.

**Depth:** At low load, the ISR wakes NAPI and it processes one packet (interrupt-driven behavior). At high load, the ISR fires once and NAPI drains thousands of packets in one poll cycle (polling behavior), preventing interrupt storms that would saturate the CPU.

---

## Q9: What is the IOMMU and how does it protect the system?

**One-liner:** The IOMMU translates device bus addresses to physical memory addresses, so a device can only access memory pages explicitly mapped for it — preventing rogue DMA attacks.

**Depth:** Without an IOMMU, a compromised or buggy DMA device can write to any physical address, including kernel code. With an IOMMU, the kernel's DMA API creates mappings for exactly the buffers the driver registers, and the hardware enforces boundaries.

---

## Q10: What tools would you use to debug a kernel module crash?

**One-liner:** `dmesg` for the oops trace, `addr2line` or `gdb vmlinux` to decode stack addresses, `kgdb` for live debugging, and `kdump`/`crash` for post-mortem analysis of core dumps.

**Depth:** A typical workflow: enable `CONFIG_DEBUG_INFO`, reproduce the crash, capture the oops from `dmesg`, use `scripts/decode_stacktrace.sh` to resolve symbols. For harder bugs, `KASAN` (AddressSanitizer for kernel) detects memory corruption, and `lockdep` detects locking errors at runtime.

---

## Quick Reference Table

| Topic | Key fact |
|---|---|
| Char vs block | Char = byte stream; Block = random block access + page cache |
| ISR constraints | No sleep, no mutex, minimal work |
| DMA coherency | Always use `dma_alloc_coherent` or `dma_sync_*` |
| ioctl command encoding | Use `_IO`, `_IOR`, `_IOW`, `_IOWR` macros |
| Unknown ioctl | Return `-ENOTTY` |
| Module load fail | `vermagic` mismatch → `Invalid module format` |
| NAPI | Interrupt → poll → re-enable interrupt |
| User-space driver | UIO or VFIO; crash-safe; higher latency |
