# Journaling File Systems

**Journaling** solves the crash consistency problem by recording intended changes in a dedicated log (the **journal**) before applying them to the main filesystem structures. After a crash, recovery replays or discards the journal — no full filesystem scan needed.

## The Core Idea: Write-Ahead Logging

The principle is borrowed from database WAL (Write-Ahead Logging):

> "Before modifying any persistent structure, write what you intend to do to the journal. Only after the journal entry is safely on disk, apply the changes."

```
Journal write:
  [TxBegin | inode_update | bitmap_update | data_block | TxCommit]
                              ↓
Main filesystem update (after journal committed):
  Write inode to its real location
  Write bitmap to its real location
  Write data to its real location
                              ↓
Journal entry marked as free (checkpoint)
```

If the system crashes **before** `TxCommit` reaches disk: recovery ignores the incomplete transaction (as if it never happened).

If the system crashes **after** `TxCommit`: recovery replays all writes listed in the transaction. The real filesystem may be partially updated, but replaying is **idempotent** — writing the same block twice with the same data is harmless.

## Anatomy of a Journal Transaction

```
┌──────────────┐
│  TxBegin     │  ← Marks start, includes transaction ID
│  Block #42   │  ← Full copy of data/metadata block
│  Block #7    │
│  Block #1    │
│  TxCommit    │  ← Only written after all blocks above are on disk
└──────────────┘
```

The **journal** is a circular log area, typically a few dozen to a few hundred megabytes, allocated at filesystem creation time (e.g., `/dev/sda1` has `journal` as a hidden inode in ext3/ext4).

## Recovery Protocol

```
On mount after unclean shutdown:
  1. Scan journal for complete transactions (TxBegin ... TxCommit pairs)
  2. For each complete transaction:
       replay all blocks to their real filesystem locations
  3. For any incomplete transaction (missing TxCommit):
       discard it — it never committed
  4. Mark journal clean → mount complete
```

Recovery only reads and replays the journal, which is tiny compared to the whole filesystem. Recovery time is **seconds**, not hours.

## ext3 and ext4: Journaling in Practice

Both ext3 and ext4 are journaling filesystems. ext4 adds extents, larger block counts, and delayed allocation but uses the same journaling infrastructure (`jbd2` — Journaling Block Device 2).

```bash
# Create an ext4 filesystem with explicit journal size:
mkfs.ext4 -J size=128 /dev/sdb1    # 128 MB journal

# Show journal info:
tune2fs -l /dev/sdb1 | grep -i journal

# Replay journal and mount (automatic on normal mount):
mount /dev/sdb1 /mnt/data
```

## Atomicity via the Commit Block

The critical insight is the **commit block**: it is written **last**, as a single sector write. On most disks, a single 512-byte sector write is atomic (either it lands or it doesn't). Recovery uses its presence or absence as an all-or-nothing signal for the whole transaction.

```
Writes to disk (in order, each flushed before the next):
  1. All data/metadata blocks in journal   ← flush (write barrier)
  2. TxCommit block                        ← atomic sector write
```

The write barrier between steps 1 and 2 ensures step 1 is truly on disk before the commit is visible.

## Performance Implications

Journaling imposes overhead:

- **Extra writes** — every block may be written twice (once to journal, once to real location).
- **Write barriers** — serialize I/O, hurting throughput on rotational disks.
- **Journal contention** — all writes funnel through the same journal area (hot spot on disk).

To mitigate, ext3/ext4 **batch** multiple filesystem operations into a single journal transaction, amortizing overhead across many writes.

## Journaling Modes (Overview)

ext3/ext4 support three modes — covered in depth in the next lesson:

| Mode | What is journaled | Overhead | Safety |
|---|---|---|---|
| `writeback` | Metadata only (unordered) | Lowest | Metadata consistent; file content may be stale |
| `ordered` | Metadata only (data flushed first) | Medium | Safe against content corruption |
| `journal` | Data + metadata | Highest | Strongest guarantee |

## Other Journaling Filesystems

- **XFS** — used in RHEL; journals only metadata, uses delayed allocation. High performance for large files.
- **NTFS** — Windows's journaling filesystem (`$LogFile`).
- **HFS+** — macOS journaling filesystem (replaced by APFS which uses CoW).
- **JFS** — IBM's journaling filesystem, still in use on AIX.

**Interview answer:** A journaling filesystem writes all pending changes to a sequential log (journal) before applying them. After a crash, the OS scans the small journal — replaying committed transactions and discarding incomplete ones — instead of scanning the entire filesystem, reducing recovery time from hours to seconds.
