# A Bare-Metal Boot Walkthrough

This lesson traces a complete minimal bare-metal RISC-V program from reset vector to printing "Hello, World!" on a UART — no OS, no C library, no SBI. Every line is explained so you understand exactly what happens and why.

## Target Platform

We target the QEMU `virt` machine, which is the easiest way to test bare-metal RISC-V:

- Reset vector: `0x8000_0000`
- NS16550A UART at `0x1000_0000`
- Single hart (hart 0)
- RV64GC ISA

## Project Layout

```
bare-metal/
  start.S          # assembly entry point
  main.c           # C code (puts, loop)
  uart.h           # UART register definitions
  link.ld          # linker script
  Makefile
```

## The Linker Script (`link.ld`)

```ld
OUTPUT_ARCH(riscv)
ENTRY(_start)

SECTIONS {
    . = 0x80000000;             /* QEMU virt load address */

    .text : {
        *(.text.init)           /* entry point first */
        *(.text*)
    }
    .rodata : { *(.rodata*) }
    .data   : { *(.data*)   }

    .bss (NOLOAD) : {
        _bss_start = .;
        *(.bss*)
        *(COMMON)
        _bss_end = .;
    }

    . = ALIGN(16);
    . += 0x4000;                /* 16 KB stack */
    _stack_top = .;
}
```

## The Entry Point (`start.S`)

```asm
    .section .text.init
    .global  _start

_start:
    # 1. Park non-zero harts
    csrr t0, mhartid
    bnez t0, _park

    # 2. Set stack pointer
    la   sp, _stack_top

    # 3. Clear BSS
    la   a0, _bss_start
    la   a1, _bss_end
bss_loop:
    bgeu a0, a1, bss_done
    sd   zero, 0(a0)
    addi a0, a0, 8
    j    bss_loop
bss_done:

    # 4. Call C entry point
    call main

_park:
    wfi
    j _park
```

## UART Driver (`uart.h`)

The QEMU `virt` machine has an NS16550A UART. At 115200 baud with a 3.686 MHz clock, it is already configured by QEMU — we only need to write bytes to the THR (Transmit Holding Register) at offset 0:

```c
#define UART_BASE  0x10000000UL
#define UART_THR   (*(volatile unsigned char *)(UART_BASE + 0))
#define UART_LSR   (*(volatile unsigned char *)(UART_BASE + 5))
#define LSR_THRE   0x20   /* Transmitter Holding Register Empty */

static inline void uart_putchar(char c) {
    while (!(UART_LSR & LSR_THRE))
        ;           /* wait for TX buffer empty */
    UART_THR = c;
}

static void uart_puts(const char *s) {
    while (*s)
        uart_putchar(*s++);
}
```

## The C Entry Point (`main.c`)

```c
#include "uart.h"

void main(void) {
    uart_puts("Hello, World!\r\n");

    /* Halt: spin forever */
    while (1)
        ;
}
```

## Building and Running

```bash
# Build
riscv64-unknown-elf-gcc -march=rv64g -mabi=lp64 \
    -nostdlib -nostartfiles \
    -T link.ld start.S main.c \
    -o hello.elf

# Strip to raw binary (optional)
riscv64-unknown-elf-objcopy -O binary hello.elf hello.bin

# Run in QEMU
qemu-system-riscv64 \
    -machine virt \
    -bios none \
    -kernel hello.elf \
    -nographic

# Expected output:
# Hello, World!
```

The `-bios none` flag tells QEMU not to load OpenSBI — our firmware IS the only code that runs.

## Execution Trace

| Step | What happens |
|------|-------------|
| QEMU loads `hello.elf` at `0x8000_0000` | ELF segments written to guest memory |
| PC set to `_start` (`0x8000_0000`) | Reset vector jumps here |
| `csrr t0, mhartid` | Reads hart 0 ID (= 0) |
| `bnez t0, _park` | Not taken (hart 0) |
| `la sp, _stack_top` | Stack pointer set |
| BSS clear loop | All static vars zeroed |
| `call main` | C code begins |
| `uart_puts(...)` | Characters sent to UART |
| `while(1)` | System halts gracefully |

## Common Mistakes in Bare-Metal Projects

- Using `printf` — it depends on syscalls that do not exist without an OS.
- Forgetting `-nostdlib` — the linker may include `crt0.o` which tries to call `main` in a different way and crashes.
- Not waiting for `LSR_THRE` — overflowing the UART FIFO drops characters.
- Placing the stack inside the `.bss` region — the BSS clear will clobber the stack.

> **Interview answer:** A bare-metal RISC-V boot writes the stack pointer and clears BSS in assembly before jumping to C; for output it writes directly to the UART's memory-mapped transmit register after polling the Line Status Register for buffer-empty.
