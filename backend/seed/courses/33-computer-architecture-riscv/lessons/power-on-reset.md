# Power-On Reset and the Reset Vector

When power is applied to a RISC-V processor, the hardware does not immediately execute application code. Instead, a carefully orchestrated sequence begins to bring the CPU into a known, safe state — a process called **Power-On Reset (POR)**.

## What Happens at Power-On

The moment Vdd stabilizes above the threshold voltage, the chip's reset logic asserts an internal reset signal. This holds all registers, pipeline stages, and control signals in a defined initial state. The reset signal is deasserted only after:

- The power supply voltage is stable.
- Any required clock sources (PLLs, oscillators) have locked.
- Optional boot configuration pins have been sampled.

Until reset is deasserted, the CPU executes nothing. This prevents undefined behavior from partially charged flip-flops or unstable clock signals.

## The Reset Vector

Once reset is released, the program counter (PC) is loaded with a fixed address called the **reset vector**. This is the very first instruction the hart (hardware thread) will fetch.

In the RISC-V specification, the reset vector is **implementation-defined** — the spec does not mandate a specific address. Common choices in real silicon:

| Platform | Reset Vector |
|----------|-------------|
| SiFive HiFive1 | `0x0000_0000` |
| QEMU `virt` machine | `0x8000_0000` |
| Rocket Chip (default) | `0x0000_1000` |

The ROM at the reset vector typically contains a tiny sequence that either jumps directly to flash memory or begins a more elaborate boot ROM routine.

## Reset Vector Code Example

Here is a minimal reset vector stub in RISC-V assembly:

```asm
    .section .text.reset, "ax"
    .global _reset_vector

_reset_vector:
    # Load the address of the main boot ROM entry point
    lui  t0, %hi(_boot_start)
    addi t0, t0, %lo(_boot_start)
    jalr zero, 0(t0)          # Jump; return address discarded
```

The `jalr zero` discards the return address, making this an unconditional jump. A one-instruction ROM at the reset vector jumping to a larger boot ROM is a common pattern.

## CSR State After Reset

After reset, all Control and Status Registers (CSRs) assume defined reset values:

- `mstatus` — machine mode, interrupts disabled, no floating-point state active.
- `mtvec` — undefined until firmware writes it; exceptions before this is set are implementation-specific.
- `pc` — reset vector address.
- All general-purpose registers — **undefined** (the spec does not require them to be zeroed).

This last point is a common pitfall: firmware must not assume `x0`–`x31` are zero after reset (except `x0`, which is always zero by definition).

## Common Pitfalls

- **Assuming registers are zeroed.** Always initialize any register you read before writing it in early boot code.
- **Forgetting clock gating.** Some peripherals (UART, SPI) need their clocks enabled via a clock-control register before they respond to configuration writes.
- **Stack pointer not set.** The CPU has no stack after reset. Any code that calls a function (even `printf`) before `sp` is initialized will corrupt memory or trap immediately.

## Why This Matters

The reset vector is the absolute first instruction. If it fetches to an invalid address or if the ROM at that address is buggy, the board appears completely dead — no UART output, no debug probe response. Understanding POR is essential for board bring-up and debugging "it won't boot at all" failures.

> **Interview answer:** After power-on reset, the RISC-V hart loads the PC with the implementation-defined reset vector address and begins fetching from there; all CSRs are at reset values but general-purpose registers are uninitialized.
