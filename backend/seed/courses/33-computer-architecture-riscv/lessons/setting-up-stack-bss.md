# Setting Up the Stack and Clearing BSS

Two of the most fundamental tasks that any boot code or firmware must perform before calling C functions are: **setting up a valid stack** and **clearing the BSS section**. These tasks look trivial but their correct implementation is critical — failure produces bugs that are nearly impossible to debug with conventional tools.

## Why the Stack Must Be Set Up First

RISC-V (like all RISC architectures) has no hardware-managed stack. The stack is just a convention: `sp` (x2) points to the top of a region of memory, and the calling convention uses it for return addresses, local variables, and spilled registers. After reset, `sp` is undefined.

The very first thing a C program does when a function is called is to subtract from `sp` to make room for the stack frame. If `sp` points to a random address, this overwrites whatever is there — potentially the firmware code itself.

```asm
    .section .text.init
    .global _start

_start:
    # Step 1: set up the stack BEFORE doing anything else
    la   sp, _stack_top       # _stack_top is defined in the linker script
    # Stack grows downward; _stack_top is the HIGH address
    
    # Step 2: clear BSS
    la   a0, _bss_start
    la   a1, _bss_end
    bgeu a0, a1, 2f           # skip if BSS is empty
1:
    sd   zero, 0(a0)          # store 8 bytes of zero
    addi a0, a0, 8
    bltu a0, a1, 1b
2:
    # Step 3: call C entry point
    call firmware_main

    # Should never return; hang if it does
3:  j 3b
```

## The Linker Script Role

The stack and BSS boundaries must be defined in the **linker script** so the assembly code can reference them:

```ld
SECTIONS {
    . = 0x80000000;

    .text : { *(.text.init) *(.text*) }
    .rodata : { *(.rodata*) }
    .data : { *(.data*) }

    .bss (NOLOAD) : {
        _bss_start = .;
        *(.bss*)
        *(COMMON)
        _bss_end = .;
    }

    /* Stack: 16 KB, placed after BSS */
    . = ALIGN(16);
    _stack_bottom = .;
    . += 0x4000;
    _stack_top = .;
}
```

The `NOLOAD` attribute on `.bss` tells the linker not to store zero bytes in the ELF file (saving space in flash); the boot code is responsible for zeroing it at runtime.

## What Is BSS and Why Clear It?

**BSS** (Block Started by Symbol) is the segment that holds **zero-initialized global and static variables**. By convention — and by the C standard — all variables with static storage duration that are not explicitly initialized must start as zero.

```c
// These live in BSS — must be zero before main() is called
static int counter;         // should be 0
char buffer[1024];          // should be all zeros
int initialized = 0;        // also BSS; explicit 0 is still BSS
```

If BSS is not cleared:

- `counter` starts at whatever DRAM happened to contain after power-on (often non-zero due to DRAM retention or charge leakage patterns).
- Programs that rely on zero-initialization will have silent data corruption bugs.

## Stack Alignment

The RISC-V calling convention requires the stack pointer to be **16-byte aligned** at function call boundaries. If `sp` is not aligned, some instructions (especially those involving floating-point or vector registers) may fault or produce incorrect results on hardware that enforces alignment.

```asm
    la   sp, _stack_top
    andi sp, sp, ~0xF         # force 16-byte alignment (clear low 4 bits)
```

## Per-Hart Stacks in Multi-Hart Systems

When multiple harts boot simultaneously, each needs its own stack. A common pattern:

```asm
_start:
    csrr a0, mhartid          # read this hart's ID
    la   sp, _stack_top
    li   t0, STACK_SIZE_PER_HART
    mul  t0, a0, t0           # offset = hartid * stack_size
    sub  sp, sp, t0           # each hart gets its own region
```

This statically partitions a large stack region into per-hart slices.

## Common Pitfalls

- **Clearing BSS before setting up `sp`.** The clear loop itself uses the stack (if written in C) — set up `sp` first, always in assembly.
- **BSS larger than expected.** Large uninitialized arrays in C silently expand BSS; use `size firmware.elf` to check segment sizes before flashing.
- **Clearing BSS with word-sized stores when BSS is not word-aligned.** Always use byte stores for the tail, or ensure the linker script aligns BSS to your store width.

> **Interview answer:** Boot code must set `sp` to a valid stack region and zero the BSS section before calling any C function; the stack pointer must be set first in assembly because BSS clearing and any C code depend on a working stack.
