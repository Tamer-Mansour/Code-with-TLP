# The Boot Sequence Step by Step

The boot sequence is the ordered chain of events that transforms a powered-off machine into a running operating system. Each stage has a specific responsibility and passes control to the next stage in a carefully defined way.

## The Complete Boot Chain

```
Power Button Pressed
        │
        ▼
1. Hardware Reset
        │
        ▼
2. Firmware Execution (BIOS / UEFI)
   - Reset vector fetch (0xFFFF0)
   - CAR (Cache-as-RAM) setup
   - DRAM training & init
   - POST (Power-On Self-Test)
   - PCIe / USB enumeration
   - Boot device selection
        │
        ▼
3. Bootloader Stage 1
   (MBR sector / UEFI application)
        │
        ▼
4. Bootloader Stage 2
   (GRUB menu, kernel/initramfs load)
        │
        ▼
5. Kernel Decompression & Early Init
   - Decompress vmlinuz
   - Setup page tables, GDT, IDT
   - start_kernel()
        │
        ▼
6. initramfs / initrd
   - Mount temporary root filesystem
   - Load essential drivers (disk, crypto, LVM)
   - Pivot to real root filesystem
        │
        ▼
7. Init System (systemd / SysV init)
   - PID 1 starts
   - Mounts filesystems, starts services
        │
        ▼
8. User Space Ready (login prompt / desktop)
```

**Interview answer:** The boot sequence is: power-on → firmware POST → bootloader (stage 1 → stage 2) → kernel decompression and early init → initramfs → init system → user space.

## Step 1: Hardware Reset

The power supply asserts the PWRGOOD signal only after voltages stabilize (typically 100–500 ms after the power button). The motherboard then releases the CPU reset line. This guarantees the CPU does not fetch garbage instructions during voltage ramp-up.

## Step 2: Firmware Execution

### BIOS Path

- CPU fetches from `0xFFFF0` → far JMP into BIOS ROM
- BIOS runs POST, builds an **BIOS Data Area** (BDA) at `0x0400`
- BIOS constructs a **drive parameter table** and fills the interrupt vector table
- BIOS reads sector 0 of the boot device into `0x0000:0x7C00` and JMPs there

### UEFI Path

- CPU fetches from reset vector → SEC phase → PEI → DXE → BDS
- BDS reads `BootOrder` from NVRAM, loads the first valid `.efi` executable into memory as a PE32+ image
- Calls the EFI application's entry point with `(EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable)`

## Step 3 & 4: Bootloader

```bash
# GRUB 2 boot timeline (visible with GRUB_CMDLINE_LINUX="debug")
# 1. GRUB stage 1 (MBR) loads core.img
# 2. core.img reads grub.cfg from /boot/grub/
# 3. User selects a menu entry (or timeout fires)
# 4. GRUB reads vmlinuz and initrd into RAM
# 5. GRUB calls 'boot' command

# You can inspect what GRUB does at runtime:
$ grub-install --dry-run /dev/sda   # shows install plan
$ update-grub                        # regenerates grub.cfg
```

Key actions:
- Parse `grub.cfg` to find kernel path and parameters
- Use BIOS `INT 13h` (extended) or UEFI file protocol to read the kernel file
- Place `vmlinuz` at a kernel-specified load address (typically ~1 MB for 32-bit, or as specified in the kernel header)
- Place `initrd` above the kernel, address passed via `boot_params`

## Step 5: Kernel Decompression and Early Init

Modern Linux kernels are compressed (`gzip`, `lz4`, or `zstd`). The kernel binary has a self-extracting stub:

```
vmlinuz structure:
┌─────────────────────────────────────────┐
│ boot sector / setup code (16-bit stub)  │
│ Protected-mode kernel (compressed)      │
│   → decompressor code                  │
│   → compressed payload (bzImage)       │
└─────────────────────────────────────────┘
```

The decompressor runs from a safe scratch area, extracts the real kernel, then jumps to `startup_64`. From there:

- CPU mode: 64-bit long mode
- Set up initial page tables (identity-map early memory)
- Set up IDT (interrupt descriptor table) with early handlers
- Call `start_kernel()` — this is where C code begins

## Step 6: initramfs

The kernel cannot mount the real root filesystem without drivers that may live *on* that filesystem (a chicken-and-egg problem). The solution is an initial RAM filesystem (`initramfs`):

```bash
# Inspect initramfs contents
$ mkdir /tmp/init && cd /tmp/init
$ zcat /boot/initrd.img-$(uname -r) | cpio -idm
$ ls
# bin/  dev/  etc/  init  lib/  scripts/  usr/
```

The kernel extracts `initramfs` to a `tmpfs` root, runs `/init` (a shell script or binary), which loads drivers, assembles RAID/LVM/encrypted volumes, then executes `switch_root` to replace the `tmpfs` root with the real root filesystem.

## Step 7: Init System

PID 1 (`/sbin/init` → symlink to `systemd` on modern distros) is the first user-space process. It never exits while the system is running. `systemd` reads unit files from `/etc/systemd/system/` and `/lib/systemd/system/`, resolves dependencies, and starts services in parallel.

```bash
# Visualize the boot timeline
$ systemd-analyze plot > boot.svg
$ systemd-analyze blame | head -10

# Check what slowed down your last boot
$ journalctl -b | grep "Startup finished"
```

## Timing a Real Boot

| Phase | Typical Duration |
|-------|-----------------|
| POST | 1–8 seconds |
| Bootloader menu | 0–5 seconds (timeout) |
| Kernel decompress | 0.1–0.5 seconds |
| initramfs | 0.5–3 seconds |
| systemd to login | 2–15 seconds |

## Common Pitfalls

- Confusing **initrd** (older, ext2 image) with **initramfs** (newer, cpio archive) — both serve the same purpose but are handled differently by the kernel.
- Assuming the kernel mounts the real root directly — it always goes through initramfs on modern systems.
- Missing drivers in initramfs after adding new hardware — run `update-initramfs -u` (Debian/Ubuntu) or `dracut -f` (RHEL/Fedora) to rebuild.
