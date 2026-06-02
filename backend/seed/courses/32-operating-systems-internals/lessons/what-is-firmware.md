# What Is Firmware? ROM, BIOS, and UEFI

Firmware sits in the gap between hardware and software. It is persistent code stored on non-volatile memory chips that runs before the operating system ever loads. Without firmware, a CPU has no idea what to execute when power is applied.

## Why Firmware Exists

A freshly powered CPU can fetch and execute instructions, but it cannot load an OS by itself — the OS lives on a disk, and the CPU has no built-in knowledge of disk formats, memory controllers, or display hardware. Firmware bridges that gap. It initializes hardware to a known state, performs self-tests, and then hands off execution to a bootloader.

**Interview answer:** Firmware is persistent low-level software stored on ROM or flash that initializes hardware and locates a bootloader on power-on.

## Storage Media: ROM, EEPROM, and Flash

| Type | Writable? | Typical Use |
|------|-----------|-------------|
| Mask ROM | No | Factory-burned; cheapest; used in microcontrollers |
| EEPROM | Byte-by-byte via high voltage | Legacy BIOS chips |
| NOR Flash | Sector-erase + byte-read | Modern BIOS/UEFI firmware |
| NAND Flash | Page-erase + page-read | Mass storage; too slow for execute-in-place |

Modern UEFI firmware lives on an SPI NOR flash chip soldered to the motherboard. Many vendors allow firmware updates via a signed image flashed by a utility or via the UEFI shell itself.

## BIOS: The Classic Firmware

**BIOS** (Basic Input/Output System) was the original IBM PC firmware, introduced in 1981. It:

- Runs in 16-bit real mode on x86
- Uses a fixed entry point at physical address `0xFFFF0` (just below 1 MB)
- Provides software interrupts (`INT 10h` for video, `INT 13h` for disk) that DOS and early bootloaders relied on
- Stores boot configuration in a small battery-backed CMOS RAM (64–256 bytes)
- Is limited to booting from the first 2 TB of storage (MBR partition scheme)

The BIOS interrupt table is a vector at the bottom of real-mode memory (`0x0000:0x0000`). Each 4-byte entry holds a segmented address pointing to a handler.

```asm
; Legacy BIOS call: read sector via INT 13h
mov ah, 0x02    ; function: read sectors
mov al, 1       ; number of sectors
mov ch, 0       ; cylinder 0
mov cl, 1       ; sector 1 (1-indexed)
mov dh, 0       ; head 0
mov dl, 0x80    ; drive: first HDD
mov bx, 0x7C00  ; ES:BX = destination buffer
int 0x13        ; call BIOS
```

## UEFI: Modern Firmware

**UEFI** (Unified Extensible Firmware Interface) replaced BIOS starting around 2005–2010. Key improvements:

- Runs in 32-bit or 64-bit protected mode — no 1 MB memory ceiling during firmware execution
- Rich C-based API accessible through protocol GUIDs and function tables
- Supports GPT partition tables (disks > 2 TB, up to 128 partitions)
- Has a built-in shell, network stack, and driver model
- Enables **Secure Boot**: cryptographic verification of each boot stage
- Stores configuration in **NVRAM** variables (accessible via `efivarfs` on Linux)

```bash
# Inspect UEFI variables from Linux
ls /sys/firmware/efi/efivars/
efivar --list | head -10

# Read BootOrder variable
efivar -n 8be4df61-93ca-11d2-aa0d-00e098032b8c-BootOrder
```

## Firmware vs. Driver vs. OS

```
Power On
   │
   ▼
Firmware (BIOS/UEFI)  ← stored on SPI flash; initializes CPU, RAM, PCIe
   │
   ▼
Bootloader (GRUB/systemd-boot/Windows Boot Manager)
   │
   ▼
Kernel  ← loads device drivers, mounts root filesystem
   │
   ▼
Init (systemd/SysV)
```

## Common Pitfalls

- Confusing "BIOS" with any firmware — many people still say "BIOS" when they mean UEFI.
- Assuming BIOS calls are available under UEFI — UEFI runs in protected/long mode; legacy BIOS interrupts do not exist unless a Compatibility Support Module (CSM) is enabled.
- Forgetting that UEFI variables are persistent across reboots and can affect boot order.

## Worked Example: Reading UEFI Boot Order

```bash
# efibootmgr shows boot entries stored in NVRAM
$ efibootmgr -v
BootCurrent: 0001
BootOrder: 0001,0000,0002
Boot0000* Windows Boot Manager
Boot0001* ubuntu
Boot0002* UEFI Shell
```

Each `Boot####` entry holds a device path. `BootOrder` controls which entry is tried first. This data survives power cycles because it sits in flash-backed NVRAM, not DRAM.
