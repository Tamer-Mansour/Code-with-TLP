# Sv39 and Sv48 Virtual Memory Schemes

RISC-V defines several virtual memory schemes for 64-bit systems. The two most important are **Sv39** (39-bit virtual address space) and **Sv48** (48-bit virtual address space). Both use a multi-level radix page table where each level is indexed by a fixed number of bits from the virtual address.

## Address Space Overview

| Scheme | Virtual bits | Page size | Levels | Max VA space | Used by |
|---|---|---|---|---|---|
| Sv32 | 32 | 4 KiB | 2 | 4 GiB | RV32 Linux |
| **Sv39** | 39 | 4 KiB | 3 | 512 GiB | Most 64-bit Linux |
| **Sv48** | 48 | 4 KiB | 4 | 256 TiB | Large-server Linux |
| Sv57 | 57 | 4 KiB | 5 | 128 PiB | Future/experimental |

## Sv39 Virtual Address Layout

A 64-bit virtual address in Sv39 uses only the low 39 bits; bits 63:39 must be sign extensions of bit 38 (canonical form). Any non-canonical address causes an instruction or load/store page fault.

```
 63        39 38      30 29      21 20      12 11            0
  sign-ext   VPN[2]     VPN[1]     VPN[0]     page offset
  (25 bits)  (9 bits)   (9 bits)   (9 bits)   (12 bits)
```

- **VPN[2]** indexes the root page table (level 2).
- **VPN[1]** indexes the level-1 page table.
- **VPN[0]** indexes the level-0 leaf page table.
- **Page offset** (12 bits) selects a byte within the 4 KiB page.

## Sv48 Virtual Address Layout

Sv48 adds one more level, extending the virtual address to 48 bits:

```
 63       48 47      39 38      30 29      21 20      12 11            0
  sign-ext   VPN[3]    VPN[2]     VPN[1]     VPN[0]     page offset
  (16 bits)  (9 bits)  (9 bits)   (9 bits)   (9 bits)   (12 bits)
```

## Page Table Entry (PTE) Format

Both Sv39 and Sv48 use the same 64-bit PTE format:

```
 63    54 53       28 27       19 18       10  9  8  7  6  5  4  3  2  1  0
 reserved  PPN[2]     PPN[1]     PPN[0]    RSW  D  A  G  U  X  W  R  V
```

| Field | Bits | Meaning |
|---|---|---|
| V | 0 | Valid — entry is in use |
| R | 1 | Read permission |
| W | 2 | Write permission |
| X | 3 | Execute permission |
| U | 4 | User-mode accessible |
| G | 5 | Global mapping (present in all address spaces) |
| A | 6 | Accessed bit (set by hardware on access) |
| D | 7 | Dirty bit (set by hardware on store) |
| RSW | 9:8 | Reserved for software use |
| PPN | 53:10 | Physical Page Number of next-level table or leaf |

A PTE with `R=0, W=0, X=0` is a **pointer PTE** (non-leaf) — it points to the next table level. Any other combination of R/W/X is a **leaf PTE** describing actual permissions.

## Huge Pages

Both Sv39 and Sv48 support huge pages by placing a leaf PTE at an intermediate level:

- **Gigapage (1 GiB)**: leaf at level 2 in Sv39 (VPN[1] and VPN[0] become part of the page offset).
- **Megapage (2 MiB)**: leaf at level 1.
- **4 KiB**: normal leaf at level 0.

Huge pages reduce TLB pressure for large contiguous mappings (e.g., the kernel's linear map of all physical RAM).

## Key Differences: Sv39 vs Sv48

| Property | Sv39 | Sv48 |
|---|---|---|
| Virtual address bits | 39 | 48 |
| Page table levels | 3 | 4 |
| Max user/kernel VA | 256 GiB each | 128 TiB each |
| Root table walks | 3 loads | 4 loads |
| Linux default | RV64 default | Opt-in (5.14+) |

## Common Pitfalls

- **Non-canonical addresses.** If bits 63:39 (Sv39) are not all equal to bit 38, the hardware raises a page fault immediately, before any table walk. The kernel must enforce canonical addresses in user-space `mmap` calls.
- **W without R.** The RISC-V spec forbids W=1, R=0 PTEs — this combination is reserved and will cause a fault on compliant hardware.
- **Forgetting to invalidate TLBs.** After modifying a PTE, software must execute `SFENCE.VMA` to flush stale TLB entries.

## Interview Answer

> "Sv39 uses a three-level page table with 9+9+9+12 bit address decomposition, supporting 512 GiB of virtual address space. Sv48 adds a fourth level to reach 256 TiB. Both use the same 64-bit PTE format with RWXUGADV bits and support 4 KiB, 2 MiB, and 1 GiB pages via leaf PTEs at different levels."
