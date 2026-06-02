# Exercise: Virtual-to-Physical Address Translation Math

In this exercise you will implement the core arithmetic of virtual-to-physical address translation, the same calculation an MMU performs on every memory access.

## What You Will Implement

Given a **page size** (always a power of two), a **page table** (a list of VPN→PFN mappings), and a list of **virtual addresses**, your program must:

1. Compute the **Virtual Page Number (VPN)** and **offset** for each address.
2. Look up the PFN in the page table.
3. Output the **physical address**, or `FAULT` if the VPN has no mapping.

## Key Formulas

```
offset_bits = log2(page_size)
VPN         = virtual_address >> offset_bits
offset      = virtual_address & (page_size - 1)
PA          = (PFN << offset_bits) | offset
```

## Input / Output Format

See the prompt file for the exact stdin/stdout specification and sample cases.

## Learning Goals

After completing this exercise you will be able to:

- Quickly derive VPN and offset from any virtual address given a page size.
- Understand what a page fault means at the hardware level.
- Explain address translation arithmetic in an interview without hesitation.
