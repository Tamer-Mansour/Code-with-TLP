# Port-Mapped (Isolated) I/O

Port-mapped I/O (PMIO) — also called isolated I/O or I/O-mapped I/O — is a second strategy for CPU-to-device communication. Rather than sharing the same address space as RAM, devices live in a completely separate *I/O address space* reachable only through dedicated instructions.

## The Separate I/O Address Space

On x86, the CPU maintains two distinct address spaces:

1. **Memory address space** — up to 2^64 bytes (64-bit), accessed by `MOV`, `LOAD`, `STORE`.
2. **I/O port address space** — 65,536 ports (16-bit port numbers 0x0000–0xFFFF), accessed by `IN` and `OUT` instructions.

Because the spaces are separate, the same numeric value can appear in both without ambiguity: port `0x03F8` is the first x86 COM (serial) port, while memory address `0x03F8` is just low RAM.

## The IN and OUT Instructions (x86)

```asm
; Write a byte to port 0x03F8 (COM1 data register)
mov  al, 'A'       ; character to send
mov  dx, 0x03F8    ; port address in DX
out  dx, al        ; send byte to I/O port

; Read a byte from port 0x03F8
mov  dx, 0x03F8
in   al, dx        ; receive byte from I/O port
```

Port widths follow the register used:
- `IN AL, DX` / `OUT DX, AL` — 8-bit (byte)
- `IN AX, DX` / `OUT DX, AX` — 16-bit (word)
- `IN EAX, DX` / `OUT DX, EAX` — 32-bit (dword)

A compact port number (0–255) can also be encoded as an immediate:

```asm
in   al, 0x61     ; read PC speaker / keyboard controller port directly
```

## Classic x86 I/O Port Map

| Port Range | Device |
|---|---|
| 0x0020–0x0021 | PIC1 (Programmable Interrupt Controller) |
| 0x0040–0x0043 | PIT (Programmable Interval Timer) |
| 0x0060–0x0064 | PS/2 Keyboard / Mouse |
| 0x0070–0x0071 | CMOS / RTC |
| 0x03F8–0x03FF | COM1 Serial Port |
| 0x0CF8–0x0CFF | PCI Configuration Space |

## Privilege and Protection

On x86, `IN` and `OUT` are **privileged instructions** when the current privilege level (CPL) is greater than the I/O Privilege Level (IOPL) stored in `EFLAGS`. The CPU checks the Task State Segment (TSS) I/O Permission Bitmap (IOPB) to decide whether a user-space program may access a specific port.

In practice, modern operating systems set IOPL to 0, meaning all direct port I/O from user space triggers a General Protection Fault. Only kernel code (device drivers) runs I/O instructions unimpeded.

## Accessing Ports in C / Linux

Linux provides helper functions for port I/O in kernel drivers:

```c
#include <asm/io.h>

uint8_t  val8  = inb(0x03F8);   // read byte
uint16_t val16 = inw(0x03F0);   // read word
uint32_t val32 = inl(0x0CF8);   // read dword

outb(0x03F8, 'A');  // write byte
outw(0x03F0, 0x0F00); // write word
```

User-space programs can access ports after calling `ioperm()` or `iopl()` (Linux-specific, requires `CAP_SYS_RAWIO`):

```c
#include <sys/io.h>

ioperm(0x03F8, 8, 1);   // grant access to 8 ports starting at 0x03F8
outb(0x03F8, 'H');
ioperm(0x03F8, 8, 0);   // revoke
```

## Advantages of PMIO

- **Clean separation** — Device registers cannot accidentally alias RAM addresses.
- **Simpler hardware decode** — The address decoder only needs to handle 16-bit port numbers.
- **No `volatile` issue at the language level** — The explicit `IN`/`OUT` instructions have implicit side effects; the compiler cannot optimize them away.
- **Hardware protection** — The IOPB allows fine-grained per-port access control.

## Limitations

- **x86-only** — ARM, RISC-V, MIPS, and almost all non-x86 architectures do not have a separate I/O address space. They use MMIO exclusively.
- **64K port limit** — 65,536 ports is far too small for modern systems with hundreds of devices.
- **Legacy only on x86** — New x86 peripherals (PCIe, USB, SATA) use MMIO via BAR (Base Address Registers); the old port map is kept only for backward compatibility.

## Common Pitfalls

- **Using the wrong port width** — Reading a 16-bit register with `inb` returns only the low byte; the high byte is lost.
- **Port conflicts** — Two drivers accidentally using the same port number cause unpredictable behavior; always call `request_region()` in Linux to claim ownership.

> **Interview answer:** Port-mapped I/O uses a separate 16-bit I/O address space on x86, accessible only via the `IN` and `OUT` instructions. It cleanly separates device registers from RAM but is limited to x86 and to only 65,536 ports. Modern peripherals on all architectures — including x86 PCIe — use memory-mapped I/O instead.
