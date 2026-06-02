# Write-Through vs Write-Back Caching

Every cache in a system — CPU cache, page cache, disk controller cache — must decide what happens when the CPU (or application) writes data. The two fundamental policies are **write-through** and **write-back**. Each trades durability for performance.

## Write-Through

In **write-through**, every write is sent to both the cache and the backing store **immediately and synchronously**. The write is not acknowledged to the caller until both levels are updated.

```
Application: write("data")
    │
    ▼
Cache ──────────────── Backing store (disk)
   (updated)               (updated NOW)
    │
    ▼
Application: write returns  ← waits for disk
```

**Pros:**
- Simple consistency model — cache and disk are always identical.
- No data loss on crash — every acknowledged write is already on disk.

**Cons:**
- Every write pays the full disk latency (~0.1–10 ms per op).
- Write throughput is bounded by the disk, not RAM.
- Write bursts cannot be absorbed or coalesced.

## Write-Back (Write-Behind)

In **write-back**, the write updates the cache immediately and is acknowledged to the caller. The dirty data is flushed to the backing store **later**, asynchronously.

```
Application: write("data")
    │
    ▼
Cache (updated, marked dirty)
    │
    ▼
Application: write returns ← immediately, disk not yet touched
    ...
    (later) Background flush thread: dirty cache → disk
```

**Pros:**
- Writes appear near-instant (memory speed).
- Multiple writes to the same block can be **coalesced** — only the final version hits disk.
- Write bursts are smoothed out; disk sees steady throughput.

**Cons:**
- Data in cache but not yet on disk can be **lost on a power failure or crash**.
- Implementing correctly requires careful dirty-tracking and ordering.

## Linux Page Cache Is Write-Back

Linux uses write-back by default. The kernel's `pdflush`/`writeback` threads flush dirty pages when:

1. A dirty page has been dirty for more than `dirty_expire_centisecs` (default 30 s).
2. The ratio of dirty pages to total RAM exceeds `dirty_ratio` (default ~20%).
3. The ratio exceeds `dirty_background_ratio` (default ~10%) — background flush starts.
4. The application calls `fsync()`, `fdatasync()`, or `sync()`.

```bash
# Tune dirty write-back thresholds:
sysctl vm.dirty_background_ratio   # background flush starts at this %
sysctl vm.dirty_ratio              # process is throttled at this %
sysctl vm.dirty_expire_centisecs   # max age of dirty page before forced flush
```

## Write-Allocate vs No-Write-Allocate

These policies interact with **what happens on a write miss** (writing to an address not currently in cache):

| Policy | On write miss |
|---|---|
| Write-allocate | Load the block into cache first, then write. Pairs with write-back. |
| No-write-allocate | Write directly to backing store, skip cache. Pairs with write-through. |

CPU L1/L2 caches almost universally use write-back + write-allocate because write-miss is common and re-use is high.

## Disk Controller Caches

Modern HDDs and SSDs have their own onboard DRAM cache, also operating in write-back mode by default. This is why:

```bash
# Flush the OS page cache:
fsync(fd);      # Still may not flush the drive's own cache!

# Force physical media commit (for drives that support it):
ioctl(fd, HDIO_DRIVE_CMD, ...);   // or use "Force Unit Access" (FUA) flag
```

Some databases issue `fsync()` + verify, or use the `O_DIRECT | O_SYNC` flags, to bypass both the OS and drive caches for durability.

## Side-by-Side Comparison

| Property | Write-Through | Write-Back |
|---|---|---|
| Write latency | High (disk latency) | Low (memory speed) |
| Write throughput | Limited by disk | High; bursts absorbed |
| Crash safety | Safe (disk always current) | Data loss possible |
| Complexity | Low | Higher (dirty tracking, ordering) |
| Where used | Simple embedded systems, SSD firmware for critical metadata | Linux page cache, CPU caches, most databases |

## A Practical Decision: When to Force Write-Through Behavior

Even on a write-back system, applications requiring durability can selectively opt in:

```c
// Open with O_SYNC: every write is synchronous (write-through behavior)
int fd = open("critical.log", O_WRONLY | O_CREAT | O_SYNC, 0644);
write(fd, record, len);  // returns only after disk confirms the write

// Or: write normally, then force flush before acknowledging a transaction
write(fd, record, len);
fsync(fd);              // blocks until dirty pages are on disk
```

**Interview answer:** Write-through sends every write to disk immediately (safe, slow); write-back acknowledges the write after updating the cache and flushes to disk asynchronously (fast, but data in cache can be lost on a crash). Linux's page cache uses write-back, which is why `fsync()` is necessary for durability guarantees.
