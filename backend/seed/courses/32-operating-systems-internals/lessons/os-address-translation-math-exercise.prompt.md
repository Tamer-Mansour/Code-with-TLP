# Prompt: Translate a Virtual Address Using a Page Table

## Problem Statement

Simulate a single-level page table address translation. For each virtual address either output the physical address or the string `PAGE FAULT` if the page is not present.

**Algorithm:**

1. Compute `offset_bits = log2(page_size)`.
2. Split: `VPN = va >> offset_bits`, `offset = va & (page_size - 1)`.
3. Look up VPN in the page table.
4. If VPN is not in the table OR present flag is 0: print `PAGE FAULT`.
5. Otherwise: `physical_address = (PFN << offset_bits) | offset`. Print the physical address as a decimal integer.

## Input Format

```
Line 1: page_size            (integer, power of two, 64 <= page_size <= 1073741824)
Line 2: m                    (number of page table entries, 1 <= m <= 500)
Lines 3..m+2: VPN PFN present
    VPN     non-negative integer
    PFN     non-negative integer
    present 0 or 1
Line m+3: n                  (number of virtual addresses, 1 <= n <= 1000)
Lines m+4..m+n+3: va         (non-negative integer, fits in 64-bit unsigned)
```

Each page table entry is unique (no duplicate VPNs in input).

## Output Format

For each virtual address (in order), print one line: the physical address as a decimal integer, or exactly `PAGE FAULT` (all caps).

## Constraints

- `page_size` is always a power of two.
- All addresses fit in 64-bit unsigned integers.
- No trailing spaces; one newline per output line.

## Sample Input 1

```
4096
3
0 5 1
1 2 1
3 7 1
4
0
4096
8192
12288
```

## Sample Output 1

```
20480
8192
PAGE FAULT
28672
```

**Explanation (page size = 4096, offset bits = 12):**
- `va=0`: VPN=0, PFN=5, offset=0 → PA = 5*4096 + 0 = 20480
- `va=4096`: VPN=1, PFN=2, offset=0 → PA = 2*4096 + 0 = 8192
- `va=8192`: VPN=2 → not in page table → PAGE FAULT
- `va=12288`: VPN=3, PFN=7, offset=0 → PA = 7*4096 + 0 = 28672

## Sample Input 2

```
256
4
0 3 1
1 0 0
2 6 1
4 9 1
5
127
256
511
512
1280
```

## Sample Output 2

```
895
PAGE FAULT
PAGE FAULT
1536
PAGE FAULT
```

**Explanation (page size = 256, offset bits = 8):**
- `va=127`: VPN=0, offset=127, PFN=3 → PA = 3*256 + 127 = 895
- `va=256`: VPN=1, present=0 → PAGE FAULT
- `va=511`: VPN=1, present=0 → PAGE FAULT
- `va=512`: VPN=2, offset=0, PFN=6 → PA = 6*256 + 0 = 1536
- `va=1280`: VPN=5 → not in page table → PAGE FAULT
