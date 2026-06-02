# User-Space vs Kernel-Space Drivers

Not all drivers must live in the kernel. A significant portion of device support — especially for USB devices, hardware accelerators, and test equipment — can be implemented entirely in user space. Understanding the trade-offs determines which model to choose.

## The Traditional Model: Kernel-Space Drivers

A kernel-space driver runs at ring 0 (x86) with full hardware access. It registers with the kernel subsystems directly and handles IRQs natively.

**Advantages:**
- Lowest possible latency — no context switch to service hardware.
- Direct access to kernel subsystems (networking stack, VFS, DMA API).
- Hardware IRQ handling without user-space relay.

**Disadvantages:**
- A bug can crash the entire system.
- Development cycle: write code → recompile module → reboot → debug (crash dumps are hard).
- Must follow strict kernel coding rules (no floating point, limited stack size, GPL implications).

## User-Space Drivers

A user-space driver is a normal process that accesses hardware through controlled kernel interfaces.

### Access Mechanisms

| Mechanism | What it provides |
|---|---|
| `/dev/mem` | Raw memory-mapped I/O (dangerous, usually restricted) |
| `mmap` on `/sys` resource files | Map PCI BAR into process address space |
| `ioport` (`inb`/`outb`) | x86 I/O port access after `ioperm()` |
| UIO (Userspace I/O) | Thin kernel shim; maps device memory + delivers IRQs |
| VFIO | Full IOMMU-backed device pass-through for safe user-space DMA |

### UIO: The Simplest Bridge

The kernel `uio` driver exposes a device as `/dev/uioN`. The user-space driver:

1. `mmap`s the hardware registers.
2. `read()`s from `/dev/uioN` — this blocks until an IRQ fires, then returns the interrupt count.
3. Handles the event and `write()`s 1 to re-enable the interrupt.

```python
import mmap, os, struct

fd = os.open("/dev/uio0", os.O_RDWR)
# Map hardware registers (device's BAR)
regs = mmap.mmap(fd, 4096, offset=0)

while True:
    # Block until interrupt
    irq_count = struct.unpack("I", os.read(fd, 4))[0]
    # Read status register (offset 0x08)
    status = struct.unpack_from("I", regs, 0x08)[0]
    # Process event ...
    # Re-enable interrupt
    os.write(fd, struct.pack("I", 1))
```

### VFIO: Production-Grade User-Space Drivers

VFIO (Virtual Function I/O) is the modern approach used by DPDK (networking), SPDK (storage), and virtual machine device pass-through. Key features:

- **IOMMU protection** — device can only DMA to addresses explicitly mapped, preventing rogue DMA attacks.
- **Container model** — groups of devices sharing an IOMMU domain are managed together.
- **No root required** — with proper group ownership.

## Framework Comparison

| Property | Kernel Driver | UIO Driver | VFIO Driver |
|---|---|---|---|
| Crash risk | Kernel panic | Process crash only | Process crash only |
| IRQ latency | Lowest | Higher (syscall) | Higher (syscall) |
| DMA safety | IOMMU optional | None | IOMMU enforced |
| Debug ease | Hard | Standard gdb/valgrind | Standard gdb/valgrind |
| Language choice | C only | Any language | Any language |
| Licensing | GPL kernel API | Flexible | Flexible |

## Real-World Examples

- **DPDK** (Data Plane Development Kit) — high-speed NIC driver in user space using VFIO/UIO, bypassing the Linux network stack to achieve line-rate packet processing.
- **SPDK** (Storage Performance Development Kit) — NVMe driver in user space using VFIO, achieving millions of IOPS without kernel overhead.
- **libusb** — USB device control library that talks to devices via the `usbfs` kernel interface (files in `/dev/bus/usb/`), used by most USB device libraries.

## When to Choose Each

Choose **kernel-space** when:
- The driver must integrate with kernel subsystems (networking, filesystem, input).
- IRQ latency requirements are in the microsecond range.
- The device is system-critical (storage controller, display).

Choose **user-space** when:
- Stability and crash isolation are paramount.
- Development speed matters.
- The device is application-specific (test equipment, accelerators).
- You need language flexibility.

## Interview Answer

> **Q: What is the main advantage of a user-space driver over a kernel-space driver?**
>
> **Interview answer:** A user-space driver runs in an isolated process, so a bug causes only that process to crash rather than panicking the kernel; it also allows debugging with standard tools like gdb and is not bound by kernel licensing or coding restrictions, at the cost of higher interrupt latency due to context-switch overhead.
