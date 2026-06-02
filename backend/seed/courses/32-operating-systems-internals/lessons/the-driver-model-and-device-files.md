# The Driver Model and Device Files

Modern operating systems use a *driver model* — a framework that standardizes how drivers register themselves, how devices are discovered, and how the kernel binds a device to the right driver. Understanding this model is essential for writing portable, maintainable drivers.

## The Linux Driver Model

Linux's driver model lives in the `drivers/base/` subsystem and exposes its structure through three core abstractions:

| Abstraction | Kernel Type | Represents |
|---|---|---|
| Bus | `struct bus_type` | A communication channel (PCI, USB, I2C, platform) |
| Device | `struct device` | A specific hardware unit on a bus |
| Driver | `struct device_driver` | Code that knows how to manage a class of devices |

When the kernel detects a new device, it walks the list of registered drivers for that bus and calls each driver's `probe()` function until one claims the device. This is called *binding*.

```c
struct device_driver {
    const char           *name;
    struct bus_type      *bus;
    int (*probe)(struct device *dev);   /* bind driver to device */
    int (*remove)(struct device *dev);  /* unbind (hot-unplug)   */
    int (*suspend)(struct device *dev, pm_message_t state);
    int (*resume)(struct device *dev);
};
```

## sysfs: The Kernel's Device Topology

The driver model exposes its entire device tree through `/sys` (sysfs). Every bus, device, and driver has a directory there. This lets user-space tools like `udev` react to hardware changes.

```bash
# See all PCI devices
ls /sys/bus/pci/devices/

# Find the driver bound to a specific device
ls -l /sys/bus/usb/devices/1-1/driver
```

## Device Files: The User-Space Interface

Unix represents devices as files in `/dev`. Applications open a device file just like a regular file; the kernel routes those calls to the appropriate driver.

Every device file has two numbers:

- **Major number** — identifies the driver responsible.
- **Minor number** — identifies the specific instance (e.g., `/dev/sda` vs `/dev/sdb`).

```bash
ls -l /dev/sda /dev/ttyS0
# brw-rw---- 1 root disk    8,  0 ...  /dev/sda    (block, major=8, minor=0)
# crw-rw---- 1 root dialout 4, 64 ...  /dev/ttyS0  (char, major=4, minor=64)
```

The `b` or `c` prefix tells you whether it is a block or character device.

## udev and Dynamic Device Management

Before `udev`, device nodes were created statically. Today `udev` listens to kernel `uevent` messages (emitted via netlink) and creates or removes `/dev` entries on demand — the reason plugging in a USB drive immediately makes `/dev/sdb` appear.

```
Kernel detects device
       |
  uevent (netlink)
       |
    udev daemon
       |
  applies rules from /etc/udev/rules.d/
       |
  creates /dev/sdb, sets permissions, fires scripts
```

## Platform Devices

Not all hardware sits on a self-describing bus like PCI. SoC peripherals (UART, SPI controllers) are described in a *Device Tree* (on ARM) or ACPI tables (on x86). The kernel parses these at boot and creates *platform devices*, which platform drivers then bind to.

```c
static const struct of_device_id my_uart_ids[] = {
    { .compatible = "vendor,my-uart" },
    {}
};
MODULE_DEVICE_TABLE(of, my_uart_ids);
```

## Common Pitfalls

- **Forgetting `remove()`** — if `probe()` allocates resources but `remove()` leaks them, hot-unplug causes a kernel memory leak.
- **Race between probe and open** — a device can be opened before `probe()` fully initializes it; use `device_initialize()` ordering carefully.
- **Wrong bus match** — a driver registered on the wrong bus will never bind, producing silent failure.

## Interview Answer

> **Q: How does the kernel know which driver to use for a newly plugged device?**
>
> **Interview answer:** The kernel's driver model matches the device's bus-specific ID (vendor/product ID on USB/PCI, compatible string in Device Tree) against all registered drivers for that bus, calling `probe()` on the matching driver to complete the binding.
