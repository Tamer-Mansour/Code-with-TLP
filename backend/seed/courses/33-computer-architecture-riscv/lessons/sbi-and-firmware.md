# The Supervisor Binary Interface (SBI)

The Supervisor Binary Interface (SBI) is the ABI that sits between the OS kernel (S-Mode) and the firmware (M-Mode). It is to RISC-V what BIOS or UEFI firmware calls are to x86 — a standardized way for the operating system to request hardware services that require machine-level privilege.

## Why SBI Exists

The OS kernel runs in S-Mode and cannot directly access hardware registers that require M-Mode privilege (timer `mtimecmp`, hart (hardware thread) management CSRs, power-control registers, etc.). Without a standard interface, every firmware implementation would require a custom kernel driver. SBI solves this by defining:

- A standard calling convention.
- A catalog of extensions (timer, IPI, RFENCE, HSM, SRST, etc.).
- An error code scheme.

The canonical implementation of SBI is **OpenSBI**, an open-source M-Mode firmware library used by most RISC-V Linux systems.

## The SBI Calling Convention

SBI calls use the `ecall` instruction from S-Mode. Arguments and return values follow a structured layout:

| Register | Role |
|---|---|
| `a7` | SBI Extension ID |
| `a6` | SBI Function ID within the extension |
| `a0`–`a5` | Input arguments |
| `a0` | Return: error code (0 = success) |
| `a1` | Return: value |

```asm
# SBI call: set_timer(stime_value)
# Extension: TIME (0x54494D45), Function: 0
li    a7, 0x54494D45    # "TIME" as ASCII bytes interpreted as u32
li    a6, 0             # function set_timer
mv    a0, s0            # next timer value (u64)
ecall
# a0 = 0 on success (SBI_SUCCESS)
```

## Standard SBI Extensions

| Extension ID | Name | Purpose |
|---|---|---|
| `0x01` | Legacy Console Putchar | Print a character (deprecated) |
| `0x54494D45` | TIME | Set timer (`sbi_set_timer`) |
| `0x735049` | sPI | Send inter-processor interrupts |
| `0x52464E43` | RFENCE | Remote TLB flushes across harts |
| `0x48534D` | HSM | Hart State Management (start/stop CPUs) |
| `0x53525354` | SRST | System Reset (reboot, shutdown) |
| `0x10` | Base | Probe extensions, get firmware version |

The Base extension is always present and is used to discover which other extensions the firmware implements:

```c
// Probe whether the SRST extension is available
long sbi_probe_extension(long ext_id) {
    register long a0 asm("a0") = ext_id;
    register long a6 asm("a6") = 3;           // sbi_probe_extension func ID
    register long a7 asm("a7") = 0x10;        // Base extension
    asm volatile("ecall" : "+r"(a0) : "r"(a6), "r"(a7) : "a1", "memory");
    return a0;   // 0 = not available, 1 = available
}
```

## SBI Error Codes

| Code | Constant | Meaning |
|---|---|---|
| 0 | `SBI_SUCCESS` | Operation succeeded |
| -1 | `SBI_ERR_FAILED` | Generic failure |
| -2 | `SBI_ERR_NOT_SUPPORTED` | Extension/function not implemented |
| -3 | `SBI_ERR_INVALID_PARAM` | Bad argument value |
| -4 | `SBI_ERR_DENIED` | Permission denied |

## A Full SBI Call: System Shutdown

```c
// Request system power-off via SRST extension
void sbi_system_reset(uint32_t reset_type, uint32_t reset_reason) {
    register long a0 asm("a0") = reset_type;    // 0=shutdown, 1=cold reboot
    register long a1 asm("a1") = reset_reason;  // 0=no reason
    register long a6 asm("a6") = 0;             // function: system_reset
    register long a7 asm("a7") = 0x53525354;    // "SRST"
    asm volatile("ecall"
        : "+r"(a0), "+r"(a1)
        : "r"(a6), "r"(a7)
        : "memory");
    // Should not return; if it does, a0 contains an error code
    while (1) asm volatile("wfi");
}
```

## OpenSBI Architecture

```
┌─────────────────────────────────┐
│     Linux Kernel (S-Mode)       │
│  drivers/firmware/riscv/sbi.c   │
└────────────────┬────────────────┘
                 │ ecall
┌────────────────▼────────────────┐
│     OpenSBI Firmware (M-Mode)   │
│  lib/sbi/sbi_ecall_*.c          │
│  ┌─────────────────────────┐    │
│  │  Platform Layer         │    │
│  │  (board-specific code)  │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
                 │
         Hardware registers
```

OpenSBI is initialized early in boot (before the kernel), sets up delegation, configures PMP, and then calls `mret` into the kernel with the SBI environment ready.

## Common Pitfall

Using deprecated legacy SBI calls (Extension IDs 0x00–0x08, the "SBI v0.1" interface) in new code. These are still present in OpenSBI for compatibility but may be removed in future firmware versions. Always use the versioned extensions (TIME, HSM, SRST, etc.) introduced in SBI v0.2.

## Worked Example: Reading the Current Time

```c
// Read mtime via SBI (since S-Mode cannot access mtime directly)
uint64_t sbi_get_time(void) {
    // On most platforms, the timer memory-mapped at a fixed address
    // is readable by S-Mode. But for portability, use SBI:
    // SBI v0.1 legacy: returns time in a0
    register long a7 asm("a7") = 0x01;   // legacy sbi_get_time (deprecated)
    register long a0 asm("a0");
    asm volatile("ecall" : "=r"(a0) : "r"(a7) : "a1", "memory");
    return (uint64_t)a0;
}
```

> **Interview answer:** SBI is the standardized ABI between the RISC-V OS kernel in S-Mode and M-Mode firmware (like OpenSBI); the kernel issues SBI calls via ecall with an extension ID in a7 and function ID in a6 to request privileged services — such as timer programming and CPU management — that require M-Mode access.
