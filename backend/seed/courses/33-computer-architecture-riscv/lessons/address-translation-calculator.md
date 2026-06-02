# Exercise: Translate a Virtual Address via a Page Table

In this exercise you will implement a **virtual-to-physical address translator** for a simplified single-level paging system. The goal is to cement your understanding of how the MMU splits a virtual address into a page number and offset, indexes into a page table, and constructs the physical address.

## What You Will Implement

Write a program that reads a page table (a list of page table entries) and one or more virtual addresses, then outputs the corresponding physical address for each — or reports a page fault if the mapping is invalid.

## The Simplified Model

- **Page size**: configurable (always a power of 2, given as the number of offset bits).
- **Page table**: given as a flat list of PTEs. Each PTE is either `-1` (invalid / page fault) or a non-negative physical frame number (PFN).
- **Virtual address**: an unsigned integer.
- **Translation rule**:
  - `vpn = va >> offset_bits`
  - `offset = va & ((1 << offset_bits) - 1)`
  - If `vpn >= len(page_table)` or `page_table[vpn] == -1`: output `PAGE FAULT`
  - Otherwise: `pa = (page_table[vpn] << offset_bits) | offset`

## Input / Output

See the linked prompt file for the exact stdin/stdout format, constraints, and sample test cases.

## Why This Matters

Manually translating addresses is a standard OS / computer-architecture interview whiteboard problem. Interviewers use it to verify that you understand:

- The bit-field decomposition of an address.
- The difference between VPN and PFN.
- That the offset passes through unchanged.
- What a page fault means.

Work through each test case by hand before running your code — that deliberate practice is what makes the concept stick.
