# The Page Cache and Buffer Cache

Modern operating systems use main memory not just for running processes but also as a high-speed staging area for disk data. This in-memory layer is called the **page cache** (sometimes also called the buffer cache). Understanding it is essential for reasoning about I/O performance and memory pressure in Linux.

## What Is the Page Cache?

The **page cache** is a region of kernel memory that holds recently-read and recently-written disk blocks mapped to filesystem pages. When a process reads a file, the kernel:

1. Checks whether the data is already in the page cache.
2. If yes (**cache hit**) — returns the data immediately, no disk I/O.
3. If no (**cache miss**) — reads the data from disk, stores a copy in the cache, then returns it.

```
read("/var/log/app.log", buf, 4096)
        │
        ▼
    Kernel: check page cache
    ├── Hit  → memcpy to userspace, return          (~100 ns)
    └── Miss → submit I/O request to disk driver
               wait for data (~0.1 ms SSD / ~10 ms HDD)
               copy into page cache frame
               memcpy to userspace, return
```

This is transparent to the process — it just calls `read()`.

## The Historical Buffer Cache

Older Unix kernels maintained two separate caches:

| Cache | Granularity | Contents |
|---|---|---|
| Buffer cache | 512-byte block | Raw disk blocks (block device I/O) |
| Page cache | 4 KB page | File-backed virtual memory pages |

In Linux 2.4 (year 2001) these were **unified**: block device buffers became a thin wrapper over the page cache. Today the term "buffer cache" usually refers to the page cache itself, though `free` output still shows `buff/cache` as a combined field.

## Cache Eviction: The LRU Approximation

The page cache competes with processes for physical RAM. The kernel's **page replacement daemon** (`kswapd`) evicts pages when memory runs low, using an **approximate LRU** (Least Recently Used) policy implemented with two lists:

- **Active list** — pages that were recently accessed twice or more.
- **Inactive list** — pages accessed only once or promoted back from active.

Pages migrate between lists based on access bits set by the MMU. Only inactive pages are candidates for eviction.

```bash
# See current page cache usage:
cat /proc/meminfo | grep -E "Cached|Buffers|MemFree"
# Output example:
# MemFree:        512000 kB
# Buffers:         32768 kB    ← raw block metadata
# Cached:        3145728 kB    ← page cache (file data)
```

## Read-Ahead (Prefetching)

When the kernel detects sequential access patterns (e.g., reading a large file linearly), it issues **read-ahead**: fetching pages beyond the current read position before the process requests them. This hides disk latency and dramatically improves throughput.

```c
// Hint the kernel to prefetch:
posix_fadvise(fd, 0, file_size, POSIX_FADV_SEQUENTIAL);
// Kernel doubles (or more) its read-ahead window.
```

## Dirty Pages and Write-Back

When a process **writes** to a file, the data first lands in the page cache and the page is marked **dirty**. The process returns immediately — the kernel will flush dirty pages to disk asynchronously in the background (write-back). This is why writes appear fast but data can be lost on a crash.

```
write(fd, "hello", 5)
    │
    ▼
    Page cache page updated → marked dirty
    ▼
    Process returns immediately   ← no disk I/O yet
    ...
    kworker thread (later): dirty page → disk flush
```

## Dropping the Cache (Testing/Debugging)

```bash
# Force the kernel to drop the page cache (useful for benchmarking):
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
```

This does **not** harm data integrity — dirty pages are flushed by `sync` first. Never do this on a production server without good reason.

## Key Numbers

| Operation | Latency |
|---|---|
| Page cache hit | ~100 ns |
| NVMe SSD read | ~100 µs |
| SATA SSD read | ~0.5 ms |
| HDD seek + read | ~10 ms |

The page cache turns filesystem I/O into memory access for hot data, making it one of the highest-leverage caches in the whole system.

**Interview answer:** The page cache is kernel memory that holds recently accessed file data so that repeated reads are served from RAM instead of disk. Writes go to the cache first and are flushed to disk asynchronously (write-back), which is why unflushed data can be lost on a crash.
