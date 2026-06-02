# File Descriptors and the Open File Table

When a process calls `open()`, the kernel returns a small non-negative integer called a **file descriptor** (fd). Behind that integer sit two kernel tables that govern how files are shared between processes — one of the most nuanced areas of Unix file semantics.

## The Three-Level Indirection

```
Process A                  Kernel
fd table                 open-file table            inode table
┌────────┐              ┌──────────────┐           ┌──────────┐
│ fd 0   │ ──────────► │ entry 10     │ ─────────► │ inode 88 │
│ fd 1   │ ──────────► │ f_pos=0      │           └──────────┘
│ fd 2   │ ─┐          │ flags=O_RDWR │
│ fd 3   │  │          │ ref_count=1  │
└────────┘  │          └──────────────┘
            │
Process B   │          ┌──────────────┐
fd table    └────────► │ entry 11     │ ─────────► same inode 88
┌────────┐             │ f_pos=0      │
│ fd 5   │ ──────────► │ ref_count=1  │
└────────┘             └──────────────┘
```

1. **Per-process fd table** — maps integers to open-file table entries.
2. **System-wide open-file table** — one entry per `open()` call; holds file position, flags, and ref count.
3. **Inode table** — one entry per file; shared across all open-file entries for the same file.

## Why the Split Matters

Two processes that `open()` the same file independently each get a separate open-file table entry with their **own file position**. Reading 100 bytes in process A does not advance process B's position. This is the expected POSIX behaviour.

After `fork()`, parent and child **share** the same open-file entry (the ref count increments). Moving the file position in the child is visible to the parent:

```c
int fd = open("data.txt", O_RDONLY);
if (fork() == 0) {
    read(fd, buf, 10);   // advances shared f_pos by 10
    exit(0);
}
wait(NULL);
read(fd, buf2, 5);       // reads from offset 10, not 0!
```

## File Descriptor Numbers and Inheritance

The kernel assigns the lowest unused fd number. By convention:

| fd | Name   | Default |
|----|--------|---------|
| 0  | stdin  | terminal read |
| 1  | stdout | terminal write |
| 2  | stderr | terminal write (unbuffered) |

File descriptors are inherited across `fork()` and survive `execve()` unless the `O_CLOEXEC` flag was set (or `FD_CLOEXEC` set via `fcntl`). Always set `O_CLOEXEC` when opening fds in a long-running server to avoid leaking them into child processes.

## dup() and dup2()

`dup(fd)` creates a new fd that points to the same open-file table entry. This is how shell redirection is implemented:

```c
// redirect stdout to a file
int out = open("log.txt", O_WRONLY | O_CREAT, 0644);
dup2(out, STDOUT_FILENO);  // fd 1 now points to log.txt's open-file entry
close(out);
// any write to fd 1 goes to log.txt
```

Both the old and the new fd share file position and flags.

## The Limits

| Limit | Typical value | Query / set |
|-------|--------------|-------------|
| Per-process soft fd limit | 1024 | `ulimit -n` |
| Per-process hard fd limit | 1048576 | `/proc/sys/fs/nr_open` |
| System-wide open files | 100000+ | `/proc/sys/fs/file-max` |

High-performance servers (nginx, Redis) bump the soft limit to hundreds of thousands with `setrlimit(RLIMIT_NOFILE, ...)`.

## Worked Example: Detecting an fd Leak

```bash
# Count open file descriptors for PID 1234
ls /proc/1234/fd | wc -l

# See what each fd points to
ls -la /proc/1234/fd
# lrwx...... fd/4 -> socket:[12345]
# lr-x...... fd/5 -> /var/log/app.log
```

An fd count that grows monotonically without bound indicates a leak — `open()` calls without matching `close()`.

## Common Pitfalls

- **Not closing fds after fork+exec.** Without `O_CLOEXEC`, a child exec'd into an unrelated binary inherits all parent fds — a security and resource leak.
- **Relying on `close()` for durability.** `close()` does not guarantee data reaches disk; call `fsync()` before `close()` for durability.
- **Large select() fd sets.** `select()` has a hard limit of `FD_SETSIZE` (1024) file descriptors. Use `poll()` or `epoll()` for servers with many connections.

> **Interview answer:** "A file descriptor is a per-process index into the open-file table; each open-file entry holds file position and flags and points to a shared inode. fork() makes parent and child share an open-file entry (same f_pos), while two independent open() calls create separate entries with independent positions."
