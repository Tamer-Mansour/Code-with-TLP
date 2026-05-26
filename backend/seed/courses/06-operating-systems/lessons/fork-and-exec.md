# fork() and exec(): Creating Processes

Unix systems use a two-step idiom to launch new programs: **fork** to duplicate the current process, then **exec** to replace the duplicate's image with a new program. This separation of concerns — create vs. load — is elegant, powerful, and used by every shell, server daemon, and runtime environment on Unix.

## fork(): Cloning a Process

`fork()` creates an exact copy of the calling process. The copy is called the **child**; the original is the **parent**. After `fork()` returns, two processes are running the same code from the same instruction.

```python
import os

pid = os.fork()          # Both parent and child continue from HERE

if pid == 0:
    print(f"I am the CHILD: my PID={os.getpid()}, parent={os.getppid()}")
    # The child does its work here
    os._exit(0)          # Exit child without flushing stdio buffers
else:
    print(f"I am the PARENT: my PID={os.getpid()}, child PID={pid}")
    status = os.wait()   # Reap the child — prevents zombie
    print(f"Child exited with status {status[1] >> 8}")
```

After `fork()`:
- Both processes are **identical** in code, data, open files, heap, stack, and environment.
- The **return value** distinguishes them: child receives 0; parent receives the child's PID (> 0). On error, parent receives -1.
- The child gets a **new PID** and a new PCB; all other state is a copy.
- Open file descriptors are **shared** — both processes have file descriptors pointing to the same underlying `struct file` objects with the same offsets.

### What Happens Inside fork()

```
parent process:
  1. Allocate new task_struct (PCB) for child
  2. Copy parent's page table entries (all marked COW, read-only)
  3. Copy file descriptor table (both share same file objects)
  4. Copy signal handlers, namespace references
  5. Assign new PID
  6. Add child to the scheduler's run queue
  7. Return child PID to parent thread

child process (runs from the same point):
  7. Return 0 to child thread
```

### Copy-on-Write (COW)

Copying gigabytes of memory on every `fork()` would be catastrophically slow. Linux uses **copy-on-write**: the parent and child initially share the same physical pages, marked read-only. The OS only copies a physical page when one process tries to **write** to it:

```
fork() called:
  Parent VA 0x1000 → PA 0xA000  [COW: read-only in both PTEs]
  Child  VA 0x1000 → PA 0xA000  [COW: read-only in both PTEs]

Child tries to write to VA 0x1000:
  → CPU raises a write-protection fault
  → OS allocates a new physical frame: 0xB000
  → OS copies 0xA000 → 0xB000
  → Child PTE: VA 0x1000 → PA 0xB000  [now writable]
  → Parent PTE: VA 0x1000 → PA 0xA000 [now writable again]
  → Fault resolved, write proceeds
```

This makes `fork()` followed immediately by `exec()` essentially free in terms of memory — `exec` discards the address space before any COW copies need to happen.

**Real-world impact:** A web server like Apache (pre-forking model) spawns worker processes with `fork()`. If the process is 500 MB (loaded modules, config), without COW each fork would need 500 MB of RAM. With COW, all workers share the read-only pages (code, read-only data) — only their stack and heap are private.

## exec(): Replacing the Process Image

`exec()` (actually a family of C functions: `execl`, `execv`, `execvp`, `execle`, `execve`) **replaces** the current process's address space, registers, and program counter with a new program loaded from disk. The PID stays the same; only the content changes.

```python
import os

pid = os.fork()
if pid == 0:
    # Child: replace ourselves with the `ls` binary
    os.execvp("ls", ["ls", "-la", "/tmp"])
    # If execvp() returns, it failed — exec never returns on success
    print("ERROR: exec failed", file=os.sys.stderr)
    os._exit(1)
else:
    os.wait()    # Wait for the child (ls) to finish
```

After a successful `exec`:
- The code segment is replaced with the new binary's `.text`.
- All data, heap, and stack are replaced.
- Open file descriptors survive **unless** marked with `O_CLOEXEC` (close-on-exec).
- Signal handlers are reset to `SIG_DFL` (default).
- Memory mappings (`mmap`) are discarded.
- The PID, PPID, and process group ID are unchanged.

### Why File Descriptors Survive

This is intentional. A shell sets up pipes before `exec`ing a command:

```bash
ls | wc -l
```

```
Shell (bash):
  1. pipe(pipefd)     → pipefd[0]=read end, pipefd[1]=write end
  2. fork() → child_ls
  3. child_ls: dup2(pipefd[1], STDOUT_FILENO)  # redirect stdout to pipe write end
               close(pipefd[0]); close(pipefd[1])
               exec("ls", ...)
               (ls writes to stdout → goes to pipe)
  4. fork() → child_wc
  5. child_wc: dup2(pipefd[0], STDIN_FILENO)   # redirect stdin to pipe read end
               close(pipefd[0]); close(pipefd[1])
               exec("wc", "-l", ...)
               (wc reads from stdin → reads from pipe)
  6. parent: close both pipefd ends, wait for both children
```

The file descriptors set up by `dup2()` survive `exec()`, allowing the pipe connection to remain intact.

## The fork/exec Pattern in a Shell

Every command you type in a shell goes through fork+exec:

```
User types: $ python3 script.py arg1

Shell (bash):
1. Tokenize: ["python3", "script.py", "arg1"]
2. fork()  → creates child bash process (PID 8921)
3. Child 8921:
   a. Set up any redirections (dup2 for < > |)
   b. execvp("python3", ["python3", "script.py", "arg1"])
      → OS loads python3 binary, replacing child 8921's address space
      → python3 runs, processes script.py
4. Parent bash: wait(8921) → blocks until python3 exits
5. Prompt returns
```

The separation allows the shell to set up redirections, change the working directory, and modify environment variables (in the child only) before `exec` — without affecting the parent shell.

## Process Hierarchy (The Process Tree)

Every process on Unix has a parent, forming a tree rooted at **PID 1** (`systemd` on modern Linux, `launchd` on macOS, or `init` on older systems):

```
PID 1   systemd
 ├── PID 231  sshd              ← listens for SSH connections
 │    └── PID 891  sshd         ← session handler for one user
 │         └── PID 892  bash    ← login shell
 │              └── PID 1047  python3 script.py
 ├── PID 312  nginx             ← master process
 │    ├── PID 313  nginx worker
 │    └── PID 314  nginx worker
 └── PID 401  cron
```

```bash
pstree -p   # Show full process tree with PIDs on Linux
```

If a parent exits before its children, the children are **reparented** to PID 1. systemd periodically calls `wait()` to reap these orphans.

## Zombies and Orphans

| Situation | Name | Effect |
|-----------|------|--------|
| Child exits; parent hasn't called `wait()` | **Zombie** | PCB stays in the process table; only the exit code is kept; occupies a PID slot |
| Parent exits before child | **Orphan** | Reparented to PID 1; eventually reaped |

A zombie is harmless memory-wise — only the PID and exit status are kept. But a server that forks thousands of children and never calls `wait()` will exhaust the PID namespace (32,768 by default on Linux), preventing any new processes from being created.

**Fix:** Use `SIGCHLD` signal handler to call `waitpid(-1, WNOHANG)` — reap all available children without blocking.

```python
import os, signal

def reap_children(signum, frame):
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
        except ChildProcessError:
            break

signal.signal(signal.SIGCHLD, reap_children)
```

## posix_spawn: A More Efficient Alternative

`posix_spawn()` combines fork+exec into a single call, avoiding the full process duplication on platforms where fork is expensive (e.g., embedded systems, or Solaris without COW). On Linux with COW, fork+exec is already fast, but `posix_spawn` is the POSIX standard way to launch processes from C.

## vfork: Ultra-Lightweight (Historical)

`vfork()` was an older optimization for the fork+exec pattern: the child borrows the parent's address space without copying (no COW setup). The parent is **suspended** until the child calls exec or exits. Dangerous and mostly superseded by COW fork, but still available in glibc for compatibility.

## Key Takeaways

- **`fork()`** clones the calling process; child receives return value 0, parent receives child PID.
- **Copy-on-write** makes `fork()` fast — physical pages are only copied when written, not on fork.
- **`exec()`** replaces the current process's code, data, and stack with a new program; the PID is preserved.
- Open file descriptors survive `exec()` (unless `O_CLOEXEC`) — used by shells to set up pipes and redirections.
- Every command in a shell is: fork a child → set up redirections → exec the command binary → parent waits.
- A child that exits before `wait()` is called becomes a **zombie** until reaped; a child whose parent exits becomes an **orphan** and is reparented to PID 1.
