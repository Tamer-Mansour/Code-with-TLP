# What Is Firmware and Where Does It Live?

Firmware is the software permanently stored in a device's non-volatile memory that provides the low-level control logic for the hardware it runs on. It is neither pure hardware nor a traditional application: it is the layer that makes hardware useful.

The word comes from its position in the software stack — harder to change than ordinary software ("software"), but softer than logic etched into silicon ("hardware").

## Where Firmware Lives

Firmware is stored in **non-volatile memory** so that it survives power cycles without a battery. The storage medium depends on the device generation and cost constraints:

| Storage Type | Characteristics | Typical Use |
|---|---|---|
| Mask ROM | Written at fabrication, immutable | Ancient or safety-critical, ultra-low-cost |
| NOR Flash | Execute-in-place (XIP), byte-addressable | MCU program flash, BIOS/UEFI |
| NAND Flash | High density, page/block access | Storage, bootloaders on application processors |
| EEPROM | Small, byte-writable, slow | Configuration data, calibration tables |
| OTP (One-Time Programmable) | Fused once, tamper-resistant | Secure boot keys, device identity |

Modern MCUs typically store firmware in **on-chip NOR flash**. The CPU fetches instructions directly from flash (execute-in-place) without copying them to RAM first, which saves memory at the cost of slightly slower instruction fetch.

## The Memory Map Perspective

At runtime, a microcontroller's address space is divided into regions:

```
0xFFFFFFFF ┌─────────────────────────┐
           │   Vendor-specific       │
0xE0000000 ├─────────────────────────┤
           │   Cortex-M PPB (debug)  │
0x40000000 ├─────────────────────────┤
           │   Peripherals (MMIO)    │
0x20000000 ├─────────────────────────┤
           │   SRAM (stack/heap/BSS) │
0x08000000 ├─────────────────────────┤
           │   Flash (firmware code) │ ← firmware lives here
0x00000000 └─────────────────────────┘
```

The interrupt vector table is at the very bottom of flash. Before `main()` runs, startup code (typically in assembly) sets up the stack pointer, clears BSS, and copies `.data` from flash to SRAM.

## What Firmware Does

Firmware typically handles:

- **Hardware abstraction** — wrapping register-level peripheral access behind function calls.
- **Startup and initialisation** — clock configuration, peripheral init, bootloader handoff.
- **Interrupt service routines (ISRs)** — responding to hardware events with minimal latency.
- **Application logic** — the actual product behaviour (sensor polling, control loops, communication stacks).
- **Bootloader** — in a two-stage design, a small bootloader in protected flash validates and launches the main firmware image. This enables field updates (OTA/DFU).

## Updating Firmware

Unlike application software, firmware updates require writing to flash — a hardware operation. Modern devices support:

- **JTAG/SWD** — debug interface used during development.
- **DFU (Device Firmware Update)** over USB or UART — in-field programming.
- **OTA (Over-The-Air)** — wireless update, critical for IoT devices at scale.

A two-bank (A/B) flash layout lets the device boot from bank A while writing the update to bank B, then atomically swap. This prevents bricking on a failed update.

## Common Pitfalls

- **No update mechanism.** Shipping without OTA means a bug fix requires physical access or a recall.
- **Unprotected bootloader.** If the bootloader flash region is not write-protected, a firmware bug can corrupt the bootloader, permanently bricking the device.
- **Forgetting flash endurance.** NOR flash supports ~10,000–100,000 erase cycles. Writing frequently to the same page (e.g., logging) will wear it out.

> **Interview answer:** Firmware is software stored in non-volatile memory (typically NOR flash) that provides low-level hardware control; it persists across power cycles, initialises the hardware at boot, and implements the device's core logic close to the metal.
