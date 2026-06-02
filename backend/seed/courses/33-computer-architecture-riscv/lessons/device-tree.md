# The Device Tree and Hardware Discovery

Unlike x86 systems that enumerate hardware through PCI and ACPI, RISC-V platforms (like ARM platforms before them) typically use a **Device Tree** to describe hardware to the operating system. The device tree is a data structure that tells the kernel what peripherals exist, where they are mapped in memory, how they are connected to interrupt controllers, and what clocks they depend on.

## Why a Device Tree?

Embedded and SoC-based systems have no universal bus that can announce "I am a UART at 0x1000_0000". The hardware topology is fixed at design time, but the OS binary should remain portable across many different boards. The device tree solves this by externalizing the hardware description into a file that can be updated without recompiling the kernel.

## Device Tree Source vs. Binary

The device tree exists in two forms:

- **DTS (Device Tree Source)** — human-readable text format.
- **DTB (Device Tree Blob)** — compiled binary, passed to the kernel at boot.

The compiler is `dtc` (Device Tree Compiler):

```bash
# Compile DTS to DTB
dtc -I dts -O dtb -o board.dtb board.dts

# Decompile DTB back to DTS (for inspection)
dtc -I dtb -O dts -o board.dts board.dtb
```

## Anatomy of a DTS File

```dts
/dts-v1/;

/ {
    #address-cells = <1>;
    #size-cells = <1>;
    compatible = "my-vendor,my-board";

    cpus {
        #address-cells = <1>;
        #size-cells = <0>;
        cpu@0 {
            compatible = "riscv";
            device_type = "cpu";
            reg = <0>;
            riscv,isa = "rv64imafdc";
        };
    };

    memory@80000000 {
        device_type = "memory";
        reg = <0x80000000 0x40000000>;  /* 1 GB at 0x80000000 */
    };

    uart0: uart@10000000 {
        compatible = "ns16550a";
        reg = <0x10000000 0x1000>;
        interrupts = <10>;
        clock-frequency = <3686400>;
    };

    chosen {
        bootargs = "console=ttyS0,115200 root=/dev/mmcblk0p2";
        stdout-path = &uart0;
    };
};
```

Key nodes:

| Node | Purpose |
|------|---------|
| `cpus` | Describes each CPU/hart |
| `memory` | Declares DRAM regions |
| `uart@10000000` | UART peripheral at that MMIO base |
| `chosen` | Kernel command line and console selection |
| `aliases` | Short names for frequently referenced nodes |

## The `compatible` Property

The `compatible` property is how the kernel matches a device to a driver. It is a list of strings from most-specific to most-general:

```dts
compatible = "my-vendor,fancy-uart", "ns16550a";
```

The kernel tries each string in order. If no driver matches the vendor-specific string, it falls back to the generic `ns16550a` driver.

## How the Kernel Reads the DTB

The bootloader places the DTB physical address in register `a1` before jumping to the kernel. The kernel entry code saves this pointer and later calls `unflatten_device_tree()` to parse it into an in-memory tree of nodes. Drivers then call APIs like:

```c
// Find a node by compatible string
struct device_node *np =
    of_find_compatible_node(NULL, NULL, "ns16550a");

// Read a u32 property
u32 clk_freq;
of_property_read_u32(np, "clock-frequency", &clk_freq);
```

## The `chosen` Node and Bootargs

The `chosen` node is special — it carries runtime information that the bootloader may modify:

```dts
chosen {
    bootargs = "console=ttyS0,115200 root=/dev/mmcblk0p2 rw";
    linux,initrd-start = <0x88000000>;
    linux,initrd-end   = <0x88800000>;
};
```

U-Boot and GRUB routinely patch the `chosen` node in the DTB before jumping to the kernel to pass the correct root device, kernel command line, or initrd address.

## Common Pitfalls

- **Wrong `#address-cells` or `#size-cells`.** These values control how many 32-bit words encode addresses and sizes in child nodes. Getting them wrong silently misparses every `reg` property.
- **Overlapping memory regions.** If the DTB is placed at an address inside a declared `memory` node, the kernel may overwrite it during boot.
- **Missing interrupt parent.** Every device with an interrupt must reference an interrupt controller via `interrupt-parent` — forgetting this means the IRQ is never connected.

> **Interview answer:** The device tree is a binary data structure (DTB) passed by the bootloader in register `a1`; it describes hardware layout (memory, peripherals, interrupts) so the kernel can discover and configure devices without hardcoded addresses.
