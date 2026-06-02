# Port-Mapped vs Memory-Mapped I/O

The CPU must reach device registers somehow. Two competing architectures have coexisted since the 1970s; knowing both — and when each is preferred — is a recurring interview topic.

## Port-Mapped I/O (PMIO)

Also called **isolated I/O** or **I/O-mapped I/O**. The device registers live in a completely separate address space — the **I/O address space** — distinct from RAM. On x86, this space is 16-bit wide (addresses 0x0000–0xFFFF, giving 65536 ports).

The CPU uses dedicated instructions to access it:

```asm
; x86 assembly — read one byte from port 0x60 (PS/2 keyboard data port)
in  al, 0x60

; Write byte 0x3C to port 0x3D4 (VGA CRT index register)
mov al, 0x3C
out 0x3D4, al
```

In C (Linux kernel / GCC builtins):

```c
#include <sys/io.h>

uint8_t  val = inb(0x60);   // read byte
outb(0x3C, 0x3D4);          // write byte
```

### PMIO Characteristics

| Attribute | Detail |
|---|---|
| Address space | Separate, 16-bit on x86 |
| Instructions | `IN` / `OUT` (privileged in ring 0) |
| Hardware | Requires a dedicated `M/IO#` control pin on the bus |
| Isolation | Naturally isolated — a buggy load/store can't hit a register |
| Portability | x86-specific; ARM, RISC-V, MIPS do not have PMIO |

## Memory-Mapped I/O (MMIO)

Device registers are **assigned physical addresses** in the same address space as RAM. The CPU uses ordinary load and store instructions — no special opcodes needed.

```c
// ARM Cortex-A: GPIO base at 0xFE200000 (Raspberry Pi)
#define GPIO_BASE  0xFE200000UL
#define GPFSEL0    (*(volatile uint32_t *)(GPIO_BASE + 0x00))
#define GPSET0     (*(volatile uint32_t *)(GPIO_BASE + 0x1C))

// Set GPIO pin 17 to output
GPFSEL0 |= (1 << 21);   // bits [23:21] for pin 17

// Assert GPIO 17 high
GPSET0   = (1 << 17);
```

### MMIO Characteristics

| Attribute | Detail |
|---|---|
| Address space | Shared with RAM (but regions are non-cacheable by default) |
| Instructions | Normal `LD` / `ST` (or `LDR`/`STR` on ARM) |
| Hardware | No extra bus signal needed |
| Caching | Must mark pages non-cacheable (e.g., `PAGE_KERNEL_IO` in Linux) |
| Portability | Works on every modern ISA |

## Head-to-Head Comparison

| Criterion | PMIO | MMIO |
|---|---|---|
| ISA support | x86 only | Universal |
| Cache risk | None (bypasses cache) | Must explicitly disable caching |
| Address range | 64 KB fixed | Limited only by physical address bus |
| Debug difficulty | Requires special tools | Visible in `/proc/iomem`, easy to memory-probe |
| Modern usage | Legacy x86 (COM, LPT, DMA chip) | All ARM/RISC-V, PCIe BARs, SoC peripherals |

## Why MMIO Won

1. **No extra ISA surface** — eliminating `IN`/`OUT` simplifies CPU design; every RISC architecture dropped dedicated I/O instructions.
2. **Larger register space** — 64 KB of ports is tiny compared to a 48-bit physical address space.
3. **Unified tooling** — debuggers, memory analyzers, and hypervisors already handle memory; no special-case code needed for I/O.

PCIe **Base Address Registers (BARs)** are the canonical modern example: the OS reads a device's BARs, allocates a physical address range, and the device's registers appear at those addresses. All driver code then uses plain pointer dereferences.

## Common Pitfall: Caching MMIO Regions

If the CPU caches a read from an MMIO register, it may return a stale value from a previous read rather than the current hardware state. Always:

- Mark MMIO pages as **non-cacheable** in the MMU page tables.
- Use `volatile` on all register pointers in C/C++.
- On ARM, use `ioremap_nocache()` (Linux) which sets the correct memory attributes automatically.

> **Interview answer:** PMIO uses a separate I/O address space accessed via `IN`/`OUT` instructions (x86 only); MMIO maps device registers into the normal physical address space so ordinary loads and stores reach them. MMIO is universal, scales to large register sets, and is used by all modern SoC and PCIe peripherals; PMIO survives only in legacy x86 PC hardware.
