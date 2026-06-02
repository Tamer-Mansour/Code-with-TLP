# The Crash Consistency Problem

A filesystem must remain in a **consistent state** after a crash — no orphaned data, no half-written metadata, no dangling pointers. Achieving this is surprisingly hard because a single logical operation (e.g., appending to a file) involves multiple independent disk writes that cannot be made atomic by hardware.

## What "Consistent" Means

A filesystem is consistent when:

- Every allocated block is reachable from exactly one inode.
- Every free block is listed as free in the bitmap/free list.
- The inode's link count matches the number of directory entries pointing to it.
- No block is simultaneously marked "allocated" and "free".

Inconsistency arises when a crash interrupts a sequence of writes mid-way.

## A Concrete Example: Creating a File

To create `/home/alice/notes.txt` on ext2, the filesystem must:

1. **Write the data block** — the file content.
2. **Update the inode** — record the file size, block pointer, timestamps.
3. **Update the inode bitmap** — mark the inode as allocated.
4. **Update the data bitmap** — mark the data block as allocated.
5. **Write the directory entry** — link the filename to the inode number.

Each of these is a separate disk write. They can land in any order and the system can crash after any subset.

```
Logical operation: "create file with content"

Physical writes needed:
  W1: data block  (content: "hello world")
  W2: inode       (size=11, block_ptr=42, ...)
  W3: inode bitmap (inode 17 → allocated)
  W4: data bitmap  (block 42 → allocated)
  W5: directory entry ("notes.txt" → inode 17)

Crash after W1+W2 but before W3, W4, W5:
  → inode has a valid block pointer
  → but bitmaps say both are free → INCONSISTENCY
  → fsck will see block 42 used but bitmap says free
```

## Crash Scenarios Matrix

| Writes completed before crash | Outcome |
|---|---|
| None | Fine — file never exists |
| Data only | Block allocated on disk but no inode → lost block (leak) |
| Inode only | Inode points to garbage → file corruption |
| Data + Inode, no bitmaps | fsck detects used blocks not in bitmap → fixable but slow |
| Data + Inode + Bitmaps, no dir entry | Inode allocated, no name → orphaned inode |
| All except dir entry | Same as above — recovered by fsck as lost+found |
| All | Fully consistent |

## The Role of `fsck`

`fsck` (filesystem check) is a scan-and-repair tool that runs after an unclean shutdown:

```bash
fsck /dev/sdb1      # Check and optionally repair
fsck -y /dev/sdb1   # Auto-fix all issues
```

It scans **all** inodes and blocks, rebuilds bitmaps from scratch, and resolves inconsistencies. The fatal downside: `fsck` runtime is **proportional to filesystem size** — on a multi-terabyte filesystem it can take hours. This is unacceptable for servers needing fast recovery.

## The Ordering Problem

Even if an OS carefully orders writes (data before metadata), it cannot guarantee that order at the disk level. The disk controller reorders requests for performance (NCQ — Native Command Queuing), and the drive's on-board write-back cache may flush in any order.

```
OS issues writes in order: W1, W2, W3
Disk controller reorders: W3, W1, W2   ← crash between W3 and W1
→ Metadata written before data: corruption
```

To enforce ordering, the OS must issue a **write barrier** (flush command) between dependent writes. This is expensive — it drains the drive's queue and cache.

## Why Soft Updates Are Hard

One historical approach (**soft updates**, used in BSD's FFS) carefully tracks dependencies between writes and reorders them so that on-disk structures are always "safe" after a crash (possibly with leaked space, but never dangling pointers). The complexity of the dependency graph made soft updates extremely difficult to implement correctly.

## The Solution Space

Three major approaches solve crash consistency without full `fsck` scans:

| Approach | Mechanism | Recovery time |
|---|---|---|
| `fsck` | Scan entire filesystem | O(disk size) — slow |
| Journaling | Log pending operations | O(journal size) — fast |
| Copy-on-Write | Never overwrite; new tree atomically committed | O(1) — instant |

**Interview answer:** The crash consistency problem arises because a single logical filesystem operation (create, delete, append) requires multiple disk writes that cannot be made atomic — a crash mid-sequence leaves the filesystem in an inconsistent state with dangling pointers, leaked blocks, or corrupted metadata. Solutions include journaling (logging operations before applying them) and copy-on-write (never overwriting live data).
