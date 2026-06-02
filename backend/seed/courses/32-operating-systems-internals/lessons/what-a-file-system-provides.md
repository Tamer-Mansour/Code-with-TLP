# What a File System Provides

Every program eventually needs to store data beyond the lifetime of a process — on disk, SSD, or network storage. A **file system** is the abstraction layer between raw block devices and the rest of the operating system. Without it, applications would have to manage disk sectors directly, an impossible burden at scale.

## Core Abstractions

A file system provides four fundamental abstractions:

- **Files** — named, byte-addressable sequences of data with a defined length and associated metadata (owner, permissions, timestamps).
- **Directories** — special files that map human-readable names to lower-level file identifiers (inodes on Unix systems).
- **Paths** — hierarchical names like `/home/alice/report.txt` that allow processes to locate files without knowing their physical location on disk.
- **Namespace** — a single, unified tree rooted at `/` (Unix) or per-drive letters (Windows), regardless of how many physical devices are mounted.

## What the File System Manages

| Concern | What the FS does |
|---------|-----------------|
| Storage allocation | Tracks which disk blocks are free or in use |
| Naming | Translates pathname strings to file identifiers |
| Metadata | Stores ownership, size, permissions, timestamps |
| Consistency | Ensures disk remains valid after a crash |
| Access control | Enforces permission checks on every open/read/write |

## Persistence and Durability

Unlike process memory, files survive across reboots. The file system guarantees:

1. **Durability** — data written to disk survives power loss (with appropriate fsync calls).
2. **Crash consistency** — journaling or copy-on-write techniques ensure the disk never ends up in a half-written state.
3. **Recoverability** — after an unclean shutdown, fsck or a journal replay can restore a consistent state.

## Common Pitfalls

- **Forgetting fsync.** Calling `write()` only sends data to the page cache. Without `fsync()`, the OS may not flush to disk before a crash.
- **Assuming atomicity.** A `write()` larger than one block is not atomic; a crash mid-write can leave a file partially updated.
- **Treating the file system as a database.** Repeated tiny writes without buffering are slow; disk I/O has high per-operation overhead.

## A Quick Code Example

```c
#include <fcntl.h>
#include <unistd.h>

int main(void) {
    int fd = open("data.bin", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    write(fd, "hello", 5);
    fsync(fd);   // flush page cache to disk — do not skip!
    close(fd);
    return 0;
}
```

Without `fsync`, the kernel may buffer "hello" in RAM and never reach disk if the machine crashes.

## The File System Stack

```
Application
    │  open() / read() / write()
    ▼
VFS (Virtual File System) ← unified kernel interface
    │
    ▼
Concrete FS driver (ext4, NTFS, ZFS, …)
    │
    ▼
Block device layer (request queue, scheduler)
    │
    ▼
Disk / SSD hardware
```

Each layer has a clean contract, allowing the VFS to multiplex dozens of concrete file system formats behind a single POSIX API.

## Why It Matters for Interviews

File system questions appear in systems design and OS interviews because every storage decision ultimately touches the FS. Knowing that the FS bridges raw blocks and the application API, and understanding durability vs. persistence, sets a strong foundation.

> **Interview answer:** "A file system provides named, persistent byte sequences (files), a hierarchical naming space (directories and paths), metadata management, access control, and crash consistency on top of raw block storage."
