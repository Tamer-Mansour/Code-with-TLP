# Privilege Levels and CPU Protection Rings

Modern CPUs formalize privilege as a numbered set of **protection rings**. The ring number determines what a piece of running code is allowed to do. Lower rings are more trusted and more powerful.

## The x86 Ring Model

Intel's x86 architecture defines **four rings**, numbered 0 through 3:

```
Ring 0  ── Kernel / OS core          (most privileged)
Ring 1  ── Device drivers (historical use; rarely used today)
Ring 2  ── Device drivers (historical use; rarely used today)
Ring 3  ── User applications          (least privileged)
```

In practice, mainstream operating systems (Linux, Windows, macOS) use only **Ring 0 and Ring 3**. Rings 1 and 2 were intended for device drivers at intermediate privilege, but the complexity was not worth the benefit — drivers run in Ring 0 or as user-space drivers instead.

## Why the Name "Ring"?

Picture concentric circles. The innermost circle (Ring 0) can reach everything — all memory, all hardware, all instructions. Each outer ring loses capabilities. Code in Ring 3 can see only what the OS explicitly grants it through controlled interfaces.

The CPU enforces ring boundaries in hardware. Any attempt by Ring 3 code to execute a Ring-0 instruction causes a **general protection fault** — a hardware trap the kernel handles.

## What Ring 0 Can Do That Ring 3 Cannot

| Operation | Ring 0 | Ring 3 |
|---|---|---|
| `HLT` (halt the CPU) | Yes | Trap |
| `IN`/`OUT` (direct I/O port access) | Yes | Trap |
| Load `CR3` (change page table) | Yes | Trap |
| `LGDT`/`LIDT` (load descriptor tables) | Yes | Trap |
| `CLI`/`STI` (disable/enable interrupts) | Yes | Trap |
| Ordinary arithmetic, function calls | Yes | Yes |
| Read own virtual memory | Yes | Yes |

## CPL, DPL, and RPL

x86 tracks privilege in three fields:

- **CPL (Current Privilege Level)**: The privilege level of the currently executing code. Stored in bits [1:0] of the `CS` register. CPL=0 means kernel; CPL=3 means user.
- **DPL (Descriptor Privilege Level)**: The minimum privilege required to access a segment or gate descriptor. Set by the OS at boot.
- **RPL (Requested Privilege Level)**: Used during segment selector loads to prevent privilege escalation tricks.

The CPU checks `CPL <= DPL` before granting access. If the check fails, you get a #GP fault.

```asm
; Reading CPL from user space — you can inspect it, but not change it
; (This snippet runs in a debugger or with OS assistance)
mov ax, cs        ; load code segment selector into AX
and ax, 3         ; mask bits [1:0] — this is the RPL, which equals CPL in practice
; ax is now 3 if you are in user mode, 0 if in kernel mode
```

## Virtualization and Ring −1

Hardware-assisted virtualization (Intel VT-x, AMD-V) introduced a concept sometimes called **Ring −1** or **VMX root mode**. A hypervisor runs in this mode — even more privileged than Ring 0 — so a guest OS can occupy Ring 0 without being able to escape the hypervisor's control. The guest OS thinks it owns the machine; the hypervisor actually does.

## ARM's Equivalent: Exception Levels

ARM uses **Exception Levels (EL0–EL3)** rather than rings, but the concept is identical:

| ARM EL | Equivalent Role |
|---|---|
| EL0 | User applications (Ring 3) |
| EL1 | OS kernel (Ring 0) |
| EL2 | Hypervisor (Ring −1) |
| EL3 | Secure monitor (firmware/TrustZone) |

## Common Pitfalls

- **Assuming Ring 1/2 are actively used**: In standard Linux/Windows kernels they are not. Mentioning them without this caveat can mislead an interviewer.
- **Confusing CPL with a software variable**: CPL is a hardware register field, not a variable you set in code.
- **Thinking rings are a Linux concept**: Rings are a CPU architecture feature. The OS decides how to use them.

## Interview Answer

> **Q: What are CPU protection rings and which ones does Linux use?**
>
> **Interview answer:** Protection rings are hardware-enforced privilege levels. x86 defines rings 0–3, where ring 0 is fully privileged. Linux uses only ring 0 for the kernel and ring 3 for user processes, relying on the CPU to trap any attempt by ring-3 code to execute ring-0 instructions.
