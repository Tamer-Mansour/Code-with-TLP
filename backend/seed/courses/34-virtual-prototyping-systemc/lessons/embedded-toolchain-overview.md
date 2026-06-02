# The Embedded Toolchain: Compiler, Linker, Loader

Turning C source into firmware running on a microcontroller involves a chain of tools: compiler, assembler, linker, and finally a programmer/loader. Understanding each stage is essential for debugging build failures, reducing code size, and diagnosing hard faults that only appear after linking.

## The Pipeline at a Glance

```
Source (.c, .cpp, .s)
        │
        ▼
   [ Preprocessor ]   — expands #include, #define, #ifdef
        │
        ▼
   [ Compiler ]       — translates C/C++ to assembly
        │
        ▼
   [ Assembler ]      — translates assembly to machine code → .o (object file)
        │
        ▼
   [ Linker ]         — combines .o files + libraries → ELF image
        │
        ▼
   [ objcopy/srec ]   — strips debug info → .bin / .hex / .srec
        │
        ▼
   [ Programmer ]     — writes binary to device flash via JTAG/SWD/UART
```

## The Compiler

For ARM Cortex targets the dominant toolchains are:

| Toolchain | Typical Use |
|---|---|
| `arm-none-eabi-gcc` (GNU Arm) | Open-source, wide ecosystem, free |
| Arm Compiler 6 (`armclang`) | Commercial, best for Cortex-A safety |
| LLVM/Clang for ARM | Growing, good for sanitizers |
| IAR EWARM `iccarm` | Certified for functional safety (DO-178, IEC 61508) |

Key compiler flags for embedded:

```bash
arm-none-eabi-gcc \
  -mcpu=cortex-m4 \       # target CPU
  -mthumb \               # use Thumb-2 ISA (compact encoding)
  -mfpu=fpv4-sp-d16 \    # hardware FPU
  -mfloat-abi=hard \      # pass floats in FPU registers
  -Os \                   # optimise for size
  -ffunction-sections \   # each function in its own ELF section
  -fdata-sections \       # each variable in its own section
  -Wall -Wextra \         # enable warnings
  -c main.c -o main.o
```

`-ffunction-sections` and `-fdata-sections` are critical — they allow the linker to garbage-collect unused code and data, which can reduce flash usage by 20–40 %.

## The Linker and Linker Script

The linker combines object files and resolves symbol references. For embedded targets, it also needs a **linker script** (`.ld`) that describes the hardware memory layout.

```ld
/* Minimal STM32F4 linker script fragment */
MEMORY {
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 1024K
    SRAM  (rwx) : ORIGIN = 0x20000000, LENGTH = 192K
}

SECTIONS {
    .text : {
        KEEP(*(.isr_vector))   /* vector table must be first */
        *(.text*)
        *(.rodata*)
    } > FLASH

    .data : {
        _sdata = .;
        *(.data*)
        _edata = .;
    } > SRAM AT > FLASH       /* VMA in SRAM, LMA in FLASH */

    .bss : {
        _sbss = .;
        *(.bss*)
        *(COMMON)
        _ebss = .;
    } > SRAM
}
```

The `AT > FLASH` directive tells the linker that `.data` lives in SRAM at runtime (VMA) but is *stored* in flash (LMA). The startup code copies it from flash to SRAM before `main()` runs.

## The Startup File

Before `main()` is called, the CPU needs:

1. Stack pointer initialised (usually the last word of SRAM, set in the vector table).
2. `.data` section copied from flash to SRAM.
3. `.bss` section zeroed.
4. C++ constructors invoked (if applicable).
5. Clocks and PLLs initialised (often in SystemInit).

```asm
/* Minimal Cortex-M startup in GNU assembly */
.global Reset_Handler
Reset_Handler:
    ldr  r0, =_estack       /* top of SRAM */
    mov  sp, r0
    bl   SystemInit         /* clock setup */
    /* copy .data */
    ldr  r1, =_sidata       /* LMA (flash source) */
    ldr  r2, =_sdata        /* VMA start */
    ldr  r3, =_edata        /* VMA end */
copy_loop:
    cmp  r2, r3
    bge  zero_bss
    ldr  r0, [r1], #4
    str  r0, [r2], #4
    b    copy_loop
zero_bss:
    /* ... zero BSS ... */
    bl   main
    b    .                  /* trap if main returns */
```

## The Loader/Programmer

The final binary is written to flash by a hardware programmer via JTAG or SWD (Serial Wire Debug). Common tools:

```bash
# OpenOCD (open source, supports hundreds of probes)
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
        -c "program firmware.elf verify reset exit"

# PyOCD (Python, DAPLink)
pyocd flash --target stm32f401re firmware.bin

# Segger J-Link
JFlashExe -device STM32F401RE -if SWD -speed 4000 -auto
```

## Common Pitfalls

- **Symbol not found at link time vs compile time.** Compile errors are per-file; linker errors reveal missing symbols across the whole program. Forgetting to include a `.c` file in the build produces a linker error, not a compiler error.
- **Wrong linker script.** Using the linker script for a 512 KB part on a 256 KB part means the linker happily links code that overflows flash. The overflow is only caught at runtime (corrupt vector table, hard fault on boot).
- **Startup code not included.** Many beginners skip the `.s` startup file, resulting in `.data` not initialised and `.bss` not zeroed — C global variables have random values.

> **Interview answer:** The embedded toolchain compiles C source to object files, links them with a hardware-specific linker script that places code in flash and data in SRAM, then a programmer tool writes the resulting binary to the device's non-volatile memory via JTAG or SWD.
