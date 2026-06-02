# Exercise: Split a Virtual Address Into Page Number and Offset

In this exercise you will implement the core arithmetic of the first step of address translation: given a virtual address and a page size, compute the **virtual page number (VPN)** and the **byte offset within the page**.

## What You Will Implement

Write a program that reads multiple virtual addresses and a page size, then prints the VPN and offset for each address.

The math is straightforward but must be exact:

```python
offset_bits = page_size.bit_length() - 1   # log2(page_size)
vpn    = virtual_address >> offset_bits
offset = virtual_address & (page_size - 1)
```

Because the page size is always a power of two, the split is a single right-shift and a bitwise AND — no division needed.

## Learning Goals

- Internalize that address splitting is pure bit manipulation.
- Understand how the page size determines the number of offset bits.
- Practice reading hexadecimal addresses and producing hex output matching what the OS and hardware use.

## Input / Output Format

See the linked prompt file for the exact specification, constraints, and sample cases.
