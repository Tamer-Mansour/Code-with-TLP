# Process Creation: fork(), exec(), and the Process Tree

On Unix-like systems, every process (except the very first) is born from another process. The kernel provides two foundational system calls — `fork()` and `exec()` — that together implement a clean separation between "create a new process" and "load a new program into it".

## The fork() System Call

`fork()` creates a **nearly identical copy** of the calling process. After `fork()` returns, two processes exist — the **parent** and the **child** — running the same code but able to diverge based on the return value.

```c
#include <unistd.h>
#include <stdio.h>

int main(void) {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        return 1;
    } else if (pid == 0) {
        // ── Child process ──
        printf("Child: my PID = %d, parent PID = %d\n", getpid(), getppid());
    } else {
        // ── Parent process ──
        printf("Parent: my PID = %d, child PID = %d\n", getpid(), pid);
    }
    return 0;
}
```

### What fork() Copies
| Resource | Behaviour |
|----------|-----------|
| Virtual address space | Copied (copy-on-write) |
| File descriptors | Shared (same open-file table entries) |
| Signal handlers | Inherited |
| PID | Child gets a new PID |
| Memory | Copy-on-write: pages shared until either writes |

**Copy-on-write (COW)**: Rather than duplicating gigabytes of RAM, the kernel marks all pages shared and read-only. Only when either process writes to a page does the kernel copy that page for the writer. This makes `fork()` very cheap even for large processes.

## The exec() Family

`exec()` replaces the calling process's address space with a new program. The PID stays the same; the code, data, heap, and stack are entirely replaced.

```c
#include <unistd.h>

int main(void) {
    // Replace this process with /bin/ls -la
    char *argv[] = {"ls", "-la", "/tmp", NULL};
    char *envp[] = {NULL};

    execve("/bin/ls", argv, envp);

    // If execve() returns, it failed
    perror("execve");
    return 1;
}
```

Common variants: `execl`, `execlp`, `execv`, `execvp`, `execvpe` — differing in how the path is resolved and how arguments are passed (list vs. array, with/without PATH search).

### What exec() Preserves (Survives exec)
- PID and PPID
- Open file descriptors (unless `FD_CLOEXEC` is set)
- Current working directory
- Signal mask (blocked signals)

### What exec() Replaces
- The entire address space (text, data, BSS, heap, stack)
- Signal handlers (reset to defaults)
- Memory mappings

## The fork-exec Pattern

The idiom for launching a new program is always `fork()` followed by `exec()` in the child:

```c
pid_t pid = fork();
if (pid == 0) {
    // Child: optionally set up redirections, close fds, etc.
    execvp("ls", (char *[]){"ls", "-la", NULL});
    _exit(1);   // exec failed
} else {
    // Parent: wait for child
    int status;
    waitpid(pid, &status, 0);
}
```

This separation gives the child a window between `fork()` and `exec()` to configure its environment — redirect stdin/stdout, close inherited fds, set the process group, etc. — before loading the target program.

## The Process Tree

Every process has a parent, forming a tree rooted at **PID 1** (init / systemd on Linux, launchd on macOS):

```
PID 1 (systemd)
├── PID 512 (sshd)
│   └── PID 1043 (bash)
│       ├── PID 2201 (vim)
│       └── PID 2315 (gcc)
│           └── PID 2316 (as)   ← assembler subprocess
└── PID 601 (cron)
    └── PID 1877 (backup.sh)
```

```bash
# View the process tree on Linux
pstree -p

# Or using ps
ps -eo pid,ppid,cmd --forest
```

## Windows: CreateProcess()

Windows does not have separate `fork()`/`exec()`. Instead, `CreateProcess()` combines both steps: it creates a new process and loads the specified executable in a single call. This is conceptually cleaner but less flexible for the shell-style fd-rearrangement tricks Unix programmers rely on.

## Common Pitfalls

- **Both parent and child run after fork**: A common mistake is forgetting the child continues from the line after `fork()`. Always check the return value.
- **File descriptors are shared after fork**: The parent and child share the same file offset for open files. Writing from both without synchronisation produces interleaved output.
- **exec() failure is silent if not checked**: `execvp` only returns on failure. Always handle it with `perror`/`_exit`.
- **Use `_exit()` not `exit()` in the child before exec**: `exit()` flushes stdio buffers that were duplicated from the parent, potentially causing double-flush corruption.

> **Interview answer:** `fork()` creates a child process as a copy-on-write clone of the parent; `exec()` replaces the calling process's address space with a new program while preserving the PID. Together they implement the Unix model of spawning new programs — the child has a window between fork and exec to configure I/O redirections before loading the target binary.
