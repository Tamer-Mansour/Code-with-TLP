# What Is Virtual Memory?

Virtual memory is one of the most powerful abstractions in modern computing. It gives every process the illusion that it owns the entire address space of the machine — even though physical RAM is finite, shared, and may be far smaller than the addresses a program uses.

## The Core Idea

When your program reads from or writes to an address like `0x00400000`, that number is a **virtual address**. The hardware, guided by the operating system, translates it on-the-fly into a **physical address** — the actual row and column of capacitors in your DRAM chips.

This translation layer is what we call **virtual memory**.

```
Program writes to: 0x00400000  (virtual)
         |
         v
  [ MMU + Page Table ]
         |
         v
Hardware reads:  0x1A3F8000  (physical)
```

## Two Distinct Address Spaces

| Address Type | Who sees it | Example range |
|---|---|---|
| Virtual | The process, compiler, linker | `0x0000_0000` – `0xFFFF_FFFF` (32-bit) |
| Physical | DRAM chips, memory controller | `0x0000_0000` – size of installed RAM |

Every process has its **own** virtual address space. Two processes can both "use" address `0x1000` and yet write to completely different physical locations. The OS keeps them apart.

## Why the Distinction Matters

Without virtual memory, every program would have to know exactly which physical memory addresses were free. Worse, one buggy program could overwrite another program's data — or the kernel itself. This was the reality on early personal computers and embedded systems without an MMU.

Virtual memory solves three related problems at once:

- **Isolation**: process A cannot touch process B's physical pages.
- **Abstraction**: programs are written as if they own a clean, contiguous address space.
- **Flexibility**: physical memory can be fragmented; virtual memory looks flat.

## The Address Space Layout

A typical 64-bit Linux process virtual address space looks like this:

```
High addresses  0xFFFF_FFFF_FFFF_FFFF
  ┌─────────────────────────────┐
  │  Kernel (not user-visible)  │
  ├─────────────────────────────┤
  │  Stack (grows downward)     │
  │  ...                        │
  │  Memory-mapped files / libs │
  │  ...                        │
  │  Heap (grows upward)        │
  ├─────────────────────────────┤
  │  BSS / data / text          │
Low addresses   0x0000_0000_0000_0000
  └─────────────────────────────┘
```

The kernel occupies the upper half; user code lives in the lower half. Neither region maps 1-to-1 to physical RAM.

## Virtual Memory Is Not the Same as RAM

A common misconception: "virtual memory" is not a synonym for swap space or disk-backed memory. Swap is one *use* of virtual memory — you can map a virtual page to a disk block instead of a physical RAM frame — but virtual memory is the entire address-translation system, whether or not any swapping ever occurs.

## RISC-V Context

RISC-V defines the **Sv32**, **Sv39**, and **Sv48** virtual memory schemes for 32-bit, 39-bit, and 48-bit virtual address spaces respectively. The scheme in use is selected by writing to the `satp` (Supervisor Address Translation and Protection) CSR. When `satp.MODE = 0`, virtual memory is disabled and addresses are physical.

```asm
# Read the satp register (RISC-V supervisor mode)
csrr t0, satp
# Bit 31 (Sv32) or bits 63:60 (Sv39/48) select the mode
```

## Interview Answer

> "Virtual memory is a hardware-OS abstraction that gives each process its own private address space. The MMU translates virtual addresses to physical addresses at runtime, providing isolation between processes and allowing the OS to manage physical memory independently of how programs address it."

A crisp follow-up: the unit of translation is the **page** (typically 4 KiB), not individual bytes — that is the subject of the next lesson.
