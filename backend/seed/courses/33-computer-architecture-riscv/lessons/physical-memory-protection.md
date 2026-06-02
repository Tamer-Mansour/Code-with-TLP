# Physical Memory Protection (PMP)

Physical Memory Protection (PMP) is a RISC-V hardware mechanism that restricts which physical addresses each privilege level can access. It is the bare-metal equivalent of a virtual-memory MMU: it works directly on physical addresses and requires no page tables, making it essential for microcontroller-class RISC-V cores that never implement virtual memory.

## Why PMP Exists

Without virtual memory, code running in S-mode or U-mode can freely read and write any physical address — including M-mode firmware, interrupt vectors, and device registers. PMP prevents this by defining up to 64 protected regions. Violations trigger an access-fault exception handled in M-mode.

Typical use cases:

- Isolate RTOS tasks from each other on an MCU.
- Prevent a supervisor kernel from touching firmware secrets.
- Lock MMIO regions so only M-mode can configure critical peripherals.

## PMP Registers

PMP is configured through two sets of CSRs:

| CSR | Count | Width | Purpose |
|---|---|---|---|
| `pmpcfg0`–`pmpcfg15` | 16 | XLEN | 8-bit config per entry, packed 4 or 8 per CSR |
| `pmpaddr0`–`pmpaddr63` | 64 | XLEN | Address of each region |

Each 8-bit config field contains:

```
 7   6   5   4   3   2   1   0
 L   -   -   A1  A0  X   W   R
```

- **R/W/X**: Read, Write, Execute permission bits.
- **A (address-matching mode)**:
  - `00` = OFF (entry disabled)
  - `01` = TOR (Top Of Range; uses previous entry as base)
  - `10` = NA4 (naturally aligned 4-byte region)
  - `11` = NAPOT (naturally aligned power-of-two region)
- **L (lock)**: When set, the entry is locked — it cannot be modified even by M-mode until reset.

## NAPOT Encoding

NAPOT is the most efficient mode for power-of-two regions. The address register encodes both the base and size:

- For a 4 KiB region at `0x8000_0000`: write `0x8000_0000 >> 2 | 0x1FF` = `0x2000_07FF`
- General formula: `addr[bits] = (base >> 2) | ((size/8) - 1)`

```c
// Helper: compute pmpaddr value for a NAPOT region
static inline uintptr_t napot_addr(uintptr_t base, size_t size) {
    return (base >> 2) | ((size / 8) - 1);
}
```

## Example: Protecting DRAM from U-mode

```c
#include <stdint.h>

// Allow S/U-mode to access 0x80000000..0x87FFFFFF (128 MiB), R/W/X
void pmp_allow_dram(void) {
    uintptr_t addr = napot_addr(0x80000000UL, 128 * 1024 * 1024);
    asm volatile("csrw pmpaddr0, %0" :: "r"(addr));

    // pmpcfg0 byte 0: NAPOT (A=11), R=1, W=1, X=1 => 0x1F
    asm volatile("csrw pmpcfg0, %0" :: "r"(0x1FUL));
}
```

After this setup, U-mode accesses to `[0x8000_0000, 0x8800_0000)` succeed; any other physical access raises an access fault.

## PMP and Virtual Memory

When a system uses Sv39/Sv48 virtual memory, PMP checks happen *after* address translation — the translated physical address is checked against PMP entries. This creates a two-layer permission system: the MMU page tables restrict virtual access, and PMP further restricts the resulting physical access.

## Common Pitfalls

- **Forgetting to cover M-mode code.** By default M-mode bypasses PMP. Once you set the L bit on an entry it applies to M-mode too — be careful not to lock yourself out.
- **Entry priority.** PMP entries are checked in order (entry 0 first); the first matching entry wins. If no entry matches, U/S-mode access is denied; M-mode access is allowed.
- **Granularity.** The minimum region size is 4 bytes (NA4) or platform-defined (often 4 KiB when the `G` field is non-zero). Check the platform's PMP granularity before using small regions.

## Interview Answer

> "PMP uses up to 64 CSR-configured regions to restrict physical memory access by privilege level. Each entry specifies a base address, size (via NAPOT or TOR mode), and R/W/X permissions. Violations generate an access-fault exception. PMP checks fire after virtual-address translation in systems that use an MMU."
