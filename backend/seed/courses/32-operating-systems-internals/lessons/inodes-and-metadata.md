# Inodes and File Metadata

The **inode** (index node) is the central data structure of Unix-style file systems. It stores everything about a file *except* its name. Understanding inodes unlocks almost every file system interview question.

## What Is Stored in an Inode?

```
Inode 88
├── File type        (regular, directory, symlink, device, …)
├── Permissions      (rwxr-xr-x → 0755)
├── Link count       (number of hard links pointing here)
├── Owner UID / GID
├── File size        (bytes)
├── atime            (last access time)
├── mtime            (last data modification time)
├── ctime            (last inode/metadata change time)
├── Block count      (512-byte units allocated on disk)
└── Block pointers   (direct, indirect, double-indirect, …)
```

The inode does **not** store the filename. Names live in directory entries, which is what allows one inode to have multiple names (hard links).

## Inode Numbers

Each filesystem has a flat array (or B-tree) of inodes, indexed by **inode number**. Inode numbers are filesystem-local — the same number can exist in two different filesystems.

```bash
$ ls -i /etc/passwd
524289 /etc/passwd
```

Root inode is conventionally inode **2** (inode 1 is reserved for bad-block tracking in ext4).

## The Three Timestamps

| Field | Updated when |
|-------|-------------|
| `atime` | File data is read (often disabled with `noatime` for performance) |
| `mtime` | File data is written |
| `ctime` | Inode fields change (chmod, chown, rename, write) |

`ctime` is **not** creation time — it is the inode *change* time. Most filesystems store no true creation timestamp in the inode; ext4 adds `crtime` as an extension.

## Inode Size and Allocation

On ext4, each inode is 256 bytes by default. The total number of inodes is fixed at **format time**:

```bash
mkfs.ext4 -N 1000000 /dev/sdb1   # create 1M inodes
```

A filesystem can run out of inodes before it runs out of disk space if many tiny files exist. `df -i` shows inode usage.

## Block Pointers Inside the Inode

An inode stores a small array of block pointers. Classic Unix (UFS/ext2) used:

| Pointer type | Blocks reachable |
|--------------|-----------------|
| 12 direct pointers | 12 × block_size |
| 1 single indirect | block_size / 4 addresses |
| 1 double indirect | (block_size / 4)² addresses |
| 1 triple indirect | (block_size / 4)³ addresses |

With 4 KiB blocks, the maximum file size through triple indirection is ≈ 4 TiB. ext4 replaces this scheme with **extents** (contiguous block ranges) for efficiency.

## Worked Example: inode lookup in C

```c
#include <sys/stat.h>
#include <stdio.h>
#include <time.h>

void print_inode_info(const char *path) {
    struct stat st;
    if (stat(path, &st) == -1) { perror("stat"); return; }

    printf("inode:  %lu\n",   (unsigned long)st.st_ino);
    printf("size:   %ld B\n", (long)st.st_size);
    printf("links:  %hu\n",   st.st_nlink);
    printf("mtime:  %s",      ctime(&st.st_mtime));
    printf("perms:  %o\n",    st.st_mode & 07777);
}

int main(void) {
    print_inode_info("/etc/hosts");
    return 0;
}
```

## Common Pitfalls

- **Running out of inodes.** `df -i` is the diagnostic; the fix is reformatting or using a filesystem with dynamic inode allocation (XFS, btrfs).
- **ctime vs mtime confusion.** `rsync -a` uses `mtime`; a `chmod` changes `ctime` but not `mtime`, so rsync may skip a file whose metadata changed.
- **Hard link surprises.** Deleting a filename decrements the link count. The inode (and data) is freed only when the link count reaches zero and no open file descriptor holds the file.

## Inode Lifecycle

```
mkfs  →  inode allocated (link count = 0)
create → directory entry added, link count = 1
link   → another directory entry, link count = 2
unlink → link count → 1; data still on disk
unlink → link count → 0, last fd closed → blocks freed
```

> **Interview answer:** "An inode is the per-file metadata record in a Unix filesystem. It stores type, permissions, owner, size, timestamps, and block pointers — everything except the filename, which lives in a directory entry. The inode is freed only when the hard-link count reaches zero and no open file descriptor holds the file."
