# Files, Directories, and Path Resolution

Understanding how the OS turns a string like `/home/alice/docs/report.txt` into bytes on disk is essential for writing correct, efficient systems code.

## What Is a File?

A **file** is a named, ordered sequence of bytes stored persistently. From the kernel's perspective a file is identified not by its name but by an **inode number** — a small integer index into a per-filesystem table. The name is just a label stuck in a directory.

Key properties of a file:

- **Data:** the raw byte content.
- **Metadata:** owner UID/GID, permission bits, size, link count, three timestamps (atime, mtime, ctime).
- **Inode:** the unique in-filesystem identifier.

## What Is a Directory?

A **directory** is a special file whose content is a mapping from names to inode numbers:

```
"."        → 42    (self)
".."       → 17    (parent)
"report.txt" → 91
"archive"    → 55
```

On disk this can be a flat linear list, a hash table, or a B-tree (ext4 uses htree). Directories do not store file data — only names and inode references.

## Absolute vs. Relative Paths

| Path type | Starts with | Resolved from |
|-----------|-------------|---------------|
| Absolute  | `/`         | filesystem root |
| Relative  | anything else | process's current working directory (`cwd`) |

Every process has a `cwd` field in its kernel struct. Relative paths avoid repeated traversal of the root, but absolute paths are unambiguous.

## Path Resolution (namei)

The kernel function `namei` (name-to-inode) walks the path component by component:

```
Resolve  /home/alice/docs/report.txt
Step 1:  Start at root inode (inode 2 by convention)
Step 2:  Look up "home"  in root dir → inode 7
Step 3:  Look up "alice" in inode 7  → inode 23
Step 4:  Look up "docs"  in inode 23 → inode 41
Step 5:  Look up "report.txt" in inode 41 → inode 88
Result:  inode 88 → read data blocks
```

Each step is a directory lookup. On a cold cache that is one disk read per component — expensive for deep paths.

## The Dot and Dot-Dot Entries

Every directory contains two mandatory entries:

- **`.`** — a hard link to itself. `chdir(".")` is a no-op.
- **`..`** — a hard link to the parent directory. Used by `cd ..` and path resolution.

The root directory's `..` points back to itself, so `/../` resolves to `/`.

## Mount Points

Multiple physical devices can be grafted into the single namespace via **mounting**:

```bash
mount /dev/sdb1 /mnt/usb
```

After mounting, path resolution that crosses `/mnt/usb` switches to the new filesystem's inode table. The VFS layer manages the transition transparently.

## Worked Example: stat()

```c
#include <sys/stat.h>
#include <stdio.h>

int main(void) {
    struct stat st;
    stat("/etc/passwd", &st);
    printf("inode=%lu size=%ld links=%hu\n",
           (unsigned long)st.st_ino,
           (long)st.st_size,
           st.st_nlink);
    return 0;
}
```

`stat()` performs path resolution internally and returns metadata from the inode — not the directory.

## Common Pitfalls

- **TOCTOU races.** Checking a path with `access()` then opening it with `open()` opens a race window. Use `openat()` with a directory file descriptor for atomicity.
- **Long paths.** POSIX guarantees `PATH_MAX` (often 4096 bytes) but does not require all operations to support it; some tools silently truncate.
- **Dangling symlinks.** A symlink target may not exist; always handle `ENOENT` from open after resolving a symlink.

> **Interview answer:** "Path resolution (namei) walks each component of a path through successive directory lookups, converting each name to an inode number, until it reaches the final inode that holds the file's metadata and data block pointers."
