# BIOS vs UEFI

BIOS and UEFI are the two generations of PC firmware. Knowing their differences matters for bootloader development, disk partitioning, Secure Boot, and OS installation troubleshooting.

## At a Glance

| Feature | Legacy BIOS | UEFI |
|---------|------------|------|
| Year introduced | 1981 (IBM PC) | 2005 (Intel EFI spec) |
| CPU mode at boot | 16-bit real mode | 32/64-bit protected mode |
| Max boot disk size | 2 TB (MBR limit) | 9.4 ZB (GPT limit) |
| Max partitions | 4 primary (MBR) | 128 (GPT default) |
| Boot config storage | CMOS RAM (battery-backed) | NVRAM variables (flash) |
| Driver model | Interrupt-based (INT 10h, 13h…) | Protocol/GUID-based C API |
| Secure Boot | No | Yes (optional) |
| Network boot | PXE via option ROM | Supports HTTP/HTTPS, IPv6 |
| Update mechanism | Flash utility (risky) | Signed capsule updates |

**Interview answer:** BIOS is a 16-bit real-mode firmware limited to 2 TB disks and 4 partitions; UEFI is a 32/64-bit firmware with GPT support, a richer API, and optional Secure Boot.

## BIOS Deep Dive

BIOS presents its services through **software interrupts**. When the bootloader or DOS needed to read a disk sector, it set up registers and issued `INT 13h`. The CPU looked up the handler address in the interrupt vector table (IVT) at `0x0000:0x0000` and jumped there.

```asm
; Read first sector of drive 0x80 (first HDD) into 0x0000:0x7C00
mov ah, 0x02    ; BIOS read sectors function
mov al, 0x01    ; read 1 sector
mov ch, 0x00    ; cylinder 0
mov cl, 0x01    ; sector 1
mov dh, 0x00    ; head 0
mov dl, 0x80    ; drive 0x80 = first HDD
xor bx, bx
mov es, bx
mov bx, 0x7C00  ; destination buffer
int 0x13
jc  disk_error  ; carry flag set on error
```

Limitations:
- All BIOS calls require real mode or a virtual-8086 mode transition (expensive under a 32-bit OS)
- No concept of drivers; every machine has the same fixed interrupt numbers
- Boot code must fit in a 512-byte MBR sector

## UEFI Deep Dive

UEFI replaces interrupt-based calls with a **system table** — a C struct containing pointers to protocol interfaces. Firmware, bootloaders, and drivers communicate through GUIDs and function pointers.

```c
// Simplified UEFI hello world
EFI_STATUS efi_main(EFI_HANDLE image, EFI_SYSTEM_TABLE *st) {
    st->ConOut->ClearScreen(st->ConOut);
    st->ConOut->OutputString(st->ConOut, L"Hello from UEFI!\r\n");
    return EFI_SUCCESS;
}
```

### UEFI Boot Process

1. SEC (Security) — very first code; sets up CAR (cache-as-RAM)
2. PEI (Pre-EFI Initialization) — initializes memory, chipset
3. DXE (Driver Execution Environment) — loads drivers from firmware volumes; builds the protocol database
4. BDS (Boot Device Selection) — checks `BootOrder` NVRAM variable, tries each entry
5. TSL (Transient System Load) — bootloader runs as a UEFI application
6. RT (Runtime) — kernel runs; UEFI runtime services still available (time, NVRAM, reset)

```
SEC → PEI → DXE → BDS → TSL (bootloader) → OS kernel
                                              ↓
                                    RT services remain
```

### UEFI Applications and the ESP

UEFI bootloaders are **PE32+ executables** (the same format as Windows .exe files) stored in the **EFI System Partition (ESP)** — a FAT32 partition with GUID `C12A7328-F81F-11D2-BA4B-00A0C93EC93B`.

```bash
# Mount and inspect the ESP on Linux
$ lsblk -o NAME,PARTTYPE,SIZE
$ mount /dev/sda1 /mnt/efi
$ find /mnt/efi -name "*.efi"
# Typical output:
# /mnt/efi/EFI/ubuntu/grubx64.efi
# /mnt/efi/EFI/Microsoft/Boot/bootmgfw.efi
# /mnt/efi/EFI/BOOT/BOOTX64.EFI   ← fallback path
```

The fallback path `\EFI\BOOT\BOOTX64.EFI` is tried when no `Boot####` NVRAM variable matches — useful for removable media.

## Compatibility Support Module (CSM)

Many UEFI implementations include a **CSM** that emulates legacy BIOS interrupts, allowing MBR-based bootloaders to run under UEFI. Enabling CSM disables Secure Boot. Most modern systems are shipping without CSM support ("UEFI only").

## Practical Considerations

- **Dual-boot setups** — both OSes must share the same firmware mode; mixing BIOS-installed Windows with UEFI-installed Linux on the same machine causes headaches.
- **Disk cloning** — cloning a UEFI system disk requires copying the ESP and updating NVRAM boot entries.
- **Rescue** — if NVRAM entries are corrupted, boot from removable media using the fallback EFI path and run `efibootmgr` to recreate entries.

```bash
# Create a new UEFI boot entry for GRUB
$ efibootmgr --create \
    --disk /dev/sda --part 1 \
    --label "ubuntu" \
    --loader '\EFI\ubuntu\grubx64.efi'
```

## Common Pitfalls

- Installing an OS in BIOS/MBR mode on a UEFI machine — it works (with CSM) but loses Secure Boot and GPT benefits.
- Forgetting that UEFI NVRAM entries are board-specific; moving a disk to a different machine may require recreating boot entries.
- Assuming all UEFI implementations are identical — vendors often add non-standard extensions or remove features like the built-in shell.
