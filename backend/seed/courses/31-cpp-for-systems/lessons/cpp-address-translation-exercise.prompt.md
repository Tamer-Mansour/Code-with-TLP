# Prompt: Virtual-to-Physical Address Translation

## Problem Statement

Implement address translation for a simple one-level page table. Given a page size (a power of two), a page table mapping VPNs to PFNs, and a list of virtual addresses, output the physical address for each query or `FAULT` if the VPN has no mapping.

## Key Formulas

```
offset_bits  = log2(page_size)
VPN          = virtual_address >> offset_bits
offset       = virtual_address & (page_size - 1)
PA           = (PFN << offset_bits) | offset
```

## Input Format

```
Line 1: page_size           (integer, power of 2)
Line 2: n                   (number of page table entries, 0 <= n <= 256)
Next n lines: VPN PFN       (two non-negative integers, space-separated)
Next line: q                (number of address queries, 1 <= q <= 100)
Next q lines: VA            (one virtual address per line, decimal)
```

## Output Format

For each query output one line:
- The **physical address** as a decimal integer if the VPN is in the page table.
- `FAULT` (all caps) if the VPN has no mapping.

## Constraints

- `1 <= page_size <= 65536`; page_size is always a power of 2.
- VPN and PFN are non-negative integers that fit in a 32-bit unsigned integer.
- All virtual addresses are non-negative integers.
- No duplicate VPN entries in the page table.

## Sample Input

```
256
4
0 5
1 2
2 7
3 1
5
0
255
256
511
1200
```

## Sample Output

```
1280
1535
512
767
FAULT
```

## Explanation

Page size = 256, so offset bits = 8.

- VA=0: VPN=0, offset=0. PFN=5. PA=(5×256)+0=1280.
- VA=255: VPN=0, offset=255. PA=(5×256)+255=1535.
- VA=256: VPN=1, offset=0. PFN=2. PA=(2×256)+0=512.
- VA=511: VPN=1, offset=255. PA=(2×256)+255=767.
- VA=1200: VPN=1200//256=4. No mapping for VPN 4 → FAULT.
