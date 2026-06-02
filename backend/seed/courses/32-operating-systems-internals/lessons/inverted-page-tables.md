# Inverted and Hashed Page Tables

Standard page tables are indexed by virtual page number and grow with the size of the virtual address space. For 64-bit systems with huge virtual spaces, this is impractical even with multiple levels. **Inverted** and **hashed** page tables flip the indexing strategy: they are sized by the number of physical frames, not by the virtual address space.

## Inverted Page Table

An inverted page table has exactly **one entry per physical frame** in RAM. Each entry stores which (process, VPN) pair currently occupies that frame.

```
Inverted page table (indexed by physical frame number):
+-------+--------+---------+
| Frame | PID    | VPN     |
+-------+--------+---------+
|   0   | proc 3 | page 7  |
|   1   | proc 1 | page 0  |
|   2   | proc 2 | page 12 |
|  ...  |  ...   |  ...    |
+-------+--------+---------+
```

**Translation procedure:**

1. Given (PID, VPN), search the entire table for a matching entry.
2. The index of the matching entry is the physical frame number.
3. Physical address = `(frame_index << offset_bits) | offset`.

**Advantages:**
- Table size is proportional to physical RAM, not virtual address space — much smaller on 64-bit systems.
- One system-wide table instead of one per process.

**Disadvantages:**
- Linear search is O(n) where n = number of frames — unacceptably slow in hardware.
- Shared memory is complex: one frame may be mapped by multiple processes, requiring extra data structures.

**Used by:** IBM PowerPC, early IA-64 designs.

## Hashed Inverted Page Table

To fix the search performance problem, the inverted table is accessed via a hash function:

```
hash_index = hash(PID, VPN) % num_frames
```

Each hash bucket holds a chain of entries to handle collisions:

```c
struct ipt_entry {
    uint32_t pid;
    uint32_t vpn;
    uint32_t pfn;
    struct ipt_entry *next;  // collision chain
};

struct ipt_entry *hash_table[NUM_FRAMES];

uint32_t translate(uint32_t pid, uint32_t vpn, uint32_t offset) {
    uint32_t h = hash(pid, vpn) % NUM_FRAMES;
    struct ipt_entry *e = hash_table[h];
    while (e) {
        if (e->pid == pid && e->vpn == vpn)
            return (e->pfn << OFFSET_BITS) | offset;
        e = e->next;
    }
    page_fault();
}
```

With a good hash function and load factor near 1, the average lookup is O(1).

## Comparison with Conventional Tables

| Property | Forward (multi-level) | Inverted (hashed) |
|----------|-----------------------|-------------------|
| Size scales with | Virtual address space | Physical RAM |
| Lookup speed | O(levels) — fast | O(1) average — fast |
| Hardware walk support | Yes (x86, ARM) | Rarely (software TLB) |
| Shared memory | Easy (separate PTEs) | Needs extra bookkeeping |
| Common on | x86-64, AArch64 | PowerPC, MIPS, SPARC |

## TLB Interaction

Both designs rely heavily on the TLB to avoid per-access table walks. The key difference is what happens on a TLB miss:

- **Forward table**: Hardware walker reads the multi-level tree directly from memory.
- **Inverted/hashed table**: The OS handles the TLB miss in software (software-managed TLB), performing the hash lookup and loading the TLB entry.

Software-TLB systems trade hardware complexity for OS flexibility; they are common in RISC architectures.

## Common Pitfalls

- Confusing the inverted table entry index (= PFN) with the VPN — it is physically indexed, not virtually.
- Forgetting that an inverted table alone cannot express shared pages; supplementary data structures are needed.
- Assuming inverted tables are faster — they are not; the hash lookup plus chain traversal is comparable to a 4-level walk, with similar TLB miss penalties.

> **Interview answer:** An inverted page table has one entry per physical frame (indexed by frame number) storing which process and VPN map to it. This keeps table size proportional to physical RAM rather than virtual address space. A hash on (PID, VPN) enables O(1) lookups, but shared memory requires extra bookkeeping and hardware walk support is rare.
