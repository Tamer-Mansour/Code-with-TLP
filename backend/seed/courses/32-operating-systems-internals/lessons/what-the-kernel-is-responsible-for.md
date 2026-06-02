# What the Kernel Is Responsible For

The kernel is the core of an operating system — the privileged software layer that sits directly above the hardware and below every user-space application. It is always resident in memory and executes in a special CPU mode (ring 0 on x86, EL1/EL2 on ARM) that grants it unrestricted access to hardware resources.

## Core Responsibilities

The kernel has five primary jobs:

- **Process management** — creating, scheduling, suspending, and terminating processes and threads.
- **Memory management** — allocating virtual address spaces, managing page tables, handling page faults, and enforcing protection boundaries.
- **Device I/O** — providing a uniform abstraction over diverse hardware through device drivers.
- **File system** — translating file paths into disk blocks and managing persistent storage.
- **Inter-process communication (IPC)** — offering pipes, sockets, shared memory, and signals so processes can coordinate.

## Kernel Mode vs User Mode

Modern CPUs enforce a privilege boundary enforced in hardware:

| Mode | Also called | Can execute | Can access |
|------|-------------|-------------|------------|
| Kernel mode | Ring 0, supervisor | Any instruction | All memory, all I/O ports |
| User mode | Ring 3, unprivileged | Safe subset | Own virtual address space only |

When a user program needs a kernel service it issues a **system call** (e.g., `read()`, `fork()`). The CPU switches to kernel mode, executes the kernel handler, then returns to user mode. This boundary is what prevents a buggy app from corrupting kernel memory.

```c
// User-space view: a simple read() system call
ssize_t n = read(fd, buf, 4096);

// Under the hood (x86-64 Linux):
// 1. Arguments placed in rdi, rsi, rdx
// 2. syscall number (0 for read) placed in rax
// 3. "syscall" instruction triggers privilege switch
// 4. Kernel sys_read() executes
// 5. Return value in rax, mode switches back
```

## Interrupt Handling

The kernel is also the system's interrupt handler. When a timer fires, a disk completes a transfer, or a network packet arrives, the CPU jumps to a kernel **interrupt service routine (ISR)**. The kernel must handle these events quickly and atomically, which is why kernel code must be extremely careful about concurrency.

## The Dual Role: Policy vs Mechanism

A classic OS design principle separates mechanism (how to do something) from policy (when or for whom to do it):

- **Mechanism** lives in the kernel: "I can switch the running process."
- **Policy** can live in user space: "Switch to the highest-priority ready thread."

Microkernels take this furthest by pushing policy out of the kernel entirely. Monolithic kernels bundle both together for performance.

## Common Pitfall

Developers sometimes confuse the kernel with the entire OS. The OS includes the kernel, standard libraries (`libc`), shells, and system daemons. The kernel is only the privileged core.

> **Interview answer:** "The kernel manages CPU scheduling, virtual memory, device drivers, the file system, and IPC, all while enforcing the user/kernel privilege boundary via hardware-supported CPU modes."

## What Happens at Boot

```
Power on
  -> BIOS/UEFI (hardware init)
  -> Bootloader (GRUB loads kernel image)
  -> Kernel startup (initializes memory, interrupts, drivers)
  -> PID 1 (systemd/init) — first user-space process
  -> Remaining user services start
```

The kernel initializes in kernel mode, sets up page tables, registers interrupt vectors, and only then spawns the first user-space process. From that point on, every transition between user and kernel mode goes through the controlled system call or interrupt interface.
