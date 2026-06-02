# Metadata vs Data Journaling Modes

Linux's ext3 and ext4 filesystems support three journaling modes that differ in **what gets written to the journal**. Choosing the right mode involves a fundamental trade-off between write performance and data safety after a crash.

## The Three Modes

### 1. `writeback` — Metadata-Only, No Ordering

Only filesystem metadata (inodes, bitmaps, directory entries) is journaled. File **data** is written directly to its final disk location at any time — the journal does not enforce ordering between data and metadata writes.

```
Sequence (may interleave in any order):
  [Data block written to final location]
  [Journal: TxBegin, inode update, TxCommit]
  [Inode written to real location]
```

**Risk:** After a crash during an append, the inode may point to a newly allocated block that still contains stale data from a previous file (or zeros from a never-written block). An attacker who can time crashes may be able to read old data from another file through a new one.

**Performance:** Highest — no ordering constraints, data and metadata writes are fully parallel.

**Mount option:**
```bash
mount -o data=writeback /dev/sdb1 /mnt
```

### 2. `ordered` — Metadata-Only, Data Flushed First (Default)

Still only metadata is journaled. However, the kernel guarantees that **file data is written to its final disk location before the metadata transaction commits**. The sequence is:

```
Step 1: Write data blocks to their real disk locations
Step 2: Issue write barrier (flush) to drain drive queue
Step 3: Write metadata to journal (TxBegin, inode, bitmap, TxCommit)
Step 4: Issue write barrier
Step 5: Write metadata to real locations (checkpoint)
```

If the system crashes before step 3 commits: metadata journal is incomplete → rolled back → file appears as if it was never written. Data blocks may have landed on disk, but they are unreachable (bitmap marks them free). No stale data from other files is ever exposed.

**Risk:** None for data integrity. Only risk is metadata consistency, which the journal handles.

**Performance:** Moderate — data and metadata cannot be fully parallelized; write barriers add latency.

**Mount option (default):**
```bash
mount -o data=ordered /dev/sdb1 /mnt   # this is the default
```

### 3. `journal` — Full Data Journaling

Both file data **and** metadata are written to the journal before being checkpointed to their real locations. Every byte of file content passes through the journal.

```
Journal transaction:
  TxBegin
  Data block (copy of file content)
  Inode update
  Bitmap update
  TxCommit
        ↓ (later checkpoint)
  Data written to real location
  Metadata written to real location
```

**Risk:** Lowest — if a crash occurs, the entire transaction (data + metadata) is either replayed or rolled back atomically.

**Performance:** Worst — every write is written twice (journal + real location). For write-heavy workloads this can roughly halve write throughput.

**Mount option:**
```bash
mount -o data=journal /dev/sdb1 /mnt
```

## Side-by-Side Comparison

| Mode | Journals | Data ordering | Stale data risk | Write overhead |
|---|---|---|---|---|
| `writeback` | Metadata only | None | Yes (security concern) | Lowest |
| `ordered` | Metadata only | Data before metadata | No | Medium |
| `journal` | Data + Metadata | Atomic together | No | Highest (~2x writes) |

## When Each Mode Is Appropriate

**Use `ordered` (default) for** most workloads — databases that manage their own durability (Postgres, MySQL InnoDB) bypass the page cache anyway with `O_DIRECT`, so the journaling mode barely affects them.

**Use `journal` mode for** applications that rely entirely on the OS for durability and cannot tolerate stale data reads after crash recovery. This includes some NFS server configurations.

**Use `writeback` for** read-heavy or scratch workloads where performance matters and crash recovery that exposes stale data is acceptable (e.g., ephemeral build caches, tmp filesystems).

## Practical Example: Database on ext4

```bash
# PostgreSQL uses O_DIRECT + fsync for its own WAL — ordered mode is fine:
mount -o data=ordered /dev/nvme0n1p1 /var/lib/postgresql

# Verify current journal mode:
tune2fs -l /dev/nvme0n1p1 | grep "Default mount options"
# → Default mount options: user_xattr acl
# (empty means ordered, which is the compiled-in default)
```

## The "Torn Write" Subtlety

Even in `journal` mode, a **torn write** — where a single 4 KB page is only partially written before a crash — can corrupt the journal entry itself. Modern filesystems use a **checksum** on the commit block:

```
TxCommit block:
  checksum = crc32c(all blocks in this transaction)
```

On recovery, if the checksum does not match, the transaction is treated as incomplete and rolled back. ext4 with the `metadata_csum` feature enabled does exactly this.

**Interview answer:** In `ordered` mode (ext4 default), file data is flushed to disk before the journal commits its metadata, preventing stale data exposure after a crash but journaling only metadata. In `journal` mode, both data and metadata are journaled for the strongest guarantee at the cost of writing everything twice. In `writeback` mode only metadata is journaled with no ordering, giving highest performance but risking stale data reads after recovery.
