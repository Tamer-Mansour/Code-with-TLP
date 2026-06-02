# Directory Structures and Lookups

A directory maps human-readable names to inode numbers. The internal structure of a directory — how it stores and searches those mappings — determines lookup performance and has evolved significantly across filesystem generations.

## The Directory as a File

From the VFS perspective a directory is just a file with a special type flag (`S_IFDIR`). Its byte content is a sequence of **directory entries** (dirents). You can read it through `getdents()` or the POSIX `readdir()` API:

```c
DIR *d = opendir("/etc");
struct dirent *e;
while ((e = readdir(d)) != NULL)
    printf("inode=%lu  name=%s\n", (unsigned long)e->d_ino, e->d_name);
closedir(d);
```

## Linear List (ext2 original)

The simplest format is a flat linked list of variable-length records:

```
[ inode | rec_len | name_len | name... | padding ]
[ inode | rec_len | name_len | name... | padding ]
...
```

- **Lookup:** O(n) — scan from the start until the name matches.
- **Create/Delete:** amortised fast; deletion marks a record free by merging it into the previous entry's `rec_len`.
- **Pitfall:** large directories (thousands of entries) suffer O(n) lookup, which is measurable on workloads with many small files.

## Hash Table (ext3/ext4 htree)

ext3 introduced an optional **HTree** (a B-tree of hash buckets) enabled by the `dir_index` feature flag:

```
Root block
├── hash_version = half-MD4
├── entries sorted by hash(name)
└── leaf blocks → linear lists within each bucket
```

Lookup is O(log n) for the tree traversal plus O(k) for collision resolution within a bucket. For a directory with 100 000 files this reduces lookup from ~50 000 disk reads to ~3.

## B-Tree Directories (XFS, HFS+, btrfs)

XFS stores large directories entirely as B+ trees, keyed by filename hash. HFS+ uses a separate B-tree file for the entire volume catalog. Benefits:

- Guaranteed O(log n) lookup, insert, and delete regardless of directory size.
- Better support for concurrent access (lock a subtree, not the whole directory).

## Comparison Table

| Format | Lookup | Insert | Delete | Used by |
|--------|--------|--------|--------|---------|
| Linear list | O(n) | O(1) amortised | O(1) | ext2 (small dirs) |
| Hash table | O(1) avg | O(1) avg | O(1) | ext3/ext4 htree |
| B-tree | O(log n) | O(log n) | O(log n) | XFS, HFS+, btrfs |

## Worked Example: Linear Scan

Suppose a directory block contains three entries:

```
Offset 0:  inode=42, rec_len=16, name="."
Offset 16: inode=17, rec_len=20, name=".."
Offset 36: inode=88, rec_len=28, name="report.txt"
```

To look up `"report.txt"`:
1. Read entry at offset 0 — name is `"."`, skip.
2. Read entry at offset 16 — name is `".."`, skip.
3. Read entry at offset 36 — name matches → return inode 88.

With htree the hash of `"report.txt"` is computed first, then only one leaf block is read.

## The `..` Entry and the Root Special Case

Every directory has `"."` and `".."` entries. The root directory's `".."` points back to inode 2 (the root inode itself). This creates the invariant: you can always walk up to the root without a special case in `namei`.

## Common Pitfalls

- **Forgetting that rmdir requires empty directories.** The kernel checks that only `"."` and `".."` remain before removing the entry. Use `rm -r` to recurse.
- **Directory rename atomicity.** `rename("a", "b")` is atomic on POSIX — the old name disappears and the new one appears without any intermediate state visible to other processes.
- **Maximum filename length.** POSIX mandates 255 bytes; the filesystem encoding (UTF-8 vs. Latin-1) matters because the limit is in bytes, not characters.

> **Interview answer:** "A directory stores name-to-inode mappings; early filesystems used a linear list giving O(n) lookup, while modern filesystems (ext4 htree, XFS B-tree) achieve O(log n) or O(1) average lookup — critical for directories with thousands of entries."
