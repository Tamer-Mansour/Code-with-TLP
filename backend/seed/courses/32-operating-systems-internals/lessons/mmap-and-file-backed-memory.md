# mmap and File-Backed Memory

`mmap()` lets a process map a file (or device) directly into its virtual address space. Instead of `read()`/`write()` syscalls, the process accesses file data with ordinary pointer dereferences. The kernel's page cache and virtual memory system work together to make this efficient.

## The `mmap()` System Call

```c
#include <sys/mman.h>
#include <fcntl.h>

int fd = open("data.bin", O_RDWR);

// Map the entire file into virtual address space:
void *addr = mmap(
    NULL,           // let the kernel choose the virtual address
    file_size,      // number of bytes to map
    PROT_READ | PROT_WRITE,  // access permissions
    MAP_SHARED,     // changes are visible to other processes and written back to file
    fd,             // file descriptor
    0               // offset within file
);

// Now access the file like memory:
int *values = (int *)addr;
values[0] = 42;    // writes to the file (eventually)

// Unmap when done:
munmap(addr, file_size);
close(fd);
```

## How It Works Internally

`mmap()` does **not** copy the file into memory immediately. It creates a **Virtual Memory Area (VMA)** in the process's address space, backed by the file's page cache:

```
Process virtual address space:
  [0x7f000000 ... 0x7f001000]  ← VMA for mapped region

First access to 0x7f000000:
  MMU: no physical page mapped → page fault
  Kernel: check page cache
    Hit  → map page cache frame into process page table
    Miss → read from disk into page cache → map into process page table
  Process resumes — pointer dereference returns file data
```

This is **demand paging** applied to files. Pages are loaded on first access and may be shared among multiple processes that map the same file.

## `MAP_SHARED` vs `MAP_PRIVATE`

| Flag | Semantics | Use case |
|---|---|---|
| `MAP_SHARED` | Writes are visible to other mappings and written back to file | IPC, database files, shared data |
| `MAP_PRIVATE` | CoW — writes create a private copy, not written to file | Process image loading, read-only configuration files |

```c
// MAP_PRIVATE: read file but keep modifications private
void *addr = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_PRIVATE, fd, 0);
((char*)addr)[0] = 'X';   // does NOT modify the file
```

## mmap vs read/write

| Aspect | `read()`/`write()` | `mmap()` |
|---|---|---|
| Syscall overhead | One per I/O operation | Only on page faults (first access) |
| Copy | Kernel → userspace buffer | Zero-copy: kernel maps page cache directly |
| Sequential large files | Efficient with large buffers | Good, but page fault overhead for first touch |
| Random access | Expensive (seek + read) | Efficient — direct address computation |
| File larger than RAM | Must read in chunks | Kernel manages windowing automatically |

For large files with random access patterns (database B-tree files, memory-mapped databases like LMDB), `mmap()` eliminates copying and reduces syscall overhead significantly.

## Write-Back for `MAP_SHARED`

When you write to a `MAP_SHARED` mapping, the page cache page is marked **dirty** exactly as if `write()` had been called. The kernel flushes it asynchronously. To force durability:

```c
// Flush dirty pages in a mapped region to disk:
msync(addr, length, MS_SYNC);    // synchronous — blocks until flushed
msync(addr, length, MS_ASYNC);   // asynchronous — schedules flush, returns immediately
```

`msync()` is the mmap equivalent of `fsync()`. Without it, modifications may be lost on a crash.

## Memory-Mapped Databases: LMDB

**LMDB** (Lightning Memory-Mapped Database) uses `mmap()` for its entire storage engine:

```
mmap() the database file → entire B-tree is in virtual address space
Read: pointer dereference into mapped region (zero syscall, zero copy)
Write: CoW on B-tree pages, atomic root pointer update, msync() on commit
```

This design achieves very high read throughput because reads are pure memory accesses with no syscall overhead.

## Anonymous Mappings

`mmap()` with `MAP_ANONYMOUS` (no file) allocates virtual address space backed by swap, not a file. This is how `malloc()` allocates large chunks internally:

```c
// Allocate 1 GB of virtual memory (no physical RAM until accessed):
void *buf = mmap(NULL, 1<<30, PROT_READ|PROT_WRITE,
                 MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
```

## Executable Loading via mmap

The dynamic linker uses `mmap()` to load executable segments and shared libraries:

```bash
cat /proc/$(pgrep nginx | head -1)/maps | head -20
# 55f3a2400000-55f3a2411000 r--p ... /usr/sbin/nginx   ← text segment (MAP_PRIVATE)
# 7f1234500000-7f12346c0000 r--p ... /lib/x86_64-linux-gnu/libc.so.6
```

The code pages of shared libraries are `MAP_SHARED` (read-only / execute) so all processes share the same physical pages.

## Pitfalls

- **SIGBUS**: accessing a mapped region beyond the file's end, or after the file is truncated, raises `SIGBUS`.
- **Coherence**: with `MAP_SHARED`, concurrent writers must use explicit locking — the kernel does not serialize mmap writes.
- **Hugepages**: `mmap` defaults to 4 KB pages; use `MAP_HUGETLB` for large mappings to reduce TLB pressure.

**Interview answer:** `mmap()` maps a file into a process's virtual address space so file data can be read and written as ordinary memory. The kernel backs the mapping with page cache frames, loading pages on demand via page faults and (for `MAP_SHARED`) writing dirty pages back to the file asynchronously. It eliminates the kernel-to-userspace copy that `read()` requires, making random access to large files very efficient.
