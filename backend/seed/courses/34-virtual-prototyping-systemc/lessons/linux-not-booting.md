# When Linux Won't Boot: A Triage Checklist

Booting Linux on a virtual prototype is a multi-stage process — bootloader, kernel decompression, device tree parsing, driver initialization, and userspace init — with many failure points. A systematic checklist prevents you from chasing the wrong stage for hours.

## The Boot Stages and Their Failure Signatures

| Stage | Expected output | Failure signature |
|---|---|---|
| Reset vector | CPU fetches from reset address | Hang at instruction 0, bad PC |
| Bootloader (U-Boot / Barebox) | `U-Boot 2024.01` banner | Blank console, early hang |
| Kernel decompression | `Uncompressing Linux...` | Hang after bootloader, no kernel banner |
| Kernel start | `Booting Linux on physical CPU 0x0` | Decompressed but no kernel output |
| Device tree parsing | `Machine model: My Board` | Kernel crash early in `start_kernel` |
| Driver initialization | Per-driver messages | Hang on specific `[    x.xxx]` line |
| Userspace | `Starting init...` | Kernel OK, user space hangs/panics |

## Checklist

### 1. Verify the Reset Vector

```
(gdb) break *0x00000000    # or wherever your SoC resets
(gdb) continue
(gdb) x/4i $pc
```

If gdb never hits the breakpoint, the CPU is not fetching from the reset address. Check:
- Is the ROM image loaded at the right address?
- Is the memory map correct in the VP?

### 2. Confirm UART is Working

Almost all boot failures look identical — a blank console — if the UART model is wrong. Test the UART in isolation first:

```bash
# Load a tiny bare-metal "hello" binary first
# If UART works, you'll see output. If not, fix UART before continuing.
```

A silent console is almost never a Linux bug — it is almost always a UART misconfiguration.

### 3. Check the Device Tree

Linux's early boot depends entirely on the Device Tree Blob (DTB). Common errors:

- **Wrong `compatible` string** in the root node — Linux cannot find a machine match and panics.
- **Wrong `reg` property** for memory — Linux maps RAM incorrectly, causing an early page fault.
- **Missing `stdout-path`** in `/chosen` — early `printk` output goes nowhere.

```bash
# Decompile the DTB and verify:
dtc -I dtb -O dts my_board.dtb | grep -A5 "chosen"
dtc -I dtb -O dts my_board.dtb | grep "compatible"
```

### 4. Enable Early Kernel Printk

Add to the kernel command line:

```
earlycon=uart8250,mmio32,0x40010000,115200n8 earlyprintk
```

This activates `printk` before the UART driver is initialized, using a hardcoded MMIO address. If you see output up to a point and then silence, the crash is after that last message.

### 5. Check the Instruction Trace at Hang Point

Pause the simulation when it hangs. Extract the last 50 instruction trace entries:

```bash
tail -50 trace.log
```

If the PC oscillates between two addresses inside the kernel, it is a spin loop — likely waiting for an interrupt from a driver (MMC, PCI, clock driver).

### 6. Verify Clock and Timer

Linux's `calibrate_delay` function spins the CPU counting loops. If the timer model returns incorrect values or never fires, this calibration loop runs forever:

```
Calibrating delay loop...
```

Check that your timer peripheral:
- Has the correct base address in the DTB.
- Fires an interrupt at the configured rate.
- Has the interrupt line wired to the interrupt controller.

### 7. Check Memory Size

If the VP's RAM size does not match the DTB `memory` node, Linux may try to access unmapped addresses:

```
/ {
    memory@20000000 {
        reg = <0x20000000 0x08000000>;  /* 128 MB */
    };
};
```

Cross-check with the VP's actual RAM size. A mismatch causes random faults during kernel page-table setup.

### 8. Kernel Oops and Panic Messages

If you do get kernel output, look for:

```
Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(0,0)
```
- Root filesystem not found. Check `root=` in the kernel command line.

```
Unable to handle kernel NULL pointer dereference
```
- A driver crashed. The `PC` line in the oops points to the exact kernel function.

```
---[ end Kernel panic - not syncing: Attempted to kill init! ]---
```
- Userspace init exited. Check the rootfs and `/sbin/init`.

## Quick Decision Tree

```
Console silent?
  → Fix UART first, then retry

Bootloader prints but no kernel?
  → Check kernel load address and entry point

Kernel prints but hangs on calibrate_delay?
  → Fix timer interrupt

Kernel panics on driver init?
  → Check DTB reg addresses for that driver

Kernel OK but userspace fails?
  → Check rootfs image and init binary
```

> **Interview answer:** "I start with the UART model because a silent console hides every other bug, then work stage by stage — reset vector, bootloader, kernel decompression, DTB parsing, driver init — using early printk and the instruction trace to pinpoint exactly where boot stops."
