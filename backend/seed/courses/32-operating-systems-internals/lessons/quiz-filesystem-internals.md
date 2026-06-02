# Quiz: File System Internals: Journaling, Caching, and Consistency

**Q1. A process calls `write(fd, data, 4096)` and it returns successfully. Which statement is TRUE?**
- [ ] The data is guaranteed to be on non-volatile storage.
- [x] The data is in the kernel's page cache but may not yet be on disk.
- [ ] The data has been written to the disk controller cache but not the OS cache.
- [ ] The call would have blocked until the data reached the disk.

_`write()` copies data into the page cache and returns immediately. The kernel flushes dirty pages to disk asynchronously. `fsync()` is required for durability._

---

**Q2. What is the purpose of the `TxCommit` block in a journaling filesystem?**
- [ ] It holds a copy of all file data written in the transaction.
- [ ] It marks the journal as full and triggers a checkpoint.
- [x] It serves as an atomic, all-or-nothing signal that the transaction is complete and can be replayed.
- [ ] It stores the checksum of the superblock.

_Recovery logic looks for a complete TxBegin...TxCommit pair. A missing commit means the transaction is discarded. The commit block is written last, as a single sector write that is effectively atomic._

---

**Q3. Which ext4 journaling mode provides the STRONGEST crash safety guarantee?**
- [ ] `writeback` — metadata journaled, no ordering
- [ ] `ordered` — data flushed before metadata commits
- [x] `journal` — both data and metadata written to journal
- [ ] `nosync` — no journal, fastest mode

_`journal` mode writes both file data and metadata into the journal before checkpointing, ensuring the entire write is either fully applied or fully rolled back after a crash, at the cost of roughly double the disk writes._

---

**Q4. A copy-on-write filesystem like Btrfs or ZFS achieves crash consistency primarily by:**
- [ ] Running fsck in the background after every write
- [ ] Journaling all metadata changes to a dedicated log area
- [ ] Using a RAID array to mirror all writes
- [x] Never overwriting live data — writing new blocks to free space and atomically updating the root pointer

_The old tree is always consistent and reachable. A crash before the atomic root pointer update leaves the old tree intact. No journal replay is needed._

---

**Q5. What does `msync(addr, length, MS_SYNC)` do for a `MAP_SHARED` mapping?**
- [ ] Releases the virtual address range back to the OS
- [ ] Invalidates the mapped pages so they are re-read from disk on next access
- [x] Flushes dirty pages in the mapped region to the underlying file on disk, blocking until complete
- [ ] Converts the mapping from MAP_SHARED to MAP_PRIVATE

_`msync()` with `MS_SYNC` is the mmap equivalent of `fsync()`. Without it, writes to a shared mapping may be lost on a crash because the kernel flushes dirty pages asynchronously._

---

**Q6. An SSD consumer drive acknowledges an `fsync()` call immediately without actually flushing its write cache. What is the practical consequence?**
- [ ] The filesystem will switch to write-through mode automatically.
- [ ] The OS will detect the lie and retry the flush.
- [ ] No consequence — the drive's write cache is non-volatile anyway.
- [x] Data acknowledged as durable may be lost on a sudden power loss, silently corrupting the database or journal.

_Some consumer drives lie about flushing to improve benchmark scores. Enterprise drives with power-loss protection (PLP) capacitors are honest and safe. Databases relying on `fsync()` for WAL durability are at risk on such drives._
