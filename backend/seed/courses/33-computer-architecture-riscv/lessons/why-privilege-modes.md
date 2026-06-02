# Why Privilege Modes Exist

Modern processors do not treat all code equally. The instructions that configure hardware, manage memory, and service interrupts must be protected from ordinary application code. Privilege modes are the hardware mechanism that enforces this separation.

## The Core Problem

Imagine a world with no privilege levels. Any program could write to any memory address, halt the CPU, reconfigure interrupt controllers, or disable paging. A single misbehaving application — or a malicious one — could crash or compromise the entire system. Operating systems need a way to assert authority over hardware while keeping user programs sandboxed.

Privilege modes solve this by dividing the instruction set into two (or more) layers:

- **Privileged instructions** — only available to trusted software (firmware, OS kernels).
- **Unprivileged instructions** — available to all software, including user applications.

Attempting to execute a privileged instruction from an unprivileged context raises a trap, handing control back to the trusted layer.

## What Privilege Modes Protect

| Resource | Requires Privilege |
|---|---|
| Physical memory map | Yes |
| Page-table base register (satp) | Yes |
| Interrupt enable/disable | Yes |
| Timer registers (mtime, mtimecmp) | Yes |
| Ordinary arithmetic / branches | No |
| Stack manipulation | No |

## RISC-V's Three-Level Hierarchy

RISC-V defines up to three privilege levels, ordered from most to least trusted:

1. **Machine Mode (M-Mode)** — Highest privilege. The processor always starts here. Firmware and bootloaders live here.
2. **Supervisor Mode (S-Mode)** — Intermediate privilege. OS kernels run here in systems that support virtual memory.
3. **User Mode (U-Mode)** — Lowest privilege. Application code runs here.

A minimal embedded system may implement only M-Mode. A full Linux-capable system implements all three. This layered design lets RISC-V scale from microcontrollers to servers.

## Why Separation Matters in Practice

**Isolation** — A bug in a user-space program cannot overwrite kernel page tables.

**Accountability** — Every attempt to cross a privilege boundary is mediated by a controlled path (the `ecall` instruction), giving the kernel full visibility.

**Minimal trusted computing base** — The firmware only needs to trust itself. The kernel only needs to trust the firmware. User applications trust nothing below them directly.

## A Concrete Analogy

Think of an airplane. Passengers (U-Mode) can read books and recline their seats. Flight attendants (S-Mode) can walk the cabin, access the galley, and communicate with the cockpit. Pilots (M-Mode) can fly the plane, alter the flight plan, and control all systems. Each level has exactly the capabilities it needs — no more.

## Common Pitfall

Developers new to systems programming sometimes conflate kernel space with M-Mode. On a Linux RISC-V system, the Linux kernel runs in **S-Mode**, not M-Mode. M-Mode is occupied by firmware (such as OpenSBI). This distinction matters when debugging trap handling or SBI calls.

## Worked Example

A user program calls `read()`. The syscall path is:

```
User program (U-Mode)
  └─ ecall  →  Linux kernel (S-Mode)
                 └─ sbi_call  →  OpenSBI firmware (M-Mode)
                                   └─ accesses UART hardware
```

Each arrow is a controlled privilege transition. Hardware enforces that no level can skip a layer.

> **Interview answer:** Privilege modes exist to prevent untrusted code from accessing hardware resources directly, ensuring only the operating system and firmware can perform operations that affect system integrity.
