# Process Lifecycle: fork, exec, and exit

Every program you run goes through a well-defined lifecycle: it is created, it executes, and it terminates. Understanding this lifecycle at the system call level is a core interview expectation for systems and OS roles.

## What Is a Process?

A process is an instance of a running program. It consists of:

- **Text segment** — the executable code (read-only).
- **Data segment** — global and static variables.
- **Heap** — dynamically allocated memory (`new`, `malloc`).
- **Stack** — local variables and call frames.
- **Kernel metadata** — PID, file descriptor table, signal handlers, scheduling info.

The OS tracks every process with a **Process Control Block (PCB)**, which holds all the state the kernel needs to pause and resume the process.

## Creating a Process: `fork()`

`fork()` is the POSIX system call that creates a new process by duplicating the calling process.

```cpp
#include <unistd.h>
#include <sys/wait.h>
#include <cstdio>

int main() {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        return 1;
    } else if (pid == 0) {
        // Child process
        printf("Child PID: %d\n", getpid());
    } else {
        // Parent process — pid is the child's PID
        printf("Parent PID: %d, Child PID: %d\n", getpid(), pid);
        wait(nullptr);  // reap the child
    }
    return 0;
}
```

**Key facts about `fork()`:**

- Returns **0** in the child, **child's PID** in the parent, **-1** on error.
- The child receives a **copy** of the parent's address space (copy-on-write in modern kernels).
- File descriptors are inherited and shared.
- After `fork()`, parent and child run **concurrently** — order is non-deterministic.

> **Interview answer:** `fork()` duplicates the calling process; the parent gets the child's PID, the child gets 0. Both then run independently from that point.

## Replacing the Process Image: `exec()`

`exec()` is a family of calls (`execve`, `execvp`, `execl`, …) that **replace** the current process image with a new program. The PID stays the same but everything else changes.

```cpp
#include <unistd.h>

int main() {
    char* args[] = {(char*)"/bin/ls", (char*)"-l", nullptr};
    execvp("/bin/ls", args);
    // Code here is never reached if execvp succeeds
    perror("execvp failed");
    return 1;
}
```

- `exec()` **never returns** on success — the new program takes over.
- Open file descriptors survive unless marked `O_CLOEXEC`.
- Signal dispositions are reset to defaults.

The classic Unix shell pattern is **fork + exec**: fork a child, then exec the desired command inside the child, while the parent waits.

## Terminating a Process: `exit()` and `_exit()`

```cpp
#include <cstdlib>

// Flush stdio buffers, run atexit handlers, then terminate
exit(0);

// Immediately terminate — no cleanup (use in child after fork)
_exit(0);
```

- `exit()` flushes C stdio buffers and runs `atexit()` handlers.
- `_exit()` goes straight to the kernel — preferred in the child after `fork()` to avoid double-flushing the parent's buffers.

## Zombie and Orphan Processes

| State | Description | Fix |
|---|---|---|
| **Zombie** | Child exited but parent hasn't called `wait()` | Parent must call `wait()` / `waitpid()` |
| **Orphan** | Parent exited before child | Adopted by `init` (PID 1) automatically |

A zombie holds a PCB slot until the parent reaps it. Accumulating many zombies exhausts the PID table.

## Worked Example: Shell-Style Command Execution

```cpp
pid_t pid = fork();
if (pid == 0) {
    execvp(argv[0], argv);  // child becomes the command
    _exit(127);             // exec failed
}
int status;
waitpid(pid, &status, 0);   // parent waits
if (WIFEXITED(status))
    printf("exited with %d\n", WEXITSTATUS(status));
```

## Common Pitfalls

- Forgetting `wait()` creates zombies.
- Using `exit()` instead of `_exit()` in the child can flush the parent's stdio buffers.
- After `fork()`, both processes share the same random seed — re-seed if using random numbers.
- File locks and mutexes are not inherited safely across `fork()` in multi-threaded programs.
