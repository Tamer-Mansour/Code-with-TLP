# The Interrupt Vector Table

When an interrupt or exception fires, the CPU needs to know *which handler to call*. It looks up the answer in the **Interrupt Vector Table** (IVT) — a data structure that maps each interrupt number (vector) to the address of its handler. On x86 in protected mode and long mode this structure is called the **Interrupt Descriptor Table** (IDT).

---

## What Is a Vector?

A **vector** is simply an 8-bit integer (0–255 on x86) that identifies the source of an interrupt or exception. Think of it as an index into an array of handler pointers.

| Range | Purpose |
|-------|---------|
| 0 – 31 | CPU exceptions (architecture-reserved) |
| 32 – 47 | Hardware IRQs mapped by the PIC/APIC |
| 48 – 255 | Software interrupts, OS-defined, MSI |

---

## Real-Mode IVT (x86 Legacy)

In 8086/real mode, the IVT lives at **physical address 0x0000:0x0000** and contains 256 entries, each 4 bytes (2-byte offset + 2-byte segment):

```
Address 0x0000 ──► [offset_lo][offset_hi][seg_lo][seg_hi]  ← vector 0
Address 0x0004 ──► [offset_lo][offset_hi][seg_lo][seg_hi]  ← vector 1
...
Address 0x03FC ──► ...                                       ← vector 255
```

Total size: 256 × 4 = **1024 bytes** (1 KB).

To compute the ISR address for vector N:

```
physical address of entry = N × 4
ISR segment  = *(uint16_t *)(N*4 + 2)
ISR offset   = *(uint16_t *)(N*4)
```

---

## Protected-Mode / Long-Mode IDT (x86-64)

In protected and long mode, entries are larger (**16 bytes each** in 64-bit mode) and the table can live anywhere in memory. The CPU is told its location via the `LIDT` instruction, which loads the **IDTR** register with the base address and limit.

```asm
lidt [idtr]   ; load IDT base + limit into IDTR
```

Each 64-bit IDT entry (gate descriptor) encodes:

| Field | Bits | Meaning |
|-------|------|---------|
| Offset (low) | 15:0 | Handler address bits 15:0 |
| Segment selector | 31:16 | Code segment for handler |
| IST | 34:32 | Interrupt Stack Table index |
| Type | 43:40 | Gate type (interrupt/trap/task) |
| DPL | 46:45 | Privilege level required to invoke |
| P | 47 | Present bit |
| Offset (mid) | 63:48 | Handler address bits 31:16 |
| Offset (high) | 95:64 | Handler address bits 63:32 |
| Reserved | 127:96 | Must be zero |

Gate types:

- **Interrupt gate** — clears IF (disables interrupts) on entry. Used for hardware IRQs.
- **Trap gate** — does NOT clear IF. Used for exceptions and syscalls.
- **Task gate** — switches to a TSS; rarely used in modern OSes.

---

## Setting Up an IDT Entry in C

```c
#include <stdint.h>

struct idt_entry {
    uint16_t offset_low;
    uint16_t selector;
    uint8_t  ist;
    uint8_t  type_attr;  // P | DPL | 0 | type
    uint16_t offset_mid;
    uint32_t offset_high;
    uint32_t reserved;
} __attribute__((packed));

struct idt_entry idt[256];

void set_idt_gate(int vector, void (*handler)(void),
                  uint16_t sel, uint8_t type_attr) {
    uintptr_t h = (uintptr_t)handler;
    idt[vector].offset_low  = h & 0xFFFF;
    idt[vector].selector    = sel;
    idt[vector].ist         = 0;
    idt[vector].type_attr   = type_attr;
    idt[vector].offset_mid  = (h >> 16) & 0xFFFF;
    idt[vector].offset_high = (h >> 32) & 0xFFFFFFFF;
    idt[vector].reserved    = 0;
}
```

---

## Common IDT Vectors on x86

| Vector | Mnemonic | Description |
|--------|----------|-------------|
| 0 | #DE | Divide Error |
| 6 | #UD | Invalid Opcode |
| 8 | #DF | Double Fault |
| 13 | #GP | General Protection Fault |
| 14 | #PF | Page Fault |
| 32 | IRQ0 | Timer (after PIC remapping) |
| 33 | IRQ1 | Keyboard |
| 128 | — | Linux syscall (`int 0x80`) |

---

## Worked Example

CPU receives vector 14 (page fault):

1. Hardware saves RFLAGS, CS, RIP (and optionally an error code) on the kernel stack.
2. Hardware reads `IDTR` to find the IDT base address.
3. Hardware reads IDT entry 14 to get the handler's 64-bit address.
4. CPU jumps to that address (the page fault handler).
5. Handler reads `CR2` (contains the faulting virtual address) and acts accordingly.

> **Interview answer:** The Interrupt Vector Table (IDT on x86 protected mode) is an array of gate descriptors indexed by vector number. The CPU loads its location from the IDTR register. Each entry holds the full 64-bit handler address plus privilege and type metadata. On an interrupt, the CPU uses the vector as the index, reads the descriptor, and jumps to the handler.
