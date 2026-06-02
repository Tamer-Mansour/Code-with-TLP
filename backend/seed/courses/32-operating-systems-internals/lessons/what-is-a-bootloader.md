# What Is a Bootloader?

A bootloader is the first piece of software the firmware hands control to. Its job is deceptively simple: find the OS kernel, load it into memory, set up the environment the kernel expects, and jump to it. In practice, bootloaders handle disk formats, file systems, cryptography, multi-OS menus, and hardware quirks — making them surprisingly complex programs.

## Why We Need a Bootloader

The firmware (BIOS or UEFI) is generic — it knows nothing about Linux ext4 or Windows NTFS. It hands control to a small, disk-specific program that *does* understand those formats. That program is the bootloader.

**Interview answer:** A bootloader is the software bridge between firmware and the OS kernel — it locates the kernel image on disk, loads it into RAM, passes a command line and hardware description, then transfers control to the kernel entry point.

## The Two-Stage Problem

Legacy BIOS hands 512 bytes of code (the MBR) to the CPU. 512 bytes is not enough to implement a file system driver. The classic solution is a **two-stage bootloader**:

- **Stage 1 (MBR):** Exactly 446 bytes of code. Its only job: find and load Stage 2 from a known disk location.
- **Stage 2:** A full-featured program that can read a file system, display a menu, load a kernel, and parse configuration files.

GRUB 2 extends this to 1.5 stages: the MBR boot code loads a small `core.img` embedded between the MBR and the first partition. `core.img` contains just enough code to read GRUB's configuration from a GRUB-formatted partition.

```
Disk layout (MBR scheme):
┌──────────────────────────────────────────────────────────┐
│ Sector 0: MBR (446 B code + 64 B part table + 2 B sig)  │
│ Sectors 1-2047: Gap where GRUB core.img lives            │
│ Sector 2048+: Partitions                                 │
└──────────────────────────────────────────────────────────┘
```

## Common Bootloaders

| Bootloader | Platform | Notes |
|------------|----------|-------|
| GRUB 2 | Linux (BIOS + UEFI) | Most common; reads ext4/XFS/Btrfs; chainloads |
| systemd-boot | Linux (UEFI only) | Simple, fast; reads only FAT32 ESP |
| Windows Boot Manager | Windows (UEFI) | Reads BCD store; loads `winload.efi` |
| rEFInd | UEFI multi-boot | Auto-detects EFI executables; good for Mac |
| SYSLINUX / ISOLINUX | BIOS; CD/USB | Common for installer media |
| U-Boot | Embedded/ARM | Dominant on development boards |
| coreboot + SeaBIOS | Open-source firmware | Replaces vendor BIOS on supported hardware |

## What a Bootloader Must Do

1. **Find the kernel** — parse a config file (`/boot/grub/grub.cfg`, `/boot/loader/entries/*.conf`) to determine which kernel image and initramfs to load.
2. **Load the kernel** — read the kernel binary (`vmlinuz`) into a physically contiguous region of RAM.
3. **Load the initramfs** — the initial RAM filesystem the kernel uses before the real root is mounted.
4. **Prepare the kernel command line** — pass arguments like `root=/dev/sda2 ro quiet splash`.
5. **Set up a boot information structure** — BIOS bootloaders fill a **boot_params** struct; UEFI bootloaders pass the `EFI_SYSTEM_TABLE` pointer.
6. **Jump to the kernel entry point** — for x86 Linux, this is the `startup_32` or `startup_64` function in `arch/x86/boot/`.

```c
// Simplified: how a UEFI bootloader jumps to the kernel
typedef void (*kernel_entry_t)(boot_params_t *params);

kernel_entry_t entry = (kernel_entry_t) kernel_load_address;
entry(&boot_params);   // kernel takes over; bootloader never returns
```

## GRUB 2 Configuration Example

```bash
# /boot/grub/grub.cfg (simplified)
set default=0
set timeout=5

menuentry "Ubuntu 24.04 LTS" {
    linux   /vmlinuz-6.8.0-31-generic root=/dev/sda2 ro quiet splash
    initrd  /initrd.img-6.8.0-31-generic
}

menuentry "Windows 11" {
    chainloader /EFI/Microsoft/Boot/bootmgfw.efi
}
```

**Chainloading** means handing control to another bootloader (e.g., Windows Boot Manager) instead of loading a kernel directly.

## Bootloader Security Considerations

A compromised bootloader can load a malicious kernel before the OS has any chance to defend itself. Threats include:

- **Evil maid attacks** — physical access, replace bootloader on disk
- **Cold boot attacks** — dump keys from DRAM after reboot
- **Bootkits** — malware that infects the MBR or EFI partition

Secure Boot and measured boot (TPM) are the primary defenses. The firmware verifies the bootloader's signature before executing it.

## Common Pitfalls

- After updating a kernel, forgetting to run `update-grub` (or `grub-mkconfig`) — the old kernel entry remains and the new one is missing.
- Installing GRUB to the wrong device (`/dev/sda1` instead of `/dev/sda`) — Stage 1 ends up in the partition boot record, not the MBR, and the system may not boot.
- On UEFI systems, expecting GRUB to "just work" after copying files without creating an NVRAM boot entry.
