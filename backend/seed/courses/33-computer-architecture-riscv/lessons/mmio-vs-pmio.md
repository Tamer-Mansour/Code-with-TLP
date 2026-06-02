# Memory-Mapped vs Port-Mapped I/O

Having studied both MMIO and PMIO individually, it is worth comparing them directly. Knowing the tradeoffs is a common interview topic and is essential for anyone writing low-level firmware, kernel drivers, or embedded code.

## Side-by-Side Comparison

| Feature | Memory-Mapped I/O (MMIO) | Port-Mapped I/O (PMIO) |
|---|---|---|
| Address space | Shared with RAM | Separate 16-bit I/O space |
| Instructions used | Normal load/store | `IN` / `OUT` (x86 only) |
| Architecture support | Universal (ARM, RISC-V, x86, MIPS…) | x86 only |
| Address range | Up to full physical address space | 65,536 ports (0x0000–0xFFFF) |
| Caching | Must disable (non-cacheable pages) | Not applicable (no cache path) |
| `volatile` needed in C | Yes | Not needed (instructions are always side-effectful) |
| Hardware protection | OS page-table attributes | IOPL / I/O Permission Bitmap |
| Performance | Can be slower (cache bypass required) | Similar, but no pipeline hazards from cache coherence |
| Modern usage | Dominant — all PCIe, USB, embedded | Legacy x86 devices only |

## Address Space Implications

With MMIO, the OS must carve out physical address ranges for devices and ensure those ranges are never handed to `malloc` or the page allocator. On a 64-bit system this is trivial — the address space is vast. On 32-bit embedded systems it requires careful linker scripts and memory maps.

```
Example: 32-bit embedded memory map
0x00000000 – 0x1FFFFFFF   Flash (read-only code/data)
0x20000000 – 0x2001FFFF   SRAM
0x40000000 – 0x5FFFFFFF   APB peripherals (MMIO)
0xE0000000 – 0xE00FFFFF   Cortex-M System peripherals (MMIO)
```

PMIO never has this concern because ports and RAM are entirely separate; a port number of `0x0060` is unrelated to memory address `0x0060`.

## Instruction Set Perspective

RISC-V has no `IN`/`OUT` equivalents. Every I/O operation is a regular `lw`/`sw` (load-word / store-word):

```asm
# RISC-V: read from UART status register at 0x10013004
lui  t0, 0x10013        # t0 = 0x10013000
lw   t1, 4(t0)          # t1 = *(0x10013004)  -> UART status

# x86: read from COM1 status register at I/O port 0x03FD
mov  dx, 0x03FD
in   al, dx             # al = inb(0x03FD)    -> UART LSR
```

This design simplicity is intentional in RISC-V — fewer instruction types means a simpler decoder and smaller silicon area.

## Cache Coherence Challenge (MMIO Only)

Because device memory sits in the CPU's physical address space, the cache subsystem must know not to cache those addresses. If a CPU caches a read from an MMIO register, subsequent reads will return the cached (stale) value instead of the live hardware state.

Solutions:

1. **Non-cacheable memory attributes** — Mark device pages as Device or Strongly-Ordered in the page tables (ARM/x86) or PMP/PTE attributes (RISC-V).
2. **Cache maintenance** — Flush and invalidate cache lines covering a device region before/after DMA (discussed later in the module).
3. **`volatile` in C** — Prevents the *compiler* from caching values in registers, but does not control hardware caches. Both `volatile` and non-cacheable mapping are required.

## When Would You Choose One Over the Other?

In practice the choice is rarely yours to make — it is dictated by the architecture:

- **x86 legacy drivers** — Use PMIO for devices that historically mapped to I/O ports (keyboard, PIT, PIC). Use MMIO for all modern PCIe devices.
- **ARM / RISC-V embedded** — MMIO only. No choice exists.
- **Writing portable driver code** — Abstract the difference behind `read_reg()` / `write_reg()` functions:

```c
// Portable abstraction hiding MMIO vs PMIO
#ifdef CONFIG_MMIO
    #define read_reg(base, off)      (*(volatile uint32_t *)((base) + (off)))
    #define write_reg(base, off, v)  (*(volatile uint32_t *)((base) + (off)) = (v))
#else  // PMIO (x86)
    #define read_reg(base, off)      inl((base) + (off))
    #define write_reg(base, off, v)  outl((base) + (off), (v))
#endif
```

## Summary

MMIO is the modern, universal approach. PMIO is an x86-only legacy mechanism maintained for backward compatibility. Both exist to let software control hardware through a simple read/write interface; they differ only in which address space hosts that interface.

> **Interview answer:** MMIO maps device registers into the normal physical address space so any load/store instruction can reach them; it works on every architecture and is the only option on ARM and RISC-V. PMIO uses a separate 16-bit I/O port space on x86 accessible only via IN/OUT instructions; it is simpler to protect but limited to 65,536 ports and the x86 architecture.
