# Virtual-to-Physical Address Translation

Address translation is the mechanism the MMU performs on every memory access. This lesson walks through the exact steps, from the raw virtual address to the final physical address, using RISC-V Sv32 as the concrete example.

## The Two Inputs

The MMU needs two things to translate an address:

1. **The virtual address** — supplied by the CPU pipeline.
2. **The root page table pointer** — stored in the `satp` CSR.

## Step-by-Step Translation (Sv32, Single-Level Simplified)

Sv32 uses a **two-level** page table, but let us first understand the single-level logic before stacking levels.

### Step 1: Split the Virtual Address

```
Virtual address (32 bits):
 ┌──────────────────────┬──────────────────┐
 │   VPN (bits 31:12)   │  Offset (11:0)   │
 └──────────────────────┴──────────────────┘
```

Example: `VA = 0x00403ABC`

```
VPN    = 0x00403ABC >> 12 = 0x403   (decimal 1027)
Offset = 0x00403ABC & 0xFFF = 0xABC
```

### Step 2: Look Up the Page Table Entry

The page table is an array in physical memory. Its base address comes from `satp.PPN << 12`.

```
PTE_address = (satp.PPN << 12) + VPN * sizeof(PTE)
            = page_table_base + 1027 * 4
```

The MMU performs a physical memory read at `PTE_address` to fetch the PTE.

### Step 3: Validate the PTE

The MMU checks:

- **V bit = 1**: the mapping is valid. If `V = 0` → page fault.
- **R/W/X bits match the access type**: a write to an R-only page → fault.
- **U bit matches privilege level**: user accessing a supervisor page → fault.

### Step 4: Extract the Physical Frame Number

```
PFN = PTE[31:10]   (22 bits in Sv32)
```

Example: PTE value = `0x0006_040F`

```
Binary: 0000 0000 0000 0110 0000 0100 | 0000 1111
PFN = bits 31:10 = 0x0018  (decimal 24)
Flags = bits 9:0 = 0x00F  (V=1, R=1, W=1, X=1, U=0)
```

### Step 5: Construct the Physical Address

```
PA = (PFN << 12) | Offset
   = (0x18 << 12) | 0xABC
   = 0x18000 | 0xABC
   = 0x18ABC
```

Full worked example in Python:

```python
va     = 0x00403ABC
satp_ppn = 0x1000        # page table at physical 0x1000_000

vpn    = va >> 12        # 0x403
offset = va & 0xFFF      # 0xABC

pte_addr = (satp_ppn << 12) + vpn * 4   # physical address of PTE
# Assume memory read returns:
pte    = 0x0006040F
v_bit  = pte & 1          # 1 — valid
pfn    = pte >> 10        # 0x18
pa     = (pfn << 12) | offset
print(hex(pa))             # 0x18abc
```

## Two-Level Translation (Sv32 Reality)

Sv32 actually splits the VPN into two 10-bit halves to form a **two-level** tree:

```
VA (32 bits):
 ┌──────────┬──────────┬──────────────────┐
 │  VPN[1]  │  VPN[0]  │     Offset       │
 │ (31:22)  │ (21:12)  │    (11:0)        │
 └──────────┴──────────┴──────────────────┘
```

Translation walk:

```
1. L1 PTE address = (satp.PPN << 12) + VPN[1] * 4
2. Read L1 PTE → extract L1 PPN
3. L0 PTE address = (L1_PPN << 12) + VPN[0] * 4
4. Read L0 PTE → extract PFN + permission bits
5. PA = (PFN << 12) | Offset
```

Each level costs one physical memory read. Without a TLB, a single load instruction causes **two** memory reads just to find out where to read.

## Permission Matrix

| Access Type | Required PTE bits |
|---|---|
| Instruction fetch | X = 1 |
| Data load | R = 1 |
| Data store | W = 1 |
| User-mode any | U = 1 |

If a required bit is 0, the MMU raises the corresponding page fault exception.

## The Dirty and Accessed Bits

The MMU sets the **A (Accessed)** bit whenever a page is read or written, and the **D (Dirty)** bit when written. The OS uses these to decide which pages to evict to swap — pages that have not been accessed recently are evicted first; dirty pages must be written to disk before the frame can be reused.

## Common Pitfall: Offset Is Never Translated

The low 12 bits of the virtual address are the **byte offset within the page**. They are copied verbatim into the physical address. Only bits above the offset go through the page-table lookup.

## Interview Answer

> "The MMU splits the virtual address into a virtual page number and a page offset. It uses the VPN to index into the page table (fetched from the satp register) to find the PTE, checks permissions, extracts the physical frame number, then concatenates PFN with the original offset to produce the physical address. The offset bits are never translated."
