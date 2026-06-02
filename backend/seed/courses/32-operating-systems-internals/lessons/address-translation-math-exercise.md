# Exercise: Translate a Virtual Address Using a Page Table

In this exercise you will simulate the core of the MMU's address translation: look up a virtual page number in a page table and produce the physical address (or detect a page fault).

## What You Will Implement

Given a page size, a page table (VPN → PFN mappings with a present bit), and a list of virtual addresses, your program must:

1. Split each virtual address into VPN and offset.
2. Look up the VPN in the page table.
3. If the entry exists and is present, compute the physical address as `(PFN << offset_bits) | offset`.
4. If the entry is missing or marked not-present, output `PAGE FAULT`.

```python
offset_bits = page_size.bit_length() - 1
vpn    = va >> offset_bits
offset = va & (page_size - 1)

entry = page_table.get(vpn)
if entry is None or not entry['present']:
    print("PAGE FAULT")
else:
    pa = (entry['pfn'] << offset_bits) | offset
    print(pa)
```

## Learning Goals

- Perform the full VPN → PFN lookup that the MMU hardware executes.
- Handle both the happy path and the page-fault path.
- Understand that the offset is copied unchanged into the physical address.

## Input / Output Format

See the linked prompt file for the complete specification, constraints, and sample test cases.
