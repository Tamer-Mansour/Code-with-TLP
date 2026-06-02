# RISC-V Boot Stages: ZSBL, FSBL, BBL

Modern RISC-V systems use a layered boot architecture. Rather than one monolithic bootloader, responsibility is divided across several distinct stages — each stage sets up the environment and hands control to the next. This graduated handoff simplifies code at every level and allows each stage to run with only the resources it absolutely needs.

## The Three Classic Stages

| Stage | Name | Runs from | Role |
|-------|------|-----------|------|
| ZSBL | Zero Stage Boot Loader | Mask ROM (on-chip) | Initialize minimal hardware, locate FSBL |
| FSBL | First Stage Boot Loader | On-chip SRAM or NOR flash | Initialize DRAM, load second-stage image |
| BBL / OpenSBI | Berkeley Boot Loader / OpenSBI | DRAM | Set up M-mode firmware, jump to OS |

After BBL/OpenSBI comes the OS bootloader (U-Boot, GRUB) and then the kernel itself.

## ZSBL — Zero Stage Boot Loader

The ZSBL lives in read-only mask ROM — the code is baked into the chip at tape-out and cannot be changed. Its responsibilities are intentionally minimal:

- Sample boot-mode selection pins (SPI flash, SD card, JTAG, etc.).
- Initialize just enough of the memory subsystem to reach the FSBL storage medium.
- Optionally verify a signature on the FSBL image.
- Copy or jump to the FSBL.

Because mask ROM is expensive and immutable, the ZSBL is kept as small as possible — sometimes fewer than 256 instructions.

## FSBL — First Stage Boot Loader

The FSBL executes from SRAM or XIP (execute-in-place) NOR flash. It has more room and can do heavier lifting:

- **DRAM initialization** — configure DDR PHY and controller, run training sequences, verify memory is functional.
- **Clock and PLL configuration** — switch CPU and bus clocks to full operating frequency.
- **Peripheral initialization** — enable UART for debug output (this is usually the first time you see serial output).
- **Loading the next stage** — read BBL/OpenSBI from flash or SD card into DRAM.

A typical FSBL UART banner might look like:

```
[FSBL] SoC rev 0x21, 2 GB LPDDR4 detected
[FSBL] Loading OpenSBI from SPI flash offset 0x100000 ...
[FSBL] Verifying SHA-256 ... OK
[FSBL] Jumping to 0x80000000
```

## BBL — Berkeley Boot Loader

BBL (from the RISC-V tools project, now largely replaced by OpenSBI) was the reference implementation of M-mode firmware for RISC-V. It:

- Ran in machine mode (M-mode) as a permanent firmware layer.
- Provided SBI (Supervisor Binary Interface) calls that the kernel invokes via `ecall`.
- Set up the Physical Memory Protection (PMP) unit.
- Transferred control to the S-mode kernel.

BBL is largely historic today, but understanding it helps clarify why OpenSBI exists.

## SBI — The Glue Between Layers

The **Supervisor Binary Interface** is a standard API between M-mode firmware and the S-mode operating system. It works like a system call but in the opposite privilege direction:

```asm
# Kernel (S-mode) calls SBI to print a character
li a7, 0x01       # SBI extension: console putchar
li a6, 0          # function ID
li a0, 'H'        # argument: character to print
ecall             # trap into M-mode firmware
```

This abstraction lets the same Linux kernel image boot on different RISC-V silicon as long as the M-mode firmware implements SBI correctly.

## Why Stage Separation Matters

- **Mutability.** Each stage beyond the ZSBL can be updated in the field without changing the chip.
- **Failure isolation.** If DRAM training fails in the FSBL, it can retry or fall back without corrupting the ZSBL.
- **Security.** Each stage can verify the next (chain of trust / secure boot).
- **Portability.** The OS only ever talks to SBI; it does not need to know the details of any earlier stage.

## Common Pitfalls

- Confusing "boot ROM" (the ZSBL in mask ROM) with "boot flash" (where the FSBL lives).
- Assuming the FSBL runs from DRAM — it typically runs from SRAM before DRAM is initialized.
- Forgetting that every stage must set up its own stack before calling any C code.

> **Interview answer:** RISC-V boot proceeds through ZSBL (mask ROM, minimal HW init) → FSBL (DRAM init, clock setup) → BBL/OpenSBI (M-mode firmware, SBI interface) → OS kernel; each stage initializes what the next stage needs.
