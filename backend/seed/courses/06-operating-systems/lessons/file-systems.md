# File Systems: Files, Directories, and Inodes

A **file system** is the OS component that organizes data on persistent storage. It provides the abstraction of named, byte-addressable files arranged in a directory hierarchy — hiding the physical reality of sectors, tracks, blocks, and raw device addresses. A well-designed file system guarantees durability (data survives crashes), consistency (no half-written metadata), and performance (fast reads, writes, and directory lookups).

## The File Abstraction

A **file** is a named sequence of bytes. The OS provides a uniform set of operations regardless of the underlying storage technology:

| Operation | System Call | Description |
|-----------|-------------|-------------|
| Create | `open(path, O_CREAT\|O_WRONLY, 0644)` | Allocate inode + data blocks |
| Open | `open(path, O_RDONLY)` | Return a file descriptor |
| Read | `read(fd, buf, n)` | Copy n bytes from file → memory |
| Write | `write(fd, buf, n)` | Copy n bytes from memory → file |
| Seek | `lseek(fd, offset, SEEK_SET)` | Move the file position pointer |
| Sync | `fsync(fd)` | Flush dirty blocks to stable storage |
| Delete | `unlink(path)` | Remove directory entry; free blocks when link count reaches 0 |
| Stat | `stat(path, &buf)` | Query metadata (size, timestamps, permissions) |

Every operation on a file goes through the OS — there is no way to bypass the file system from user space.

## Directories

A **directory** is a special file that maps human-readable **names** to **inode numbers**. Directories contain a list of entries; each entry is simply `(name, inode_number)`.

```
/ (root, inode 2)
├── etc/        (inode 5)
│   └── passwd  (inode 47)
├── home/       (inode 8)
│   └── alice/  (inode 91)
│       └── notes.txt  (inode 204)
│       └── .bashrc    (inode 207)
└── bin/        (inode 12)
    └── ls      (inode 33)
```

**Path resolution** for `/home/alice/notes.txt`:
1. Start at inode 2 (root directory).
2. Read root's directory data: find entry `home` → inode 8.
3. Read inode 8 (directory): find entry `alice` → inode 91.
4. Read inode 91 (directory): find entry `notes.txt` → inode 204.
5. Read inode 204 (file) to access the actual data.

Each step requires a disk read if not cached. The **directory entry cache (dcache)** in Linux caches recent path resolution results in memory.

## Inodes (Index Nodes)

An **inode** is a fixed-size metadata structure on disk. On ext4, each inode is 256 bytes. Every file and directory has exactly one inode.

```
Inode 204:
  File type:    regular file (S_IFREG)
  Permissions:  -rw-r--r-- (0644)
  Owner UID:    1000 (alice)
  Owner GID:    1000 (alice)
  File size:    4,096 bytes
  Link count:   1
  atime:        2025-01-15 09:30:00   (last access)
  mtime:        2025-01-15 09:28:45   (last data modification)
  ctime:        2025-01-15 09:28:45   (last inode metadata change)
  Blocks used:  8 (512-byte sectors)
  Extent 0:     logical 0 → physical block 5021, length 1 block
```

Critical observation: **the inode does NOT contain the filename.** The filename lives only in the directory entry. This decoupling enables hard links.

### Block Pointers: Extents in Ext4

For large files, inodes must reference many disk blocks. Modern ext4 uses **extents** (contiguous block ranges) rather than individual block pointers:

```
Inode extent tree:
  Extent header: depth=0, num_entries=2
  Extent 0: logical blocks 0–63   → physical blocks 10240–10303   (256 KB)
  Extent 1: logical blocks 64–127 → physical blocks 20480–20543   (256 KB)
```

For very large files, the extent tree becomes multi-level (like a B-tree). Older ext2/ext3 used direct/indirect/double-indirect block pointers:

```
12 direct pointers          → 12 × 4KB = 48 KB max directly
1 indirect pointer          → 1 block of 1024 pointers → 4 MB
1 double-indirect pointer   → 1024 × 1024 pointers → 4 GB
1 triple-indirect pointer   → up to 4 TB
```

## Hard Links vs. Symbolic Links

| | Hard Link | Symbolic (Soft) Link |
|-|-----------|---------------------|
| Points to | Inode number directly | A string (the target path) |
| Survives deletion of original? | Yes (while link count > 0) | No (becomes a dangling symlink) |
| Cross-filesystem? | No (inode numbers are per-filesystem) | Yes |
| Can link to directories? | No (usually) | Yes |
| `stat()` returns | Original file's metadata | Symlink's own inode metadata |
| Storage | Just a directory entry (no extra inode) | Its own inode containing the path string |

```bash
# Create a hard link
ln notes.txt alias.txt
# Now both names point to inode 204; link count = 2
# Deleting either one decrements link count; blocks freed only when count = 0

# Create a symbolic link
ln -s /home/alice/notes.txt /tmp/notes-link
# /tmp/notes-link is its own inode; its data is the string "/home/alice/notes.txt"
```

## File System Layout on Disk (Ext4)

A disk partition formatted with ext4 is divided into **block groups**, each containing:

```
Block Group N:
  ┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
  │ Superblock*  │ Group desc.  │ Block bitmap │ Inode bitmap │ Inode table  │
  │ (copy/main)  │ table        │              │              │ (256B/inode) │
  └──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
  Then: data blocks (file content, directory entries)
```

- **Superblock:** global metadata (total blocks, free blocks, inode count, block size, magic number `0xEF53`).
- **Block bitmap:** one bit per block — 1 = allocated, 0 = free.
- **Inode bitmap:** one bit per inode — 1 = allocated, 0 = free.
- **Inode table:** array of fixed-size inode records for this group.

Placing inodes near their data blocks within the same group improves locality and reduces seek time.

## Journaling: Crash Consistency

Without journaling, a crash between two related writes (e.g., writing the inode update and the directory entry update) can leave the file system in an **inconsistent state** — a file with data blocks but no directory entry, or vice versa.

**Journaling** (also called write-ahead logging) solves this by writing a transaction log before modifying the actual file system structures:

```
Write operations for creating a file:
1. Write journal transaction: BEGIN
2. Journal: new inode, updated directory, updated bitmaps
3. Write journal: COMMIT
4. (replay is now safe — if crash, journal can be replayed)
5. Checkpoint: apply changes to actual file system structures
6. Mark journal transaction as complete
```

If the system crashes after step 3, the journal is replayed on next mount (fast recovery). If it crashes before step 3, the incomplete transaction is discarded.

Linux ext4 offers three journaling modes:
- `ordered` (default): data written to disk before metadata journaled — good balance.
- `writeback`: metadata journaled; data may be out of order — fastest but less safe.
- `journal`: both data and metadata journaled — slowest but most durable.

## The Virtual File System (VFS)

Linux's **VFS** is an abstraction layer that makes all file systems look identical to applications:

```
Application: open(), read(), write(), stat()
                 │
         ┌───────▼───────┐
         │  VFS Layer     │   (struct inode_operations, struct file_operations)
         └───────┬───────┘
        ╱    ╱   │   ╲    ╲
     ext4  xfs  btrfs  tmpfs  procfs  nfs  cifs ...
    (disk)(disk)(disk) (RAM) (kernel)(net) (net)
```

Each file system implements a set of VFS callbacks: `inode_operations->lookup()`, `file_operations->read()`, etc. When you call `read(fd, buf, n)`, the kernel calls `fd->file->f_op->read()` — which is ext4's implementation if the file is on an ext4 partition, or NFS's implementation if the file is on a network share.

This is why `cat /proc/cpuinfo` works: `/proc` is `procfs`, a pseudo-file-system that generates data on the fly from kernel data structures via VFS callbacks.

## Windows NTFS Highlights

NTFS (New Technology File System) uses a different on-disk structure:

- **Master File Table (MFT):** one row per file/directory. Everything — including small file data — can be stored directly in the MFT row (resident attribute). Large files have non-resident data attributes with extent lists.
- **$LogFile:** a circular journal for crash recovery (similar to ext4 journaling).
- **$Bitmap:** tracks free clusters.
- **$MFT mirror:** backup of the first 4 MFT entries for recovery.
- Supports: compression, encryption (EFS), hard links, symlinks, reparse points (used for junctions and symlinks), sparse files, alternate data streams.

## Key Takeaways

- A **file** is a named byte sequence; its metadata (permissions, size, block pointers) lives in an **inode**.
- A **directory** maps names to inode numbers — the name is only in the directory, not the inode.
- **Hard links** share an inode (same data); **symbolic links** store a path string and have their own inode.
- Ext4 organizes disk into **block groups** with superblock, bitmaps, inode table, and data blocks.
- **Journaling** (write-ahead logging) ensures crash consistency by logging intended changes before applying them.
- The **VFS** layer lets applications use any file system (ext4, NTFS, NFS, tmpfs, procfs) through a uniform interface.
- Inode number 2 is always the root directory on Unix file systems; NTFS uses the MFT instead of inodes.
