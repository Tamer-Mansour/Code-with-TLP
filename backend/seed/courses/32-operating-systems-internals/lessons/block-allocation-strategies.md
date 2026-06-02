# Block Allocation: Contiguous, Linked, and Indexed

Disk (or SSD) storage is divided into fixed-size **blocks** (commonly 4 KiB). The file system must decide how to assign blocks to files. The three classical strategies each make different tradeoffs between simplicity, random access speed, and external fragmentation.

## 1. Contiguous Allocation

All blocks of a file occupy a consecutive run on disk. The inode stores only a **start block** and a **length**.

```
Block map:
 0  1  2  3  4  5  6  7  8  9
[A][A][A][B][B][B][B][ ][ ][ ]
File A: start=0, len=3
File B: start=3, len=4
```

**Pros:**
- Fastest sequential and random access (seek once, read linearly).
- Simple: two numbers per file.

**Cons:**
- **External fragmentation** — free space becomes scattered holes over time.
- Growing a file often requires copying it to a new location.
- Must know file size at creation (impractical for most use-cases).

**Real-world use:** CD-ROM/ISO 9660 (files never grow), some tape formats.

## 2. Linked Allocation (FAT)

Each block contains a **pointer to the next block**, forming a singly linked list. The inode stores only the first block number.

```
Block 2 → block 7 → block 9 → NULL   (file C)
```

FAT (File Allocation Table) centralises these pointers in a table at the beginning of the volume:

| Block | Next |
|-------|------|
| 2     | 7    |
| 7     | 9    |
| 9     | EOF  |

**Pros:**
- No external fragmentation; any free block can extend the file.
- Files can grow/shrink easily.

**Cons:**
- **Sequential access only is efficient.** Seeking to byte N requires traversing N/block_size pointers.
- FAT table must fit in memory for performance; fails for large volumes.
- Reliability: one bad link corrupts the rest of the chain.

**Real-world use:** FAT32, exFAT (USB drives, SD cards).

## 3. Indexed Allocation (inode with block pointers)

A dedicated **index block** (or inode) holds an array of block pointers. No pointer overhead inside data blocks.

```
Inode:
  direct[0] = 12
  direct[1] = 45
  direct[2] = 67
  single_indirect = 200   ← block 200 holds more pointers
```

**Pros:**
- Direct random access: to read byte N, compute block index = N / block_size, fetch pointer, read block — three I/Os maximum.
- No internal chaining in data blocks.

**Cons:**
- Small files waste space if the index block is large.
- Very large files need multi-level indirection (double/triple indirect).

## Comparing the Three

| Property | Contiguous | Linked (FAT) | Indexed (inode) |
|----------|-----------|-------------|-----------------|
| Random access | O(1) | O(n) | O(1) (with levels) |
| Sequential access | Excellent | Good | Good |
| External fragmentation | High | None | None |
| Internal fragmentation | None | Minor | Minor |
| File growth | Hard | Easy | Easy |
| Real-world FS | CD-ROM | FAT32/exFAT | ext4, NTFS, HFS+ |

## Modern Extension: Extents

ext4 and NTFS replace raw block pointer arrays with **extents** — `(start_block, length)` pairs. A single extent describes a contiguous run, reducing metadata for large sequential files:

```c
// ext4 extent structure (simplified)
struct ext4_extent {
    uint32_t ee_block;   // first logical block
    uint16_t ee_len;     // number of blocks in run
    uint32_t ee_start;   // first physical block
};
```

A 1 GB file that happens to be contiguous needs only one extent, not 256 K block pointers.

## Common Pitfalls

- **Confusing FAT with full linked allocation.** FAT centralises the link table rather than storing next-pointers inside data blocks — random access is better but still O(n) without caching.
- **Block size vs cluster size.** FAT uses "clusters" (multiple sectors); internal fragmentation grows with cluster size. ext4 uses blocks; typical default is 4 KiB.
- **Sparse files.** Indexed allocation allows "holes": a block pointer of 0 means the range reads as zeros with no disk allocation. `ls -s` vs `ls -l` will differ for sparse files.

> **Interview answer:** "Contiguous allocation is fastest but fragments space; linked allocation avoids fragmentation but makes random access O(n); indexed allocation (inodes) gives O(1) random access with multi-level indirection for large files — the scheme used by virtually all production filesystems."
