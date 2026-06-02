# Exercise: Resolve a File Offset Through Direct and Indirect Blocks

Unix-style filesystems (ext2/ext3) store block pointers in three tiers inside the inode:

1. **Direct pointers** — point straight to data blocks (fast, but limited in count).
2. **Single-indirect pointer** — points to an *index block* full of data-block addresses.
3. **Double-indirect pointer** — points to an index block of index blocks.

Given a byte offset inside a file, a systems engineer must know which tier serves that offset and how many block reads are required to reach the data.

## What You Will Implement

Write a program that reads a filesystem configuration and a byte offset, then prints:

- Which allocation tier holds that byte (`direct`, `single_indirect`, or `double_indirect`).
- The zero-based index of the data block within that tier.
- The number of sequential block reads needed to reach the data block (not counting the inode itself):
  - Direct → **1** read (the data block itself).
  - Single-indirect → **2** reads (index block + data block).
  - Double-indirect → **3** reads (outer index block + inner index block + data block).

Assume block pointers are **4 bytes** each (so `ptrs_per_block = block_size / 4`).

## Input Format

```
block_size num_direct
byte_offset
```

- `block_size` — size of one block in bytes (power of 2, between 512 and 65536).
- `num_direct` — number of direct block pointers in the inode (1–15).
- `byte_offset` — non-negative byte offset into the file.
- The offset will always fall within the direct, single-indirect, or double-indirect range.

## Output Format

```
<tier> <tier_index> <accesses>
```

All on one line, space-separated.

## Sample Input

```
4096 12
49152
```

## Sample Output

```
single_indirect 0 2
```

**Explanation:** block_size=4096, ptrs_per_block=1024, num_direct=12.
Logical block number = 49152 / 4096 = 12.
Direct range: blocks 0–11 (12 blocks).
Single-indirect range: blocks 12–1035 (1024 blocks).
Block 12 is at index 0 within the single-indirect tier → 2 reads.
