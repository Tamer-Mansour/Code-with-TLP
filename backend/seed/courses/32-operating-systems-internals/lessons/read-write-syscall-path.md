# The read() and write() System Call Path

`read()` and `write()` are the two most-called system calls in any I/O-heavy program. Knowing exactly what happens inside the kernel separates candidates who can design systems from those who can only use them.

## The read() Path

```
fd = open("data.txt", O_RDONLY)
n  = read(fd, buf, 4096)
```

### 1. VFS Layer

The kernel represents every open file as a `struct file`. The file descriptor `fd` is an index into the per-process file descriptor table, which holds pointers to `struct file` objects.

```c
// Kernel: fs/read_write.c (simplified)
ssize_t vfs_read(struct file *file, char __user *buf, size_t count, loff_t *pos)
{
    if (!(file->f_mode & FMODE_READ))
        return -EBADF;
    if (!file->f_op->read_iter)
        return -EINVAL;
    return call_read_iter(file, &kiocb, &iter);
}
```

The Virtual File System (VFS) is an abstraction layer. It calls the `read_iter` function pointer on the file's operations table, which dispatches to the correct filesystem (ext4, tmpfs, socket, pipe, etc.).

### 2. Page Cache Check

For regular files, the kernel first checks the **page cache** — a RAM cache of disk blocks mapped to `(inode, page_index)` tuples.

```
read() → VFS → page cache?
                 ├─ HIT:  copy page to user buf, return
                 └─ MISS: submit block I/O, wait, copy, return
```

- **Cache hit:** `copy_to_user()` copies bytes from a cached page to the user buffer. Fast path, no disk I/O.
- **Cache miss:** The kernel submits an I/O request to the block layer, puts the calling thread to sleep (state = `TASK_INTERRUPTIBLE`), and wakes it when the I/O completes.

### 3. copy_to_user

```c
// Safely copies kernel memory to user space
if (copy_to_user(user_buf, kernel_page + offset, count))
    return -EFAULT;
```

`copy_to_user` validates the user pointer and handles page faults. A raw pointer dereference would be a kernel security hole.

## The write() Path

```c
n = write(fd, "hello\n", 6);
```

### 1. Validate and Find the File

Same as `read()` — validate fd, check `FMODE_WRITE`, dispatch through VFS.

### 2. copy_from_user

```c
// Kernel copies user buffer into kernel space first
if (copy_from_user(kernel_buf, user_buf, count))
    return -EFAULT;
```

The kernel must copy the data out of user space **before** it can be written to the page cache or device. If the kernel deferred this and the user modified `buf` after the call returned, the data written would be wrong (TOCTOU issue).

### 3. Write to Page Cache (Buffered I/O)

By default (`O_WRONLY` without `O_SYNC`), the write goes into the page cache and the page is marked **dirty**. The kernel returns to user space immediately — the data is **not yet on disk**.

The kernel's **writeback daemon** (`pdflush`/`kworker`) periodically flushes dirty pages to disk based on:
- Age of the dirty page (default 30 s).
- Dirty ratio thresholds (system-wide memory pressure).
- Explicit `fsync()` / `fdatasync()` calls.

### 4. Direct I/O (O_DIRECT)

With `O_DIRECT`, the kernel bypasses the page cache entirely. Data is transferred directly between user buffers and the device with DMA. Useful for databases that manage their own caching.

```c
int fd = open("db.dat", O_RDWR | O_DIRECT);
// buf must be aligned to logical block size (usually 512 or 4096 bytes)
```

## End-to-End Latency Breakdown

| Path | Typical Latency |
|---|---|
| `write()` to page cache (buffered) | < 1 µs |
| `write()` + `fsync()` to SSD | 50–200 µs |
| `write()` + `fsync()` to HDD | 5–10 ms |
| `read()` from page cache | < 1 µs |
| `read()` with cache miss (SSD) | 50–200 µs |

## Common Pitfalls

- **`write()` returning short:** A `write()` may write fewer bytes than requested (especially on sockets). Always loop until all bytes are written.
- **`write()` success does not mean durability:** Call `fsync()` after critical writes (databases, transaction logs).
- **`read()` on a socket may block indefinitely** if no data arrives and the socket is in blocking mode.

**Interview answer:** `read()` checks the page cache first; on a hit it calls `copy_to_user` and returns immediately; on a miss it sleeps while block I/O completes. `write()` copies user data with `copy_from_user`, marks the page dirty in cache, and returns — `fsync()` is needed for durability.
