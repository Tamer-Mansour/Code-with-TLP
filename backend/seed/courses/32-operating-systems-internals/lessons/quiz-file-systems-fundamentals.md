# Quiz: File Systems Fundamentals

**Q1. What does a Unix inode store?**
- [ ] The filename and the file's data blocks
- [ ] Only the file's data; names are in the superblock
- [x] Metadata (permissions, size, timestamps) and block pointers, but NOT the filename
- [ ] The filename and a pointer to the directory that contains it

_Explanation: Filenames live in directory entries. The inode holds everything else about a file — owner, permissions, size, timestamps, and pointers to data blocks._

---

**Q2. A filesystem has block_size=4096 bytes and 12 direct block pointers per inode. Each block pointer is 4 bytes. What is the maximum file offset reachable through the single-indirect pointer?**
- [ ] 48 KiB (12 direct blocks only)
- [ ] 4 MiB
- [x] Approximately 4 MiB above the direct range (12 + 1024 blocks total)
- [ ] 4 GiB

_Explanation: ptrs_per_block = 4096/4 = 1024. Single-indirect adds 1024 blocks of 4 KiB = 4 MiB. Combined with 12 direct blocks (48 KiB), the single-indirect tier ends at block 1035._

---

**Q3. Two processes both open the same file independently (separate open() calls). Process A reads 100 bytes. What is Process B's file offset?**
- [x] Still 0 — they have separate open-file table entries with independent positions
- [ ] 100 — they share the same open-file table entry
- [ ] Undefined — the OS does not guarantee any particular offset
- [ ] 50 — the offset is split equally

_Explanation: Each independent open() creates a separate entry in the system open-file table with its own f_pos. Only fork() causes parent and child to share an entry._

---

**Q4. Which of the following is a key advantage of symbolic links over hard links?**
- [ ] Symbolic links cannot become dangling
- [ ] Symbolic links share the target's inode, saving disk space
- [x] Symbolic links can cross filesystem boundaries and point to directories
- [ ] Symbolic links are faster to resolve because they bypass namei

_Explanation: Hard links are restricted to the same filesystem (inode numbers are per-filesystem) and usually cannot link directories. Symbolic links have none of these restrictions but can become dangling if the target is removed._

---

**Q5. What is the primary role of the VFS dentry cache (dcache)?**
- [ ] To cache the raw data bytes of recently accessed files
- [ ] To buffer disk writes and flush them in the background
- [x] To cache name-to-inode mappings so repeated path lookups avoid disk reads
- [ ] To track which processes have a given file open

_Explanation: The dcache stores (parent_dentry, name) → inode mappings in memory. On a warm cache, resolving a path like /home/alice/file.txt requires zero disk reads for the directory lookups._

---

**Q6. A process calls unlink("data.txt") but another process still has the file open. When is the inode and its data actually freed?**
- [ ] Immediately when unlink() returns
- [ ] When the filesystem is next unmounted
- [ ] When the OS runs fsck
- [x] When the link count reaches zero AND all file descriptors referencing it are closed

_Explanation: unlink() decrements the hard-link count. Data blocks are freed only when link_count == 0 AND no open file descriptor holds the file. This is how deletion of a file open by a running program is handled gracefully on Unix._
