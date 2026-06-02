# Interview Drill: File System Internals

This lesson collects the highest-frequency interview questions on file system internals — journaling, caching, crash consistency, and durability. For each, a concise one-line answer is provided alongside the deeper explanation an interviewer expects.

## Q1: What is the page cache and why does it exist?

**One-line answer:** The page cache is kernel RAM that stores recently accessed file data so repeated reads are served from memory instead of disk.

**Depth to add:** It is transparent to applications — `read()` and `write()` go through it automatically. Writes land in the cache (dirty) and are flushed asynchronously by the kernel's write-back threads. The cache is evicted under memory pressure using an approximate LRU policy. It is why `free` output shows most RAM as "used" even on an otherwise idle system — that memory is productively caching disk data.

---

## Q2: What happens when you call `write()` on Linux?

**One-line answer:** The data is copied into a dirty page in the kernel's page cache; `write()` returns immediately without touching disk.

**Depth to add:** The actual disk write happens later, when the kernel's `writeback` thread flushes dirty pages (triggered by age or memory pressure). If you need the data on disk before returning, call `fsync(fd)` after `write()`. Without `fsync()`, data in the page cache is lost on a power failure or kernel panic.

---

## Q3: What is crash consistency and why is it hard?

**One-line answer:** Crash consistency means the filesystem remains valid after an abrupt power loss; it is hard because a logical operation requires multiple disk writes that cannot be made atomic.

**Depth to add:** For example, creating a file requires updating the inode, data bitmap, inode bitmap, and directory entry — five or more separate disk writes. Any crash mid-sequence leaves the filesystem in an inconsistent state. The problem is exacerbated by disk controller reordering (NCQ) and drive write-back caches.

---

## Q4: How does journaling solve crash consistency?

**One-line answer:** It writes intended changes to a small sequential log (journal) before applying them, so recovery can replay or discard the log rather than scanning the entire filesystem.

**Depth to add:** The journal uses a **commit block** — a single atomic sector write — as an all-or-nothing signal. If the commit is present, the transaction is replayed. If absent, the partial transaction is discarded. Recovery scans only the journal (megabytes, seconds) instead of the whole filesystem (terabytes, hours).

---

## Q5: What is the difference between ext4's `ordered` and `journal` modes?

**One-line answer:** `ordered` (default) journals only metadata and flushes file data before committing; `journal` mode writes both data and metadata to the journal for stronger guarantees at the cost of double writes.

**Depth to add:** In `ordered` mode a crash can cause a file to appear truncated (metadata rolled back) but never exposes stale data from other files. In `journal` mode every write is written twice — once to the journal, once to the real location — roughly halving write throughput for write-heavy workloads. Most databases use `ordered` mode and manage their own durability via `fsync()`.

---

## Q6: What does `fsync()` actually do?

**One-line answer:** It blocks until the file's dirty pages are flushed from the page cache **and** the drive's own write-back cache to non-volatile storage.

**Depth to add:** The drive is commanded to flush via a FLUSH CACHE ATA/SCSI command. Consumer drives sometimes acknowledge this command without actually flushing (to appear faster in benchmarks). `fdatasync()` is a cheaper variant that skips flushing metadata when only data has changed. Databases call `fsync()` on their WAL before acknowledging a committed transaction.

---

## Q7: How do copy-on-write filesystems achieve crash consistency without a journal?

**One-line answer:** They never overwrite live data — new versions are written to free space, and the root pointer is atomically redirected to the new tree.

**Depth to add:** A crash at any point leaves the old tree reachable and consistent. No replay is needed. As a bonus, old tree versions can be preserved as snapshots for free (just keep the old root pointer). Btrfs and ZFS use this approach; APFS does too.

---

## Q8: What is the difference between `mmap(MAP_SHARED)` and `mmap(MAP_PRIVATE)`?

**One-line answer:** `MAP_SHARED` writes are visible to other processes and written back to the file; `MAP_PRIVATE` uses copy-on-write so writes stay private and never touch the file.

**Depth to add:** Executables are loaded with `MAP_PRIVATE` — a process can modify its own BSS segment without affecting the on-disk binary. Shared memory IPC and database files use `MAP_SHARED`. Writes to `MAP_SHARED` mappings still need `msync()` for durability guarantees.

---

## Q9: Why is write-back faster than write-through?

**One-line answer:** Write-back acknowledges the write after updating memory (nanoseconds); write-through waits for the physical disk write (milliseconds).

**Depth to add:** Write-back also allows **coalescing** — if a block is written 10 times before the flush, only the final version goes to disk. Write-through is safer (acknowledged writes are on disk immediately) but throughput is bounded by disk speed. Most systems use write-back for the page cache and expose `fsync()` for applications that need write-through semantics.

---

## Q10: What is a write barrier in the context of filesystems?

**One-line answer:** A write barrier is a command that tells the storage device to flush all preceding writes to non-volatile media before accepting new writes, enforcing ordering.

**Depth to add:** Journaling filesystems issue a write barrier between writing journal data and writing the commit block, to guarantee the commit truly lands after the data. Without a barrier, the commit block could be written before the data it confirms, breaking the atomicity guarantee. In Linux, `fsync()` implicitly issues a barrier to the underlying block device.

---

## Common Pitfalls to Mention

- Calling `close()` is **not** the same as `fsync()` — close does not flush dirty pages.
- `sync()` is advisory on Linux and does not block for completion — use `fsync()` for reliability.
- Drives with volatile write caches can silently lose data even after `fsync()` if the drive lies about flushing. Enterprise drives with PLP capacitors are the safe choice for databases.
- CoW filesystems (Btrfs) can run out of space for new writes even when old blocks exist, because GC may not have reclaimed them yet — always leave headroom.
