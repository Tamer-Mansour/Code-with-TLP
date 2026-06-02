# Copy-on-Write File Systems

**Copy-on-Write (CoW) filesystems** take a fundamentally different approach to crash consistency: instead of journaling changes to existing structures, they **never overwrite live data**. Every update writes new blocks to free space, and the filesystem's root pointer is atomically redirected to the new tree.

## The Core CoW Principle

Traditional filesystems (ext4, XFS) write data in-place: updating an inode means overwriting the old inode bytes on disk. CoW filesystems instead:

1. Write the new version of a block to a **free location** on disk.
2. Update the parent block (which references this block) — but again, write a new copy of the parent.
3. Continue up the tree until reaching the **superblock** or **root pointer**.
4. Atomically redirect the root pointer to the new tree version.

```
Before update:
  Root → [Dir Block A] → [Inode B] → [Data Block C]

Update Data Block C to C':
  Write C' to free space
  Write new Inode B' (pointing to C') to free space
  Write new Dir Block A' (pointing to B') to free space
  Atomically update Root → [Dir Block A'] → [Inode B'] → [Data Block C']

Old blocks (A, B, C) are now unreferenced → can be reclaimed
```

The atomic root pointer update is a **single sector write** — the same trick journaling uses for its commit block.

## Crash Safety Without a Journal

Because old blocks are never overwritten:
- A crash at any point leaves the old tree intact and reachable via the old root pointer.
- The new tree is only "live" after the atomic root update.
- No journal replay or `fsck` is needed — the old tree is always consistent.

```
Crash during write of new tree:
  Root still points to old (consistent) tree.
  New (partial) blocks are unreferenced → ignored or reclaimed by garbage collector.
  Recovery: instant, zero replay work.
```

## Snapshots: A Free Benefit

Because old block versions remain on disk until explicitly freed, CoW filesystems gain **snapshots** almost for free:

```
Before snapshot:
  Root (current) → tree version 5

Take snapshot:
  Snapshot root (frozen) → tree version 5   ← extra root pointer, no data copied
  Root (current) still → tree version 5

After write (new blocks written, root updated):
  Snapshot root (frozen) → version 5 tree still intact
  Root (current) → version 6 tree (shares unchanged blocks with version 5)
```

Unchanged blocks are shared between snapshot and current tree — no wasted space. Only written blocks diverge.

## Btrfs: Linux's CoW Filesystem

**Btrfs** (B-tree filesystem) is the primary CoW filesystem on Linux:

```bash
# Create a btrfs filesystem:
mkfs.btrfs /dev/sdb

# Take a snapshot (instant, nearly free):
btrfs subvolume snapshot /mnt/data /mnt/data-snap-2026-06-02

# List snapshots:
btrfs subvolume list /mnt

# Send/receive snapshots for incremental backups:
btrfs send /mnt/data-snap-2026-06-02 | ssh backup-server btrfs receive /backup/
```

Btrfs also supports RAID, compression, and online defragmentation.

## ZFS: The Gold Standard

**ZFS** (originally from Sun/Solaris, now via OpenZFS on Linux/FreeBSD) is the most mature CoW filesystem:

```bash
# Create a ZFS pool:
zpool create mypool /dev/sdb

# Snapshot in milliseconds:
zfs snapshot mypool@2026-06-02

# Roll back to a previous snapshot:
zfs rollback mypool@2026-06-02

# Incremental replication:
zfs send -i mypool@yesterday mypool@today | ssh remote zfs receive backup/mypool
```

ZFS features: **checksums on every block** (detects silent disk corruption), **RAID-Z** (software RAID), **transparent compression**, and **deduplication**.

## APFS: Apple's Modern Filesystem

**APFS** (Apple File System, 2017) replaced HFS+ on macOS/iOS/iPadOS with a full CoW design. It provides:
- Instant snapshots (used by Time Machine).
- Per-file encryption.
- Clones: instant file copies sharing blocks until diverged.
- Shared space pool across volumes.

## CoW Pitfalls

| Pitfall | Explanation |
|---|---|
| **Write amplification** | Small writes force copying entire tree path to free space, multiplying actual disk I/O. |
| **Fragmentation over time** | Data is always written to free locations, never in-place; sequential layout degrades. |
| **Free space management** | Old blocks must be tracked and reclaimed — adds GC complexity. |
| **Random write performance** | SSDs partially mitigate fragmentation, but CoW still struggles vs. in-place writes for sequential workloads. |

## CoW vs Journaling Comparison

| Property | Journaling (ext4) | CoW (Btrfs/ZFS) |
|---|---|---|
| Crash recovery | Replay journal | Instant (no replay) |
| Snapshots | Not native (needs LVM) | Native, near-free |
| Write amplification | Moderate (2x in journal mode) | Higher for small random writes |
| Fragmentation | Managed by allocator | Grows over time |
| Maturity | Very high (30+ years) | High (ZFS), Moderate (Btrfs) |

**Interview answer:** Copy-on-Write filesystems (Btrfs, ZFS, APFS) never overwrite live data — they write new versions to free space and atomically redirect the root pointer. This guarantees crash consistency without a journal, and enables instant snapshots by sharing unchanged blocks between old and new tree versions.
