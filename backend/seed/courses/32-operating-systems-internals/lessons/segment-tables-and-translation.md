# Segment Tables and Segmented Address Translation

Every process that runs under a segmented memory manager has its own **segment table** — an array of descriptors that tell the CPU where each logical segment lives in physical memory, how large it is, and what operations are permitted on it.

## Segment Table Structure

Each row in a segment table is called a **Segment Descriptor** (or Segment Table Entry, STE). A minimal descriptor contains:

| Field | Width | Purpose |
|---|---|---|
| Base | 32 or 64 bits | Starting physical address of the segment |
| Limit | 20–32 bits | Length in bytes (or pages, in some architectures) |
| Valid bit | 1 bit | Whether the entry is present in physical memory |
| Protection | 3 bits | Read / Write / Execute permissions |

In x86 Protected Mode (32-bit), the Global Descriptor Table (GDT) and Local Descriptor Table (LDT) serve as segment tables. Each descriptor is 8 bytes and packs base, limit, and flags into a compact bit-field layout.

```
63      56 55 52 51  48 47   40 39     16 15       0
+----------+----+------+--------+---------+-----------+
| Base 31:24 | G DL 0 AVL | Limit 19:16 | Access byte | Base 23:0 | Limit 15:0 |
+----------+----+------+--------+---------+-----------+
```

The `G` (Granularity) bit determines whether Limit is in bytes or 4 KB pages.

## Address Translation Steps

When the CPU executes a memory access under segmentation, hardware performs these steps:

1. **Extract the segment selector** from a segment register (`CS`, `DS`, `SS`, `ES`, `FS`, `GS`). The selector encodes the table index and a privilege level (RPL).
2. **Index into the descriptor table** (GDT or LDT) to fetch the descriptor.
3. **Check the Valid bit** — if 0, raise a General Protection Fault.
4. **Compare offset vs. limit** — if `offset > limit`, raise a Segmentation Fault.
5. **Check protection bits** — if the operation (read/write/execute) is not permitted, raise a fault.
6. **Compute physical address**: `physical = base + offset`.

```
Logical address:   [ seg selector | offset ]
                         |              |
                   Descriptor table    |
                         |             |
                     [ base | limit ]  |
                         |             |
                   base + offset ------+---> Physical address
```

## The Segment Register and Selector

In x86, segment registers do not hold the base directly — they hold a 16-bit **selector**:

```
15          3  2  1 0
+------------+--+--+
| Table Index | TI | RPL |
+------------+--+--+
```

- **TI** (Table Indicator): 0 = GDT, 1 = LDT
- **RPL** (Requested Privilege Level): 0 = kernel, 3 = user

The CPU uses `Table_Index × 8` as a byte offset into the GDT/LDT to find the descriptor.

## Worked Translation Example

Assume a flat GDT with two user-space descriptors:

| Index | Base | Limit | Perms |
|---|---|---|---|
| 1 (code) | 0x08048000 | 0x4FFF | R-X |
| 2 (data) | 0x0804D000 | 0x1FFF | RW- |

The CPU is executing a `mov` instruction. `DS = 0x10` (selector 2, TI=0, RPL=0).

Logical address: `<DS, 0x100>` → `<2, 0x100>`

```
offset 0x100 <= limit 0x1FFF  ✓
physical = 0x0804D000 + 0x100 = 0x0804D100
```

Now suppose the program tries to execute code through DS:

```
offset 0x100 <= limit 0x1FFF  ✓
but Execute bit is not set on descriptor 2  → General Protection Fault
```

## STBR and STLR: OS-Level Registers

The OS keeps track of each process's segment table using two CPU registers (analogous to PTBR/PTLR in paging):

- **STBR** (Segment Table Base Register) — physical address of the table
- **STLR** (Segment Table Length Register) — number of valid entries

On a context switch, the OS saves the old process's STBR/STLR to its PCB and loads the new process's values. From that moment, every memory access uses the new segment table transparently.

## Common Pitfalls

- Confusing the **selector** (what the register holds) with the **base** (what the descriptor contains).
- Forgetting the privilege check (RPL vs. DPL) — user code cannot load a kernel-privilege descriptor.
- Assuming the descriptor limit is always in bytes — the Granularity bit can make it a page count.

**Interview answer:** A segment table stores a (base, limit, permissions) descriptor for each logical segment. Hardware translation extracts the segment number from a selector register, looks up the descriptor, validates the offset against the limit, checks permission bits, and adds base + offset to produce the physical address.
