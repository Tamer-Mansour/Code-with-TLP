# fsync, Durability, and the Write Barrier

Even though the OS write-back cache makes writes appear instant, data is not truly **durable** until it reaches non-volatile storage. The `fsync()` system call and the related concept of **write barriers** are the mechanisms applications use to demand real durability.

## The Durability Gap

```
Application write path:
  write(fd, data, len)
      ↓ (returns immediately)
  Kernel page cache (DRAM)    ← data here; power loss = lost!
      ↓ (async, seconds later)
  Disk controller write-back cache (DRAM on drive) ← still volatile!
      ↓ (async)
  Non-volatile storage (flash cells / magnetic platters) ← DURABLE
```

An acknowledged `write()` syscall only guarantees data is in kernel memory. Two more layers of volatile cache stand between you and durability.

## `fsync()` — Flush to Physical Media

```c
#include <unistd.h>

int fd = open("txn.log", O_WRONLY | O_CREAT | O_APPEND, 0644);
write(fd, &record, sizeof(record));

// Force data AND metadata (inode timestamps, size) to disk:
if (fsync(fd) != 0) {
    perror("fsync failed");
    // Handle error — storage may have failed
}
close(fd);
```

`fsync()` blocks until:
1. Dirty pages for this file are written from the page cache to the disk controller.
2. The disk controller's own cache is flushed to the physical medium.

The second step is triggered by a **FLUSH CACHE** SCSI/ATA command. On drives with a battery-backed write cache this step may be skipped (the drive guarantees cache survives power loss).

## `fdatasync()` — Data Only, Skip Metadata

`fdatasync()` is like `fsync()` but skips flushing metadata (atime, mtime, file size) **unless the size has changed**. Useful for log writers that update existing fixed-size records:

```c
fdatasync(fd);   // Faster than fsync() when metadata hasn't changed
```

Rule of thumb: use `fdatasync()` for log/WAL files where size is extended in batches; use `fsync()` when metadata correctness is also required.

## `O_SYNC` and `O_DSYNC`

Open flags that enforce per-write durability without explicit `fsync()` calls:

```c
// O_SYNC: every write() call acts like write() + fsync()
int fd = open("wal.log", O_WRONLY | O_CREAT | O_SYNC, 0644);
write(fd, data, len);   // blocks until physically durable

// O_DSYNC: every write() acts like write() + fdatasync()
int fd = open("data.bin", O_WRONLY | O_CREAT | O_DSYNC, 0644);
```

These are appropriate for write-ahead logs or append-only audit files where every write must survive a crash.

## Write Barriers

A **write barrier** is a command to the storage device that says: "flush all writes issued before this point to non-volatile media before accepting any new writes." It enforces ordering across the storage stack.

In Linux, write barriers are used:
- By journaling filesystems to ensure the commit block lands after the data blocks.
- By databases (PostgreSQL, MySQL) when writing WAL records.

```c
// Force a write barrier via fsync on a file descriptor:
fsync(fd);   // implicitly issues a barrier to the underlying block device

// Or directly on a block device:
ioctl(device_fd, BLKFLSBUF);   // flush block device buffers
```

## The `sync()` System Call

```c
sync();   // Flush ALL dirty pages in the entire system to disk
```

`sync()` is a blunt instrument — it flushes every process's dirty pages. It does **not** wait for writes to complete (it is advisory on Linux). Use `fsync()` on specific file descriptors for reliable durability.

## Practical Patterns

### Database WAL Pattern (PostgreSQL-style)

```c
// 1. Write WAL record to log buffer
write(wal_fd, &wal_record, sizeof(wal_record));

// 2. On transaction commit, force WAL to disk
fsync(wal_fd);

// 3. Now it is safe to acknowledge the commit to the client
send(client_fd, "COMMIT OK", 9, 0);

// (Data files are written lazily in the background)
```

### Group Commit Optimization

`fsync()` is expensive (~1–10 ms). High-throughput databases **batch** multiple transactions and call `fsync()` once for all of them:

```
T1 commit → add to "waiting for fsync" queue
T2 commit → add to queue
T3 commit → triggers fsync()
            → fsync returns → all three transactions are durable
            → acknowledge T1, T2, T3 to clients simultaneously
```

This technique (group commit) can multiply transaction throughput by 10x or more.

## Disks That Lie

Some consumer-grade HDDs and SSDs **acknowledge the FLUSH CACHE command without actually flushing** — they lie to improve benchmark scores. This can cause silent data corruption on power loss. Enterprise drives have power-loss protection (PLP) capacitors and never lie.

```bash
# Test if your drive handles fsync honestly:
# hdparm -W0 /dev/sda   (disable write cache — guaranteed honest but slow)
```

**Interview answer:** `fsync(fd)` forces all dirty pages for a file from the kernel page cache through the disk controller's cache to non-volatile storage, blocking until completion. It is required for durability guarantees because `write()` only updates kernel memory. Databases call `fsync()` on their WAL before acknowledging a committed transaction.
