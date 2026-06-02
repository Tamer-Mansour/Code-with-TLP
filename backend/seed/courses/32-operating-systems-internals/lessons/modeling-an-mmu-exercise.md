# Exercise: Model a Two-Level MMU Translation

In this exercise you will implement the address translation logic used by a RISC-V Sv32 MMU. The Memory Management Unit converts a virtual address issued by software into a physical address using a two-level page table walk — the exact process the Linux kernel relies on to isolate processes.

## Background

RISC-V Sv32 uses 32-bit virtual addresses divided into three fields:

```
 31       22 21       12 11          0
+----------+-----------+-------------+
|  VPN[1]  |  VPN[0]   | page offset |
| (10 bits)| (10 bits) | (12 bits)   |
+----------+-----------+-------------+
```

The translation algorithm:

1. Read the root **Page Directory** base address from the SATP register (physical address = SATP.PPN × 4096).
2. Index it with VPN[1] to get a **Page Directory Entry (PDE)**.
3. If PDE.V=1 and it is a pointer (not a leaf), read the **Page Table** at PDE.PPN × 4096.
4. Index it with VPN[0] to get a **Page Table Entry (PTE)**.
5. Check PTE.V=1 and permission bits (R/W/X/U).
6. Physical address = PTE.PPN × 4096 + page offset.

Each PTE is a 32-bit word with this layout:

```
 31        10  9   8   7   6   5   4   3   2   1   0
+------------+---+---+---+---+---+---+---+---+---+---+
|  PPN[19:0] | RSW   | D | A | G | U | X | W | R | V |
+------------+-------+---+---+---+---+---+---+---+---+
```

- **V** = Valid
- **R/W/X** = Read/Write/Execute permissions
- **U** = User-accessible
- **PPN** = Physical Page Number (bits 31:10)

## What You Will Implement

Your program receives a complete simulated memory image (a set of address→value mappings), the SATP.PPN value, and one or more virtual addresses. For each virtual address it must perform the two-level Sv32 page table walk and output either the physical address or a fault reason.

This exercise directly models what the Linux kernel's `__do_page_fault` path and the MMU hardware do on every memory access.
