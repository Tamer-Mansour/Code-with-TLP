# The System Address Map

The **system address map** (sometimes called the memory map) is the specification that assigns every byte in a processor's address space to a named region: RAM, Flash, peripheral registers, or an unmapped hole. It is the single most important document an embedded firmware engineer needs when bring-up starts.

## Why a Single Flat Address Space?

Modern SoC buses present one flat 32-bit or 64-bit address space to the CPU. Every peripheral, no matter how heterogeneous, is reached through ordinary load and store instructions targeting that space. The address map is what converts a physical address like `0x4000_2800` into "SPI1 control registers on APB1."

## Anatomy of an Address Map Entry

Each region needs at minimum:

| Field | Purpose | Example |
|---|---|---|
| `name` | Human-readable label | `"SRAM1"` |
| `base` | First byte address | `0x2000_0000` |
| `size` | Region length in bytes | `0x0002_0000` (128 KB) |
| `end` (derived) | `base + size - 1` | `0x2001_FFFF` |
| `type` | RAM / ROM / MMIO / reserved | `RAM` |
| `access` | R, W, RW, R-only | `RW` |

## A Typical Cortex-M Address Map

ARM Cortex-M defines a standard layout that chip vendors follow:

```
Address Range           Region              Notes
------------------      ----------------    ---------------------------------
0x0000_0000 - 0x1FFF_FFFF  Code           Flash / ROM (512 MB)
0x2000_0000 - 0x3FFF_FFFF  SRAM           Internal data RAM (512 MB)
0x4000_0000 - 0x5FFF_FFFF  Peripherals    APB/AHB registers (512 MB)
0x6000_0000 - 0x9FFF_FFFF  External RAM   FSMC / FMC (1 GB)
0xA000_0000 - 0xBFFF_FFFF  External Flash FSMC / FMC (512 MB)
0xE000_0000 - 0xE00F_FFFF  Private PPB    NVIC, SysTick, CoreSight
```

Each chip vendor then sub-divides the peripheral band. On an STM32F4:

```
0x4000_0000  TIM2        (APB1)
0x4000_1400  USART2      (APB1)
0x4001_3000  SPI1        (APB2)
0x4002_0000  DMA1        (AHB1)
0x4002_3000  GPIOA       (AHB1)
```

## Representing the Map in a Virtual Prototype

In a TLM platform the address map lives in the **router** (or interconnect). A simple representation is a sorted vector of entries:

```cpp
struct MapEntry {
    sc_dt::uint64  base;
    sc_dt::uint64  size;
    std::string    name;
    tlm::tlm_target_socket_base* target; // pointer to the socket
};

std::vector<MapEntry> map = {
    { 0x0000'0000, 0x0008'0000, "Flash",  &flash.socket  },
    { 0x2000'0000, 0x0002'0000, "SRAM",   &sram.socket   },
    { 0x4000'0000, 0x0400'0000, "Periph", &periph.socket },
};
```

The router iterates the vector, finds the first entry where `base <= addr < base + size`, then forwards the transaction.

## Gaps and Reserved Regions

Not every address is mapped. Accessing an unmapped gap should return a bus-error (`TLM_ADDRESS_ERROR_RESPONSE`). Some routers assert a "default slave" target that returns `0xDEADBEEF` on reads — a debugging aid that makes uninitialised pointer dereferences immediately visible.

## Common Pitfalls

- **Off-by-one on `end`**: The last valid byte is `base + size - 1`, not `base + size`. Code that uses `<=` vs `<` is a frequent bug.
- **Overlapping regions**: Two entries covering the same address create ambiguity. Always validate the map at elaboration time.
- **Endianness of the map**: The map is always in the CPU's physical address space. Endianness affects byte ordering within a word, not address assignment.

## Interview Answer

> "The system address map assigns every address in the CPU's flat address space to a named region — Flash, SRAM, or peripheral — with a base address and size. The virtual-prototype router uses it to decode transactions and forward them to the correct target socket."
