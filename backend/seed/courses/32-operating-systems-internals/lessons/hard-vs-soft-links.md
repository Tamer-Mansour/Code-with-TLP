# Hard Links vs Symbolic Links

Both hard links and symbolic links let multiple names refer to the same file, but they differ fundamentally in how they work, and choosing the wrong one is a classic source of bugs.

## Hard Links

A **hard link** is a directory entry that points directly to an inode. Every file starts with one hard link (its original name). Creating a second hard link with `ln` adds another directory entry pointing to the **same inode**:

```bash
ln report.txt backup.txt
```

```
Directory:
  "report.txt" → inode 88
  "backup.txt" → inode 88   ← same inode!

Inode 88:
  link_count = 2
  data blocks: [...]
```

The inode's **link count** tracks the number of directory entries pointing to it. Data is freed only when the link count drops to zero **and** no open file descriptor holds the file.

```bash
$ stat report.txt
  Inode: 88     Links: 2
```

### Hard Link Rules

- Both names are fully equivalent — there is no "original".
- Renaming or deleting one name does not affect the other.
- Hard links **cannot cross filesystem boundaries** (inode numbers are per-filesystem).
- Hard links to **directories** are not permitted in most Unix systems (to prevent cycles in the directory DAG).

## Symbolic Links (Symlinks)

A **symbolic link** is a special file whose content is a **path string** (the target path). The inode of a symlink stores the path, not the data of the target.

```bash
ln -s /home/alice/report.txt shortcut.txt
```

```
"shortcut.txt" → inode 99  (type: symlink, data="/home/alice/report.txt")
```

When the kernel encounters a symlink during path resolution it transparently follows it (up to a loop limit, typically 40 hops on Linux).

### Symbolic Link Rules

- Can cross filesystem boundaries.
- Can point to directories.
- Target need not exist — a **dangling symlink** is valid on disk but causes `ENOENT` when followed.
- Deleting the target breaks all symlinks to it.
- Symlinks have their own inode, permissions (always `lrwxrwxrwx`), and `atime`/`ctime`.

## Side-by-Side Comparison

| Property | Hard Link | Symbolic Link |
|----------|-----------|---------------|
| Same inode as target? | Yes | No (own inode) |
| Cross-filesystem? | No | Yes |
| Works for directories? | No (usually) | Yes |
| Survives target deletion? | Yes (is the target) | Becomes dangling |
| Path resolution overhead | None | One extra lookup |
| Shows up in `ls -l` | Looks like regular file | `l` prefix, `->` target |

## Worked Example

```bash
echo "data" > original.txt
ln   original.txt hard.txt       # hard link
ln -s original.txt soft.txt      # symlink

ls -li
# 88 -rw-r--r-- 2 alice alice 5 ... original.txt
# 88 -rw-r--r-- 2 alice alice 5 ... hard.txt       ← same inode 88
# 99 lrwxrwxrwx 1 alice alice 12 ... soft.txt -> original.txt

rm original.txt
cat hard.txt    # OK — data still accessible through inode 88
cat soft.txt    # ERROR: No such file or directory (dangling symlink)
```

## Common Pitfalls

- **Using symlinks for shared libraries.** If `libfoo.so -> libfoo.so.1.2`, and libfoo.so.1.2 is deleted during an upgrade, processes trying to open `libfoo.so` fail. Always update the symlink atomically with `ln -sf`.
- **Symlink loops.** `a -> b` and `b -> a` loops are detected by the kernel's hop counter. `open()` returns `ELOOP` after 40 hops.
- **Backup tools and hard links.** `rsync --hard-links` preserves hard link relationships; without this flag, duplicated data inflates backup size.
- **stat vs lstat.** `stat()` follows symlinks; `lstat()` returns the symlink's own metadata. Always use `lstat()` when you need to detect symlinks.

## Checking Link Type in C

```c
#include <sys/stat.h>
#include <stdio.h>

int main(void) {
    struct stat st;
    lstat("soft.txt", &st);  // do NOT follow symlink
    if (S_ISLNK(st.st_mode))
        printf("symlink\n");
    else if (S_ISREG(st.st_mode))
        printf("regular file (nlinks=%hu)\n", st.st_nlink);
    return 0;
}
```

> **Interview answer:** "A hard link is an additional directory entry pointing to the same inode — it survives deletion of the original name but cannot cross filesystems. A symbolic link is a separate inode storing a path string — it can cross filesystems and point to directories, but breaks if the target is removed."
