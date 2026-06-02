# Exercise: Translate an Sv39 Virtual Address

In this exercise you will implement the Sv39 page table walk algorithm in software. Given a description of page table entries in memory, you will compute the resulting physical address (or detect a fault condition).

## What You Will Implement

Write a program that reads:

1. A 64-bit virtual address to translate.
2. A series of PTE values at specific physical addresses (simulating physical memory).
3. The `satp` PPN (root page table page number).

Your program must:

- Decompose the virtual address into VPN[2], VPN[1], VPN[0], and the 12-bit page offset.
- Walk the three-level Sv39 page table using the provided PTE table.
- Detect and report faults (invalid PTE, reserved encoding, permission issues).
- Output the final physical address on success.

## Key Formulas

```
VPN[2] = (va >> 30) & 0x1FF
VPN[1] = (va >> 21) & 0x1FF
VPN[0] = (va >> 12) & 0x1FF
offset = va & 0xFFF

pte_phys_addr = (table_ppn * 4096) + (vpn * 8)
physical_addr = (leaf_pte_ppn * 4096) + offset
```

A PTE is a **leaf** when R=1 or X=1. A PTE with V=0 is invalid (FAULT). A PTE with V=1, R=0, W=1, X=0 is reserved (FAULT).

## What to Submit

Implement a Python program that reads from stdin and writes to stdout exactly as specified in the prompt file. No third-party libraries are permitted.
