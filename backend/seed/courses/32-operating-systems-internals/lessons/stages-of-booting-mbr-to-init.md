# Boot Stages: From MBR/GPT to init

This lesson drills into the on-disk structures that control booting — the MBR, the GPT, and the partition boot records — then traces how the bootloader reads them and ultimately delivers control to the init system.

## The Master Boot Record (MBR)

The MBR occupies **sector 0** of a disk — exactly 512 bytes. Its layout:

```
Offset  Size   Content
0x000   446 B  Boot code (Stage 1 bootloader)
0x1BE    64 B  Partition table (4 × 16-byte entries)
0x1FE     2 B  Boot signature: 0x55 0xAA
```

Each 16-byte partition entry contains:

```c
struct mbr_partition {
    uint8_t  status;        // 0x80 = bootable, 0x00 = not
    uint8_t  first_chs[3]; // CHS of first sector (legacy)
    uint8_t  type;          // partition type code (0x83=Linux, 0x82=swap…)
    uint8_t  last_chs[3];  // CHS of last sector (legacy)
    uint32_t lba_start;    // LBA of first sector
    uint32_t lba_size;     // number of sectors in partition
} __attribute__((packed));
```

The 2-byte `0x55AA` signature at offset 510 tells the BIOS this is a valid boot sector. If it is missing, the BIOS skips the device.

**Interview answer:** The MBR is the 512-byte sector 0 of a disk containing up to 446 bytes of boot code, a 4-entry partition table, and the `0x55AA` boot signature.

### MBR Limitations

- Only 4 **primary** partitions (one can be an **extended** partition containing logical partitions)
- Maximum disk size: 2 TB (32-bit LBA × 512-byte sectors = 2^32 × 512 = 2 TB)
- No redundancy — corruption of sector 0 is fatal

## The GUID Partition Table (GPT)

GPT is the modern replacement, defined by the UEFI spec. It resides at the start of the disk alongside a **Protective MBR** (a fake MBR that tells BIOS-era tools "this disk is in use").

```
Sector 0:  Protective MBR (type 0xEE spanning whole disk)
Sector 1:  GPT Header (primary)
Sectors 2–33: Partition entries (128 entries × 128 bytes each)
...
Sectors N-33 to N-1: Backup partition entries
Sector N:  GPT Header (backup)
```

Each GPT partition entry (128 bytes):

```c
struct gpt_partition {
    uint8_t  type_guid[16];   // partition type GUID
    uint8_t  unique_guid[16]; // unique partition GUID
    uint64_t start_lba;
    uint64_t end_lba;
    uint64_t attributes;      // bit 2 = required for platform
    uint16_t name[36];        // UTF-16 partition name
} __attribute__((packed));
```

GPT stores a CRC32 checksum of the header and partition table. Backup copies at the end of the disk allow recovery from corruption.

```bash
# Inspect GPT with gdisk
$ gdisk -l /dev/sda
GPT fdisk (gdisk) version 1.0.9
Disk /dev/sda: 1000215216 sectors, 476.9 GiB
Sector size (logical/physical): 512/4096 bytes
...
Number  Start (sector)    End (sector)  Size       Code  Name
   1            2048         1050623   512.0 MiB   EF00  EFI system partition
   2         1050624       975503359   464.8 GiB   8300  Linux filesystem
```

## The Volume Boot Record (VBR)

Each partition has its own **Volume Boot Record** (VBR) — the first sector of the partition. For MBR-scheme disks, when the BIOS loads MBR stage 1 code and that code wants to boot a specific partition, it reads the VBR and jumps to it.

The VBR contains file-system-specific boot code and a **BIOS Parameter Block (BPB)** describing the file system geometry (FAT32 VBRs contain a BPB; ext4 partitions use a different boot sector convention).

## GRUB's Boot Stages in Detail

```
Stage 1 (MBR sector, ≤446 bytes)
  │  Reads sector offset stored in its own code
  ▼
core.img (1.5-stage, typically in MBR gap sectors 1-2047)
  │  Contains: disk driver + filesystem driver + config reader
  │  Reads /boot/grub/grub.cfg
  ▼
grub.cfg parsed → user selects entry
  │
  ▼
GRUB reads vmlinuz + initrd into RAM
  │  Uses its built-in ext4/xfs/btrfs driver (no BIOS help needed)
  ▼
linux  command: sets up boot_params struct
initrd command: records initrd address in boot_params
boot   command: jumps to kernel
```

On **UEFI**, `grubx64.efi` is loaded directly as a PE32+ executable — there is no MBR, no stage 1, no gap trick. GRUB reads its config from the ESP.

## From Kernel to init

Once the kernel finishes early setup (page tables, interrupts, memory allocator), it:

1. Mounts `initramfs` as the root `tmpfs`
2. Runs `/init` in the initramfs (PID 1, but temporary)
3. `/init` loads kernel modules needed to access the real root (e.g., `ext4`, `ahci`, `dm-crypt`)
4. `/init` calls `switch_root /sysroot /sbin/init` — replaces the initramfs root with the real filesystem and executes the real init

```bash
# Inside initramfs /init (simplified dracut script excerpt):
mount -t ext4 /dev/sda2 /sysroot
exec switch_root /sysroot /sbin/init "$@"
```

`switch_root` does three things atomically:
- Deletes all files from the old initramfs root (frees RAM)
- Makes `/sysroot` the new root (`pivot_root` syscall internally)
- `exec`s the new init — PID 1 is now the real init

## systemd as PID 1

`systemd` reads **unit files** and their dependency graph:

```bash
# Key targets in systemd's boot graph:
# sysinit.target → basic.target → multi-user.target → graphical.target
$ systemctl list-dependencies multi-user.target --plain | head -15
```

Unit types relevant to boot:

| Unit Type | Example | Purpose |
|-----------|---------|---------|
| `.mount` | `boot.mount` | Mount filesystems |
| `.service` | `sshd.service` | Start daemons |
| `.target` | `multi-user.target` | Synchronization point |
| `.socket` | `dbus.socket` | Socket activation |
| `.device` | `dev-sda2.device` | udev device events |

## Common Pitfalls

- Forgetting that GRUB's `core.img` is installed in the MBR gap — resizing or creating a partition starting before sector 2048 will overwrite it and break boot.
- On GPT + BIOS systems, GRUB requires a dedicated **BIOS Boot Partition** (type `EF02`, ~1 MB) to embed `core.img` since there is no MBR gap in GPT layout.
- Confusing `switch_root` with `chroot` — `chroot` keeps the old root mounted; `switch_root` deletes it, reclaiming initramfs memory.
