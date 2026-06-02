# Power-On, the Reset Vector, and POST

The instant you press the power button, a carefully choreographed sequence of hardware events begins — long before any OS code runs. Understanding this sequence is essential for debugging boot failures and for systems programming interviews.

## The Reset Signal

When power is applied (or the reset pin is asserted), the CPU's internal state is driven to a defined reset state. For x86:

- All registers are set to hardcoded reset values
- `CS` (Code Segment) = `0xF000`, `EIP` = `0xFFF0`
- The effective physical address = `(CS << 4) + EIP` = `0xFFFF0`

This is the **reset vector** — the first instruction the CPU fetches after power-on.

**Interview answer:** The reset vector is the hardcoded physical address (`0xFFFF0` on x86) where the CPU fetches its very first instruction after reset.

## Why 0xFFFF0?

With a 20-bit address bus (real mode), the top of the 1 MB address space is `0xFFFFF`. The reset vector at `0xFFFF0` is just 16 bytes from the top, so the firmware ROM must be mapped to the top of that address space. Those 16 bytes almost always contain a single far `JMP` instruction that jumps to the actual firmware code body:

```asm
; Reset vector contents (simplified)
0xFFFF0:  JMP FAR 0xF000:0xE05B   ; jump into main BIOS code
```

On UEFI systems the same mechanism applies, but the firmware quickly transitions to 32-bit (or 64-bit) protected mode after the initial real-mode stub.

## Power-On Self-Test (POST)

POST is the firmware's hardware validation phase. It runs before any bootable device is examined.

### POST Stages

1. **CPU test** — verify that basic registers, ALU, and flags work correctly
2. **Cache init** — initialize L1/L2 caches; use cache-as-RAM (CAR) technique before DRAM is available
3. **Memory controller init** — configure DRAM timing, detect DIMMs, train the memory bus
4. **Memory test** — write and read-back patterns to detect faulty cells
5. **Chipset init** — configure PCIe lanes, USB controllers, SATA, power management
6. **Video init** — initialize GPU firmware (VBIOS/GOP), set up framebuffer
7. **Peripheral discovery** — enumerate PCI/PCIe devices
8. **Boot device selection** — check for bootable media in the configured boot order

### POST Codes

During POST, the firmware writes progress codes to I/O port `0x80`. A POST card (or the motherboard's LED display) shows these codes. When a machine hangs mid-POST, the code tells you exactly which stage failed.

```bash
# On a running Linux system, you can read the last POST code via
# some embedded controllers (vendor-specific):
$ cat /sys/class/watchdog/watchdog0/state
```

### POST Beep Codes

If the video subsystem fails (or no display is present) the firmware signals errors via beep codes through the PC speaker. Classic AMI BIOS, Award BIOS, and Phoenix each have different beep patterns.

| Beeps (AMI) | Meaning |
|-------------|---------|
| 1 short | POST passed, about to boot |
| 2 short | Memory error |
| 3 long | Keyboard controller failure |
| Continuous | RAM not detected |

## Cache-as-RAM (CAR)

A subtle problem: the CPU needs a stack (for calling C functions) before DRAM is initialized. The solution is to configure a small region of L2 cache to behave as RAM — writes go to cache lines that are never evicted. This technique, called **Cache-as-RAM** or **No-Eviction Mode**, is used in coreboot and most modern UEFI firmware.

```
Power On
   │
   ▼
CPU reset → fetch from reset vector (0xFFFF0)
   │
   ▼
CAR setup (use L2 cache as stack/heap)
   │
   ▼
DRAM training & test
   │
   ▼
Full memory available → copy firmware to RAM, switch stack
   │
   ▼
POST: enumerate PCI, init video, test peripherals
   │
   ▼
Hand off to bootloader
```

## Common Pitfalls

- Assuming DRAM is available at reset — it is not; the first firmware code runs entirely in cache or on-chip SRAM.
- Forgetting that `0xFFFF0` is a real-mode address; above 1 MB, the chip uses memory-mapped IO ranges that the firmware unmaps once DRAM is ready.
- Confusing POST failure (hardware fault) with boot failure (bootloader/OS issue) — POST failures typically occur before any disk is read.

## Worked Example: Tracing a POST Hang

A machine powers on but shows a blank screen and emits three long beeps (AMI BIOS). Steps to diagnose:

1. Count beeps: 3 long = keyboard controller fault (or USB init failure on newer firmware).
2. Reseat USB devices; try with only keyboard plugged in.
3. If hang persists, read POST code 0x80 via POST card — code `0xB2` might indicate USB init failure.
4. Update firmware if a known bug exists for that POST code on that board revision.
