# Prompt: Model a Two-Level MMU Translation (RISC-V Sv32)

## Problem Description

Simulate the RISC-V Sv32 two-level page table walk. Given a memory image, a root page table base (SATP.PPN), and virtual addresses, output the physical address or a fault for each query.

## RISC-V Sv32 Translation Rules

Virtual address (32-bit) layout:
- bits [31:22] = VPN[1]  (10 bits, index into page directory)
- bits [21:12] = VPN[0]  (10 bits, index into page table)
- bits [11:0]  = page offset (12 bits)

Page Table Entry (PTE) — 32-bit word:
- bits [31:10] = PPN (physical page number, 22 bits)
- bit  [0]     = V (valid)
- bit  [1]     = R (readable)
- bit  [2]     = W (writable)
- bit  [3]     = X (executable)

Translation steps:
1. Page directory address = SATP_PPN * 4096
2. PDE address = page_directory_address + VPN[1] * 4
3. Read PDE from memory. If PDE.V == 0 → fault "INVALID_PDE"
4. Page table address = PDE.PPN * 4096
5. PTE address = page_table_address + VPN[0] * 4
6. Read PTE from memory. If PTE.V == 0 → fault "INVALID_PTE"
7. Physical address = PTE.PPN * 4096 + page_offset

Note: For this exercise, treat any non-zero PDE with V=1 as a pointer (not a superpage).

## Input Format

```
SATP_PPN <decimal>
MEM <hex_address> <hex_value>
MEM <hex_address> <hex_value>
...
TRANSLATE <hex_virtual_address>
TRANSLATE <hex_virtual_address>
...
```

- `SATP_PPN` appears exactly once at the start.
- `MEM` lines define the memory image (address and 32-bit value in hex, no 0x prefix).
- `TRANSLATE` lines request translation of a 32-bit virtual address (hex, no 0x prefix).
- At most 256 MEM entries and 50 TRANSLATE queries.
- Memory addresses not listed in MEM lines read as 0x00000000.

## Output Format

For each TRANSLATE query, print one line:

- On success: `VA 0x<8hex> -> PA 0x<8hex>`
- On PDE fault: `VA 0x<8hex> -> FAULT INVALID_PDE`
- On PTE fault: `VA 0x<8hex> -> FAULT INVALID_PTE`

Addresses are printed as 8 lowercase hex digits with a 0x prefix.

## Sample Input

```
SATP_PPN 1
MEM 00001000 00000801
MEM 00002000 00000c01
TRANSLATE 00000000
TRANSLATE 00001000
```

## Sample Output

```
VA 0x00000000 -> PA 0x00003000
VA 0x00001000 -> FAULT INVALID_PTE
```

### Explanation

- SATP_PPN=1, so page directory is at physical address 1×4096 = 0x1000.
- For VA 0x00000000: VPN[1]=0, VPN[0]=0, offset=0.
  - PDE at 0x1000 + 0×4 = 0x1000 → value 0x00000801 → V=1, PPN=2 → page table at 0x2000.
  - PTE at 0x2000 + 0×4 = 0x2000 → value 0x00000c01 → V=1, PPN=3 → PA = 3×4096 + 0 = 0x3000.
- For VA 0x00001000: VPN[1]=0, VPN[0]=1, offset=0.
  - PDE at 0x1000 → V=1, PPN=2, page table at 0x2000.
  - PTE at 0x2000 + 1×4 = 0x2004 → not in MEM → value 0x00000000 → V=0 → FAULT INVALID_PTE.

## Constraints

- All addresses fit in 32 bits.
- Memory values are valid 32-bit unsigned integers.
- At most 256 MEM lines; at most 50 TRANSLATE lines.
