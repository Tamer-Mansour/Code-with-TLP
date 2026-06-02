# The RISC-V Page Table Walk

When the RISC-V MMU receives a virtual address with paging enabled, it performs a **page table walk** — a hardware-executed sequence of physical memory loads that traverses the tree of page tables and resolves the translation. Understanding the exact algorithm is key to writing correct OS code, debugging translation faults, and passing systems interviews.

## The Walk Algorithm (Sv39)

The RISC-V privileged spec defines the walk as a pseudocode loop. Here is the equivalent in clear steps for Sv39 (3-level tables):

```
Given: virtual address va, satp register

1. levels = 3, page_size = 4096
   a = satp.PPN * page_size            # root page table physical address
   i = levels - 1                      # start at level 2

2. LOOP:
   pte_addr = a + VPN[i] * 8           # PTE is 8 bytes wide
   pte = phys_load_64(pte_addr)        # hardware loads the PTE

3. if pte.V == 0:                      # V bit clear
       FAULT (page fault)

4. if pte.R == 0 and pte.W == 1:       # reserved combination
       FAULT (page fault)

5. if pte.R == 1 or pte.X == 1:        # leaf PTE found
       goto LEAF

6. else:                               # pointer PTE (non-leaf)
       i = i - 1
       if i < 0: FAULT
       a = pte.PPN * page_size
       goto LOOP

7. LEAF:
   # Check alignment for huge pages
   if i > 0 and pte.PPN[i-1:0] != 0:  # misaligned huge page
       FAULT

   # Check permissions vs access type
   check R/W/X/U bits vs. access type and privilege level
   if check fails: FAULT

   # Construct physical address
   pa.offset    = va[11:0]
   pa.PPN[i-1:0] = va.VPN[i-1:0]      # for huge pages
   pa.PPN[levels-1:i] = pte.PPN[levels-1:i]
   return pa
```

## Worked Example

Translate virtual address `0x0000_0000_4020_1ABC` using Sv39 with a root page table at physical `0x8000_0000`.

**Step 1 — Decompose the VA:**

```
VA = 0x0000_0000_4020_1ABC
   = 0b 000_000_000  001_000_000  010_000_000  001_1010_1011_1100

VPN[2] = 0b000_000_000 = 0
VPN[1] = 0b001_000_000 = 64  (0x40)
VPN[0] = 0b010_000_000 = 128 (0x80) -- wait, let me re-expand correctly

VA bits [38:30] = VPN[2]
VA bits [29:21] = VPN[1]
VA bits [20:12] = VPN[0]
VA bits [11:0]  = offset = 0xABC

0x4020_1ABC = 0100 0000 0010 0000 0001 1010 1011 1100
              [38:30]=[0x01]  [29:21]=[0x01] [20:12]=[0x01]  [11:0]=0xABC

Actual decomposition of 0x4020_1ABC:
  Binary: 0100_0000_0010_0000_0001_1010_1011_1100
  VPN[2] = bits 38:30 → 0x00 (top 9 bits are 0 in a 39-bit VA)
  VPN[1] = bits 29:21 → 0x02 (0b000_000_010 = 2)
  VPN[0] = bits 20:12 → 0x01 (0b000_000_001 = 1)
  offset = bits 11:0  → 0xABC
```

**Step 2 — Level 2 load:**
```
pte_addr = 0x8000_0000 + 0 * 8 = 0x8000_0000
pte      = load(0x8000_0000) → 0x0000_0000_2000_04CF  (V=1, R=0, W=0, X=0 → pointer)
a        = pte.PPN * 4096 = 0x8001_0000
```

**Step 3 — Level 1 load:**
```
pte_addr = 0x8001_0000 + 2 * 8 = 0x8001_0010
pte      = load(0x8001_0010) → 0x0000_0000_2000_84CF  (V=1, R=0, W=0, X=0 → pointer)
a        = pte.PPN * 4096 = 0x8002_0000
```

**Step 4 — Level 0 (leaf) load:**
```
pte_addr = 0x8002_0000 + 1 * 8 = 0x8002_0008
pte      = load(0x8002_0008) → 0x0000_0000_2000_C0CF  (V=1, R=1, W=1, X=0 → leaf)
PA       = pte.PPN * 4096 + offset = 0x8003_0000 + 0xABC = 0x8003_0ABC
```

## Hardware vs Software Walk

Most RISC-V implementations use a **hardware page table walker (PTW)** — dedicated silicon that performs the walk automatically on a TLB miss. RISC-V also permits software-managed TLBs (rare), where a TLB-miss trap invokes an M-mode handler that performs the walk manually.

## Accessed and Dirty Bits

If the hardware supports A/D bit updates, it sets the **A** (Accessed) bit on every successful translation and the **D** (Dirty) bit on every store. If the hardware does not support automatic updates, the A/D bits start at 0 and the hardware faults, letting the OS set them in software.

## Common Pitfalls

- **Ignoring the huge-page alignment check.** A megapage or gigapage PPN must have the appropriate low bits zero; otherwise it is a misaligned huge page and triggers a fault.
- **Confusing physical and virtual addresses.** The `a` variable in the walk is always a *physical* address. Before paging is enabled, the page tables are constructed using physical pointers; once enabled, the kernel must have its own virtual mappings consistent.
- **Not checking U-bit.** A leaf PTE with U=0 is supervisor-only. An access from U-mode causes a page fault even if R/W/X match.

## Interview Answer

> "The RISC-V page table walk iterates from the root (pointed to by satp.PPN) downward through levels, each time loading a PTE at the address formed by the current table base plus the appropriate VPN index times 8. A non-leaf PTE (R=0, W=0, X=0, V=1) descends to the next level; a leaf PTE ends the walk and provides permission bits and the physical page number."
