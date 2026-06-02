# The RISC-V Physical Memory Map

RISC-V does not mandate a fixed physical memory layout — the specification intentionally leaves the physical address space platform-defined. This flexibility lets the same ISA serve tiny microcontrollers and warehouse-scale servers. Understanding what *is* standardized and what is left to the platform is the first step to writing correct bare-metal or OS-level code.

## What the Spec Defines

RISC-V specifies address widths (32-bit for RV32, 34-bit for RV32 with Sv32, 56-bit for RV64 with Sv48, etc.) and a handful of reserved regions, but the physical memory map itself comes from the **platform specification** or a **Device Tree Blob (DTB)** passed at boot.

Key facts:

- Address `0x0` is *not* guaranteed to be RAM or ROM.
- The machine can boot from any physical address; the reset vector is platform-defined.
- The RISC-V Privileged Spec defines *no* mandatory I/O addresses — everything is MMIO and platform-specific.

## Typical SiFive/QEMU virt Platform Layout

The QEMU `virt` machine (widely used for OS development) gives a concrete example:

| Region | Base Address | Notes |
|---|---|---|
| Debug / ROM | `0x0000_0000` | Tiny on-chip ROM, holds reset vector |
| CLINT | `0x0200_0000` | Core-Local Interrupt Controller |
| PLIC | `0x0C00_0000` | Platform-Level Interrupt Controller |
| UART0 | `0x1000_0000` | 16550-compatible serial port |
| Flash / ROM | `0x2000_0000` | Optional SPI NOR flash |
| DRAM | `0x8000_0000` | Main system RAM |

The exact sizes and presence of regions vary by platform. Always consult the DTB or the board reference manual.

## DRAM Placement

Most RISC-V platforms place DRAM at or above `0x8000_0000`. This is a convention inherited from early RISC designs and leaves the lower 2 GiB free for MMIO and firmware ROM — crucial for 32-bit systems where the total address space is only 4 GiB.

```asm
# Typical linker script origin for a RISC-V bare-metal kernel
MEMORY {
  ROM   (rx)  : ORIGIN = 0x20000000, LENGTH = 4M
  DRAM  (rwx) : ORIGIN = 0x80000000, LENGTH = 128M
}
```

## The Reset Vector

When power is applied (or a reset occurs), the hart (hardware thread) fetches its first instruction from the **reset vector**. On SiFive cores this is typically `0x0000_1000` (inside the on-chip ROM), which contains a jump to `0x8000_0000` where the firmware or bootloader lives. The OpenSBI firmware then sets up supervisor mode and hands off to the OS kernel.

## Common Pitfalls

- **Assuming DRAM at address 0.** Writing to address `0x0` often hits ROM or an unmapped region, causing a store-access fault.
- **Hard-coding UART addresses.** Always read from the DTB or platform header so your driver works across boards.
- **Forgetting fence instructions.** Reads/writes to MMIO regions must be ordered with `fence` instructions; the CPU and memory system are allowed to reorder accesses to normal DRAM.

## Interview Answer

> "RISC-V has no mandatory physical memory map. The platform spec or DTB defines what lives at each address. Typical platforms put DRAM at `0x8000_0000` and MMIO devices below it; the reset vector points to a small on-chip ROM that jumps to the firmware."
