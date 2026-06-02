# The Virtual File System (VFS) Layer

Linux must support dozens of filesystem formats — ext4, XFS, btrfs, tmpfs, procfs, NFS, FUSE — simultaneously, and expose them all through a single, uniform POSIX API. The **Virtual File System (VFS)** is the kernel subsystem that makes this possible.

## The Core Problem VFS Solves

Without VFS, every syscall like `read()` would need a giant `switch` on the filesystem type. Instead, VFS defines a set of **abstract objects and method tables** (C function pointers). Each concrete filesystem registers handlers for those methods. Callers never know which backend they hit.

```
Application:  read(fd, buf, n)
                    │
              VFS dispatch (file->f_op->read)
                    │
         ┌──────────┴──────────┐
       ext4                  tmpfs
    (reads from disk)    (reads from RAM)
```

## The Four VFS Objects

| Object | Kernel struct | What it represents |
|--------|-------------|-------------------|
| Superblock | `struct super_block` | Mounted filesystem instance |
| Inode | `struct inode` | One file or directory |
| Dentry | `struct dentry` | One path component (name ↔ inode cache entry) |
| File | `struct file` | One open-file descriptor in a process |

### Superblock

Created when a filesystem is mounted. Stores volume-wide metadata (block size, inode count, free block count) and a `super_operations` table with methods like `alloc_inode`, `write_inode`, `sync_fs`.

### Inode

Mirrors what is on disk; also holds VFS-level fields (reference count, dirty flag) and an `inode_operations` table with methods: `lookup`, `create`, `link`, `unlink`, `mkdir`, `rename`, `readlink`.

### Dentry (Directory Entry Cache)

The dentry cache (**dcache**) maps `(parent_dentry, name)` pairs to inodes, avoiding repeated disk lookups for the same path component. Dentries are reference-counted and evicted under memory pressure.

```
/home/alice/report.txt resolved from cache:
  dentry("/")          → inode 2
  dentry("home")       → inode 7
  dentry("alice")      → inode 23
  dentry("report.txt") → inode 88   ← cache hit avoids disk read
```

### File Object

Created by `open()`, destroyed by `close()`. Holds the **file position** (`f_pos`), the open flags, and an `file_operations` table with `read`, `write`, `mmap`, `ioctl`, `poll`, `fsync`, and others.

## Method Table Example

```c
// ext4 registers these operations for regular files
const struct file_operations ext4_file_operations = {
    .read_iter   = ext4_file_read_iter,
    .write_iter  = ext4_file_write_iter,
    .mmap        = ext4_file_mmap,
    .fsync       = ext4_sync_file,
    .fallocate   = ext4_fallocate,
    // ...
};
```

When a process calls `read(fd, ...)`, the VFS calls `file->f_op->read_iter(...)` — dispatching to whichever concrete implementation was registered at mount time.

## The Page Cache and VFS

VFS sits above the **page cache** (also called the buffer cache). Reads are served from cached pages when possible; writes go to dirty pages that are flushed to disk by `pdflush`/writeback threads or `fsync()`.

```
read() → page in cache? → return data
                       → no → schedule block read → fill page → return data
```

This means two processes reading the same file share physical pages — a critical memory efficiency win.

## procfs and sysfs as VFS Filesystems

Special kernel-internal filesystems implement the same VFS interface without any disk backing:

- **procfs** (`/proc`) — each directory entry's `read` method calls a kernel function that generates text on the fly.
- **sysfs** (`/sys`) — exposes kernel objects (devices, drivers) as a tree of files.
- **tmpfs** (`/tmp`) — stores data in anonymous pages; disappears on reboot.

## Common Pitfalls

- **Dentry cache pollution.** Creating millions of short-lived files (log rotation, temp files) can thrash the dcache. Use dedicated directories or tmpfs.
- **Forgetting that ioctl is filesystem-specific.** `ioctl(fd, FIEMAP, ...)` works on ext4 but not on NFS or FUSE unless implemented.
- **VFS vs filesystem consistency.** VFS flushes the page cache; filesystem journals protect on-disk metadata separately. Both layers must cooperate for full durability.

> **Interview answer:** "VFS defines abstract objects (superblock, inode, dentry, file) with method tables. Concrete filesystems register their implementations at mount time; all POSIX file syscalls dispatch through VFS so the rest of the kernel and all applications remain filesystem-agnostic."
