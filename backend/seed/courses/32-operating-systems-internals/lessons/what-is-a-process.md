# What Is a Process? The Program-in-Execution Abstraction

A **program** is a passive artifact — a file on disk containing instructions and data. A **process** is that program brought to life: an active instance that the operating system has loaded into memory, given a stack, a heap, and a program counter, and scheduled to run on the CPU.

The distinction matters because the same executable can spawn multiple processes simultaneously. Open two terminals and run the same Python script in each — you have one program, two processes, each with its own independent memory and execution state.

## What Makes a Process?

The OS uses the process abstraction to create the illusion that each program owns the entire machine. Each process gets:

- **Private virtual address space** — it sees a contiguous range of addresses from 0 to some maximum, even though physical RAM is shared with dozens of other processes.
- **At least one thread of control** — a sequence of instructions executing over time.
- **Kernel-managed metadata** — the OS tracks the process in a data structure called the Process Control Block (PCB).
- **Resources** — open file descriptors, network sockets, signal handlers, and more.

## Program vs. Process vs. Thread

| Concept | What it is | Owns memory? | Scheduled? |
|---------|-----------|--------------|-----------|
| Program | Binary on disk | No | No |
| Process | Running instance | Yes (virtual AS) | Yes |
| Thread | Execution stream inside a process | Shares process AS | Yes |

A process can contain many threads, all sharing the same address space but each with its own stack and register state.

## The Lifecycle at a Glance

When you run `./myapp`, the shell calls `fork()` to clone itself, then `exec()` to replace the clone's address space with `myapp`'s binary. The kernel:

1. Allocates a new PCB and assigns a unique **PID** (Process Identifier).
2. Sets up the virtual address space (text, data, heap, stack segments).
3. Initializes the program counter to the entry point (`_start` / `main`).
4. Places the process in the **Ready** queue.

The scheduler eventually picks it up, loads it onto a CPU, and execution begins.

## Why the Abstraction Matters

Before processes, programs ran bare-metal and could accidentally (or maliciously) overwrite each other's memory. The process abstraction enforces **isolation**: one process cannot read or write another's address space without explicit OS cooperation (e.g., shared memory or pipes).

It also enables **concurrency**: the OS switches the CPU rapidly among ready processes, giving each the illusion of dedicated hardware. This time-sharing is transparent to user programs.

## Worked Example: Observing Processes on Linux

```bash
# List all processes with PID, parent PID, and command
ps -eo pid,ppid,cmd --forest | head -20

# A process's virtual address space is visible in /proc
cat /proc/$$/maps | head -10
```

The `$$` shell variable holds the current shell's PID. The `/proc/<pid>/maps` file shows every region of the process's virtual address space — text, libraries, heap, stack — with permissions.

## Common Pitfalls

- **Confusing process and thread**: A process is the unit of resource ownership; a thread is the unit of execution. Threads within one process share heap and globals but have separate stacks.
- **Thinking PID is stable**: PIDs are reused after a process exits. Never cache a PID and assume the process is still the same one seconds later.
- **Forgetting the kernel is not a process**: The kernel runs in privileged mode and manages all processes, but it is not itself a user-space process.

> **Interview answer:** A process is a running instance of a program — it is the OS abstraction that bundles a virtual address space, at least one thread of execution, and a set of kernel-managed resources such as open files and signal handlers.
