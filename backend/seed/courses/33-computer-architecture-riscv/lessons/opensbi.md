# OpenSBI and the M-Mode Firmware Role

**OpenSBI** (Open Source Supervisor Binary Interface) is the reference M-mode firmware for RISC-V platforms. It replaced the older Berkeley Boot Loader (BBL) and is now the standard that Linux, FreeBSD, and other operating systems expect when running on RISC-V hardware.

## Why M-Mode Firmware Exists

RISC-V defines three privilege levels:

| Level | Name | Typical occupant |
|-------|------|-----------------|
| M | Machine | Firmware (OpenSBI) |
| S | Supervisor | OS kernel |
| U | User | Applications |

Machine mode is the most privileged — it has unrestricted access to all CSRs and physical memory. However, a general-purpose operating system should not run in M-mode because that would give it the ability to bypass all hardware protections. Instead, the OS runs in S-mode and calls into M-mode firmware through a well-defined interface (SBI) whenever it needs a privileged operation.

## The SBI Specification

The RISC-V SBI specification defines a set of **extensions** and **functions** the firmware must implement. The kernel issues an `ecall` instruction to invoke them:

```asm
# Example: SBI Hart State Management — stop (power off) this hart
li a7, 0x48534D   # Extension ID: "HSM"
li a6, 1          # Function ID: hart_stop
ecall
```

Important SBI extensions:

- **Base (0x10)** — probe which other extensions are available.
- **Timer (0x54494D45)** — set the hardware timer (`mtimecmp`).
- **IPI (0x735049)** — send inter-processor interrupts between harts.
- **RFNC (0x52464E43)** — remote fence instructions (TLB shootdowns).
- **HSM (0x48534D)** — start, stop, and suspend individual harts.
- **SRST (0x53525354)** — system reset and shutdown.

## OpenSBI Architecture

OpenSBI is structured in three layers:

```
+-------------------------------+
|    Platform-specific code     |  (board/SoC vendor provides this)
+-------------------------------+
|    OpenSBI generic library    |  (opensbi/lib/*)
+-------------------------------+
|    SBI specification impl.    |  (trap handler, extension dispatch)
+-------------------------------+
```

A vendor porting OpenSBI to new hardware implements a **platform struct** with callbacks for console I/O, timer access, and IPI delivery. The generic library handles everything else.

## Firmware Payload Modes

OpenSBI can be built in three modes depending on how it is integrated:

- **FW_PAYLOAD** — OpenSBI bundles the next-stage image (e.g., U-Boot or the kernel) directly as a payload. A single binary is loaded by the FSBL.
- **FW_JUMP** — OpenSBI jumps to a fixed address after initialization. The FSBL must have already loaded the next-stage image there.
- **FW_DYNAMIC** — The FSBL passes a struct to OpenSBI describing where the next-stage image is. Most flexible; used by U-Boot SPL + OpenSBI combinations.

## The OpenSBI Trap Handler

When the kernel executes `ecall`, the CPU traps into M-mode and OpenSBI's trap handler runs:

```c
// Simplified dispatch (opensbi/lib/sbi/sbi_ecall.c)
int sbi_ecall_handler(struct sbi_trap_regs *regs) {
    unsigned long ext_id = regs->a7;
    unsigned long func_id = regs->a6;

    ext = sbi_ecall_find_extension(ext_id);
    if (!ext)
        return SBI_ENOTSUPP;

    return ext->handle(func_id, regs);
}
```

After handling the call, OpenSBI advances `mepc` by 4 (to skip past the `ecall` instruction) and returns to S-mode.

## PMP Setup

Before delegating to S-mode, OpenSBI configures the **Physical Memory Protection (PMP)** unit to ensure the kernel cannot access M-mode memory regions (OpenSBI's own code and data). This is a critical security boundary.

## Common Pitfalls

- Calling an SBI extension the firmware does not implement — always probe with the Base extension first if portability is required.
- Forgetting that `mtime` and `mtimecmp` are MMIO registers, not CSRs; only M-mode firmware should touch them directly.
- Mismatched SBI spec versions between firmware and kernel can cause subtle failures (check `sbi_spec_version` via the Base extension).

> **Interview answer:** OpenSBI is the standard RISC-V M-mode firmware; it implements the SBI specification so the S-mode OS kernel can request privileged operations (timer, IPI, system reset) via `ecall` without running in machine mode itself.
