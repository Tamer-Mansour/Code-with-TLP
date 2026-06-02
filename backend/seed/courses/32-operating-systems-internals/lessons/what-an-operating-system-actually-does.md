# What an Operating System Actually Does

Most developers interact with an OS through shell commands or system calls without thinking deeply about what the OS is actually managing. This lesson gives a precise, hardware-grounded answer.

## The Core Definition

An **operating system** is software that:

1. **Abstracts** hardware into portable, convenient interfaces.
2. **Multiplexes** hardware resources among multiple concurrent users or processes.
3. **Protects** processes and the kernel from each other.

Everything else — file systems, networking stacks, device drivers, GUIs — builds on these three primitives.

## What the OS Manages

### CPU Time
The OS **scheduler** decides which process runs on which CPU core at any moment. Since there are far more runnable processes than cores, the scheduler rapidly switches between them (typically every 1–10 ms), creating the illusion of parallelism. Each switch is a **context switch** — saving the CPU register state of the outgoing process and restoring the register state of the incoming one.

### Physical Memory
Each process sees a large, contiguous, private **virtual address space** (e.g., 0 to 2⁴⁸ bytes on x86-64), but physical RAM is shared. The OS maintains **page tables** that translate virtual addresses to physical addresses. This gives each process isolation — writing to address 0x1000 in process A cannot affect process B's memory.

### Devices and I/O
A keyboard, disk, or network card is just registers and buffers on a bus. The OS provides **device drivers** — code that speaks the hardware protocol — and exposes a uniform interface (read, write, ioctl) to user programs. When a device has data ready, it signals the CPU with an **interrupt**, which the OS handles before returning to the interrupted process.

### Files and Persistent Storage
Disks store raw sectors. The OS **file system** layer organizes sectors into files, directories, and metadata, handles caching (page cache), and enforces permissions. A `read()` system call can be satisfied from cache without touching the disk at all.

### Security and Protection
User processes run in **ring 3** (unprivileged). Privileged CPU instructions and hardware registers are accessible only in **ring 0** (kernel mode). The OS enforces this boundary: a process cannot directly access another process's memory, cannot issue raw I/O, and cannot modify page tables — it must ask the OS via system calls.

## The System Call Interface

The only legal way for a user process to request OS services is a **system call**. On x86-64 Linux this is the `syscall` instruction:

```asm
; write(1, "hello\n", 6)  — Linux x86-64 ABI
mov rax, 1          ; syscall number: sys_write
mov rdi, 1          ; fd: stdout
lea rsi, [msg]      ; pointer to buffer
mov rdx, 6          ; byte count
syscall             ; trap into kernel (ring 0)
```

The `syscall` instruction switches the CPU to ring 0, saves user-mode register state, and jumps to the kernel's system call handler. The kernel validates arguments, performs the action, then returns to user mode via `sysret`.

## The Kernel vs User Space Split

```
User space (ring 3):    app A  │  app B  │  app C  │  libc
──────────────────────────────────────────────────────────
Kernel space (ring 0):  scheduler │ VM │ VFS │ drivers │ net
──────────────────────────────────────────────────────────
Hardware:               CPU │ RAM │ disk │ NIC │ GPU
```

Libraries like `libc` are *not* the OS — they are user-space wrappers that may call into the kernel via `syscall`. `printf` ultimately calls `write`, which is a syscall.

## Common Pitfalls

- Thinking the OS "runs alongside" programs — the OS runs *instead of* a program, briefly, on behalf of that program, when a syscall or interrupt occurs.
- Conflating kernel and OS — some embedded systems have no kernel at all; the "OS" is just a thin HAL. On desktop Linux, the kernel is the core; init, systemd, shell, and libc are in user space.
- Assuming system calls are cheap — a syscall crosses the user/kernel boundary, flushes parts of the pipeline and TLB, and may block. High-frequency calls (millions/sec) are a real bottleneck; that is why `io_uring` batches them.

> **Interview answer:** An operating system abstracts hardware (CPU, RAM, devices, disk) into portable interfaces, multiplexes those resources among concurrent processes using scheduling and virtual memory, and protects processes from each other by enforcing privilege rings. Processes access OS services only via system calls, which switch the CPU from ring 3 (user) to ring 0 (kernel).
