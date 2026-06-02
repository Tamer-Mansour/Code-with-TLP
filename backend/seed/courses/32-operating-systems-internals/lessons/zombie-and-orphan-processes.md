# Zombie and Orphan Processes Explained

Process creation creates a parent-child relationship. When that relationship breaks down — either because the child exits before the parent collects its status, or because the parent exits before the child — two special process conditions arise: **zombies** and **orphans**. Both are normal OS concepts, but uncontrolled accumulation of either is a sign of a bug.

## Zombie Processes

When a process calls `exit()`, the kernel **releases most of its resources** — its address space, open files, and page tables are freed. However, the **PCB is not freed**. Instead, the process enters the **Zombie** (Z) state and waits for its parent to call `wait()` or `waitpid()` to collect the **exit status**.

The zombie exists to answer one question: "How did my child exit, and with what code?"

```
Child calls exit(42)
       │
       ▼
 Resources freed (memory, fds, etc.)
 PCB kept in ZOMBIE state
 Parent is notified via SIGCHLD
       │
       ▼  (parent calls waitpid())
 Kernel returns exit status (42) to parent
 PCB fully deallocated  ← zombie gone
```

### Demonstrating a Zombie

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void) {
    pid_t pid = fork();
    if (pid == 0) {
        // Child exits immediately
        exit(0);
    }
    // Parent sleeps without calling wait() — child is now a zombie
    printf("Child PID %d is a zombie — check 'ps aux | grep Z'\n", pid);
    sleep(30);
    // After sleep, parent exits; zombie is reaped by init
    return 0;
}
```

```bash
# While the parent is sleeping, observe the zombie
ps aux | grep 'Z'
# or
ps -eo pid,stat,cmd | grep ' Z '
```

### Why Zombies Are Harmless (In Small Numbers)

A zombie holds only a PCB — a few hundred bytes. A single zombie does no harm. However, a server that `fork()`s thousands of children without calling `wait()` will accumulate thousands of zombies, **exhausting the PID namespace** (Linux default: 32,768 PIDs). At that point, no new processes can be created system-wide.

### Preventing Zombies

- **Call `wait()`/`waitpid()`** in the parent after each child exits.
- **Handle `SIGCHLD`**: Install a `SIGCHLD` handler that calls `waitpid(-1, NULL, WNOHANG)` in a loop to reap all available children without blocking.
- **Double-fork trick**: `fork()` → child `fork()`s a grandchild → child exits immediately → grandchild is orphaned and adopted by init. Init always reaps its children, so the grandchild can never become a zombie.

```c
// SIGCHLD handler: non-blocking reap
#include <sys/wait.h>
void sigchld_handler(int sig) {
    while (waitpid(-1, NULL, WNOHANG) > 0)
        ;  // reap all available zombies
}
```

## Orphan Processes

An **orphan** is a process whose parent has exited before it. The parent's exit means there is no process to call `wait()` for the orphan when it eventually finishes.

The kernel solves this automatically: when a parent exits, all of its children are **re-parented** to PID 1 (init/systemd on Linux). Init runs an eternal `wait()` loop, so it immediately reaps any orphan that exits, preventing zombie accumulation.

```
Parent exits while Child is still running
       │
       ▼
 Kernel detects: child's PPID's owner is gone
 Child's PPID → set to 1 (init)
       │
       ▼  (child later exits)
 Init calls wait() → child reaped cleanly
```

### Intentional Orphans: Daemon Processes

Daemons (background services like `sshd`, `nginx`) are deliberately orphaned. The standard daemonisation procedure is:

1. `fork()` — parent exits, shell returns control to the user.
2. Child calls `setsid()` — becomes session leader, detaches from the terminal.
3. Child is now an orphan adopted by init; it runs forever in the background.

## Side-by-Side Comparison

| | Zombie | Orphan |
|--|--------|--------|
| Who exited first? | Child | Parent |
| Is the process still running? | No (done, PCB kept) | Yes (still executing) |
| Danger | PID/PCB exhaustion | None (init adopts it) |
| Fix | Parent calls `wait()` | Automatic re-parenting |

## Common Pitfalls

- **"Killing a zombie with SIGKILL"**: SIGKILL cannot kill a zombie — it is already dead. Only the parent calling `wait()` (or the parent dying) removes it.
- **Orphan != zombie**: Orphans are still alive and doing work; zombies are finished but uncollected. Conflating them is a common interview mistake.
- **Long-lived daemons that fork without reaping**: A daemon that forks workers to handle requests must either reap them or install a SIGCHLD handler, or it will accumulate zombies over time.

> **Interview answer:** A zombie is a process that has exited but whose PCB is retained until the parent calls `wait()` to collect the exit status. An orphan is a process whose parent has exited; the kernel automatically re-parents it to init, which reaps it when it exits. Zombies are dangerous if they accumulate because they consume PID slots.
