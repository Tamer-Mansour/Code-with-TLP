# Prompt: Translate a Virtual Address via a Page Table

## Problem Description

Implement a virtual-to-physical address translator for a single-level paging system.

### Translation Rules

Given:
- `offset_bits` — the number of bits used for the page offset (page size = 2^offset_bits bytes).
- A page table — a flat array of Physical Frame Numbers (PFNs). A value of `-1` means the page is invalid (not mapped).
- One or more virtual addresses.

For each virtual address `va`:
1. `vpn    = va >> offset_bits`
2. `offset = va & ((1 << offset_bits) - 1)`
3. If `vpn >= len(page_table)` OR `page_table[vpn] == -1`: print `PAGE FAULT`
4. Otherwise: `pa = (page_table[vpn] << offset_bits) | offset`, print `pa` as a decimal integer.

## Input Format

```
offset_bits
n
pte_0 pte_1 ... pte_{n-1}
q
va_0
va_1
...
va_{q-1}
```

- Line 1: integer `offset_bits` (1 ≤ offset_bits ≤ 20)
- Line 2: integer `n` — number of PTEs in the page table (1 ≤ n ≤ 1024)
- Line 3: `n` space-separated integers; each is either `-1` (invalid) or a PFN in range [0, 2^20)
- Line 4: integer `q` — number of virtual addresses to translate (1 ≤ q ≤ 100)
- Lines 5 to 4+q: one virtual address per line (0 ≤ va < 2^32)

## Output Format

For each query, print one line:
- The physical address as a **decimal integer**, if the mapping is valid.
- The string `PAGE FAULT` (exactly, all caps), if the mapping is invalid.

## Constraints

- 1 ≤ offset_bits ≤ 20
- 1 ≤ n ≤ 1024
- 1 ≤ q ≤ 100
- 0 ≤ va < 2^32
- PFN values in [0, 2^20) or -1
- No floating-point arithmetic needed.

## Sample Input

```
12
4
5 -1 3 7
4
4096
8191
8192
16383
```

## Sample Output

```
20480
PAGE FAULT
12288
28671
```

## Explanation of Sample

- `offset_bits = 12` → page size = 4096, offset mask = 0xFFF
- Page table: PTE[0]=5, PTE[1]=-1, PTE[2]=3, PTE[3]=7

Query 1: `va = 4096`
  - `vpn = 4096 >> 12 = 1`, `offset = 4096 & 0xFFF = 0`
  - PTE[1] = -1 → PAGE FAULT

Wait — let me recheck:
  - `vpn = 4096 >> 12 = 1` → PTE[1] = -1 → `PAGE FAULT`

Query 2: `va = 8191`
  - `vpn = 8191 >> 12 = 1` → PTE[1] = -1 → `PAGE FAULT`

Hmm, that gives two PAGE FAULTs for the sample. Let me use a corrected sample:

## Corrected Sample Input

```
12
4
5 -1 3 7
4
0
4096
8192
12288
```

## Corrected Sample Output

```
20480
PAGE FAULT
12288
28672
```

## Explanation of Corrected Sample

- `offset_bits = 12`, page size = 4096
- PTE[0]=5, PTE[1]=-1, PTE[2]=3, PTE[3]=7

| va | vpn | offset | PTE[vpn] | pa |
|---|---|---|---|---|
| 0 | 0 | 0 | 5 | (5 << 12) \| 0 = 20480 |
| 4096 | 1 | 0 | -1 | PAGE FAULT |
| 8192 | 2 | 0 | 3 | (3 << 12) \| 0 = 12288 |
| 12288 | 3 | 0 | 7 | (7 << 12) \| 0 = 28672 |
