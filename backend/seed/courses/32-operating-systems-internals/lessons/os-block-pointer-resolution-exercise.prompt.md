# Resolve a File Offset Through Direct and Indirect Blocks

## Background

Unix inodes (ext2/ext3 style) store block addresses in three tiers:

- **Direct pointers** (`num_direct` of them): each points directly to a data block.
- **Single-indirect pointer**: points to one *index block* that contains `ptrs_per_block` data-block addresses.
- **Double-indirect pointer**: points to an *outer index block* containing `ptrs_per_block` addresses of *inner index blocks*, each holding `ptrs_per_block` data-block addresses.

Block pointers are **4 bytes** each, so `ptrs_per_block = block_size / 4`.

## Task

Given the filesystem block size, the number of direct pointers, and a byte offset into a file, determine:

1. Which tier (`direct`, `single_indirect`, or `double_indirect`) contains the logical block that holds the byte.
2. The zero-based index of that logical block within its tier.
3. How many block reads are needed to reach the data (not counting reading the inode):
   - `direct` → 1 read.
   - `single_indirect` → 2 reads (index block + data block).
   - `double_indirect` → 3 reads (outer index + inner index + data block).

## Input Format

```
block_size num_direct
byte_offset
```

- Line 1: two integers separated by a space.
  - `block_size` (integer, power of 2, 512 ≤ block_size ≤ 65536)
  - `num_direct` (integer, 1 ≤ num_direct ≤ 15)
- Line 2: one non-negative integer `byte_offset`.
- The offset is guaranteed to fall within the direct, single-indirect, or double-indirect range.

## Output Format

```
<tier> <tier_index> <accesses>
```

One line, three fields separated by single spaces.

- `tier`: one of `direct`, `single_indirect`, `double_indirect` (no quotes).
- `tier_index`: zero-based index of the logical data block within the tier (integer).
- `accesses`: integer, 1, 2, or 3.

## Constraints

- All values fit in a 64-bit integer.
- No leading/trailing whitespace other than the final newline.

## Sample Input 1

```
4096 12
49152
```

## Sample Output 1

```
single_indirect 0 2
```

**Explanation:** logical block = 49152 / 4096 = 12. Direct covers [0, 11]. Block 12 is at index 0 in single-indirect tier. Reads needed: 2.

## Sample Input 2

```
4096 12
0
```

## Sample Output 2

```
direct 0 1
```

## Sample Input 3

```
4096 12
4243456
```

## Sample Output 3

```
double_indirect 0 3
```

**Explanation:** logical block = 4243456 / 4096 = 1036. ptrs_per_block = 1024. Direct covers [0,11], single-indirect covers [12, 1035], double-indirect starts at 1036. Tier index = 1036 - 12 - 1024 = 0.
