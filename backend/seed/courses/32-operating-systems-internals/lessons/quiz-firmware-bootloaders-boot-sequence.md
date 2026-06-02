# Quiz: Firmware, Bootloaders, and the Boot Sequence

**Q1. What is the reset vector on x86 processors, and what does the CPU do with it?**

- [ ] The CPU reads the reset vector from NVRAM and loads the kernel directly.
- [ ] The CPU fetches the first instruction from physical address `0x00000` (the bottom of memory).
- [x] The CPU fetches its first instruction from physical address `0xFFFF0` (near the top of the 1 MB real-mode address space).
- [ ] The CPU waits for the BIOS to set the instruction pointer before executing anything.

> The reset vector is hardcoded in the CPU. On x86, CS=0xF000 and EIP=0xFFF0 after reset, giving physical address 0xFFFF0. This is where firmware ROM must be mapped so the very first instruction is fetched from there.

---

**Q2. Which of the following best describes the purpose of POST (Power-On Self-Test)?**

- [ ] POST loads the bootloader from the first bootable partition into memory.
- [ ] POST decompresses the Linux kernel image stored in firmware flash.
- [x] POST initializes and tests hardware components (CPU, RAM, PCIe, etc.) before attempting to boot.
- [ ] POST verifies the digital signatures of the bootloader and kernel using the TPM.

> POST is the firmware's hardware validation phase. It runs before any bootable device is touched. It includes DRAM training, PCI enumeration, and peripheral checks. Errors are signaled via POST codes or beep codes.

---

**Q3. A system administrator wants to boot from a 4 TB NVMe drive and use more than four primary partitions. Which combination is required?**

- [ ] Legacy BIOS firmware with an MBR partition scheme.
- [ ] Legacy BIOS firmware with a GPT partition scheme.
- [ ] UEFI firmware with an MBR partition scheme.
- [x] UEFI firmware with a GPT partition scheme.

> MBR limits disks to 2 TB (32-bit LBA × 512-byte sectors) and 4 primary partitions. GPT supports disks up to 9.4 ZB and 128 partitions by default. UEFI is required to natively boot from GPT without a Compatibility Support Module.

---

**Q4. In a UEFI Secure Boot chain, the UEFI firmware verifies the bootloader using a key stored in which NVRAM variable?**

- [ ] PK (Platform Key) — the firmware signs the bootloader directly with this key.
- [ ] KEK (Key Exchange Key) — the bootloader must be signed by this key.
- [x] db (Allowed Signature Database) — the bootloader's certificate or hash must appear here.
- [ ] dbx (Forbidden Signature Database) — the bootloader is verified against this revocation list.

> `db` contains the certificates and/or hashes of trusted EFI executables. Before executing a bootloader, UEFI checks its signature against `db`. `dbx` is a revocation list — if the bootloader's hash is in `dbx`, it is blocked even if it is also in `db`.

---

**Q5. What is the role of `initramfs` (initial RAM filesystem) during Linux boot?**

- [ ] It is a compressed copy of the kernel stored in NVRAM that UEFI loads before grub.
- [ ] It replaces systemd as PID 1 on systems without a graphical desktop.
- [x] It provides a temporary root filesystem with drivers and scripts to mount the real root filesystem.
- [ ] It is the partition table index that the kernel reads to find the root device.

> The kernel cannot mount the real root without filesystem and device drivers that may live on that root — a chicken-and-egg problem. `initramfs` is a cpio archive containing enough drivers and scripts to discover, unlock, and mount the real root, then hand off to the real init via `switch_root`.

---

**Q6. A GRUB 2 installation on a BIOS/MBR system embeds `core.img` in the "MBR gap". What is the MBR gap?**

- [ ] The 64-byte region inside the MBR reserved for the partition table.
- [x] The unpartitioned sectors between the MBR (sector 0) and the first partition (typically starting at sector 2048).
- [ ] A special partition of type `0xEF` that GPT uses to store the protective MBR.
- [ ] The last 2 bytes of the MBR that hold the `0x55AA` boot signature.

> By convention, most partitioning tools align the first partition to sector 2048 (1 MiB boundary), leaving sectors 1–2047 unused. GRUB 2 uses this space to embed `core.img` — its Stage 1.5 that contains the filesystem driver needed to read `grub.cfg` from `/boot/grub/`.
