# What an Operating System Does

An **operating system (OS)** is system software that manages hardware resources and provides a platform on which applications run. Without it, every program would need to speak directly to the CPU, memory controller, disk driver, and network card — an impossible burden on application developers and a security catastrophe.

## The Three Core Jobs of an OS

| Job | Meaning | Example |
|-----|---------|---------|
| **Resource management** | Allocates CPU time, RAM, and I/O bandwidth fairly among competing programs | Scheduler gives each browser tab CPU cycles |
| **Abstraction** | Hides hardware details behind clean interfaces | `open("file.txt")` works on any disk brand |
| **Protection** | Isolates processes so one crash does not corrupt another | Browser sandbox cannot write kernel memory |

## What an OS Is Not

An OS is *not* just a graphical desktop. The Linux kernel has no GUI at all. The kernel is the core of the OS; the desktop environment (GNOME, KDE, Windows Shell) is an application that runs *on top of* the kernel. Many production servers run Linux with zero graphical interface.

## OS as a Resource Arbitrator

Modern computers run dozens or hundreds of processes simultaneously on just a few CPU cores. The OS acts as an **arbitrator**, deciding:

- **Which process runs next and for how long** (CPU scheduling — covered in Module 4).
- **Where in physical memory each process's data lives** (memory management — Module 6).
- **Which process's disk request goes to the disk controller next** (I/O scheduling — Module 7).

Without this arbitration, processes would starve or collide. Consider the analogy of a single-lane bridge: cars (processes) need coordinated access, a traffic officer (the OS) enforces turn-taking, and nobody permanently blocks the bridge.

## OS as a Virtual Machine

From a programmer's perspective, the OS provides the illusion that each process owns:

- Its own **infinite CPU** — context switching is invisible; your program just "runs."
- Its own **contiguous private memory** — virtual address spaces hide physical layout.
- Its own **named files** on a persistent disk — the file system abstraction.
- Its own **network interfaces** — via socket abstractions.

These illusions dramatically simplify programming. You write `malloc(1024)` and the OS handles physical page mapping, fragmentation, and swap space transparently. You call `open("data.csv")` and the OS handles block device offsets, caches, and journaling.

## A Layered View of the System

The OS sits between hardware and applications in a clear layer cake:

```
┌───────────────────────────────────────┐
│         User Applications             │  ← your Python scripts, browsers
├───────────────────────────────────────┤
│     Standard Library (libc, glibc)    │  ← printf, malloc, pthread
├───────────────────────────────────────┤
│   System Call Interface (kernel ABI)  │  ← read, write, fork, mmap
├─────────────────────────────────────── ┤
│   OS Kernel                           │
│   ├── Process Scheduler               │
│   ├── Virtual Memory Manager          │
│   ├── File System (VFS + ext4/NTFS)   │
│   ├── Network Stack (TCP/IP)          │
│   └── Device Drivers                  │
├───────────────────────────────────────┤
│   Hardware Abstraction Layer (HAL)    │
├───────────────────────────────────────┤
│   Hardware: CPU, RAM, Disk, NIC       │
└───────────────────────────────────────┘
```

Each layer only communicates with the layer directly above or below it. This modularity is what lets Linux run on everything from a Raspberry Pi to a 10,000-core supercomputer without rewriting applications.

## Major OS Families

```
Operating Systems
├── Unix-like
│   ├── Linux (Android, most servers, embedded devices)
│   ├── macOS / iOS (Darwin kernel, BSD-derived)
│   └── FreeBSD, OpenBSD (internet infrastructure)
└── Windows NT family
    ├── Windows 10/11 (desktop)
    └── Windows Server
```

Each family makes different design trade-offs in modularity, security model, and scheduling policy, but all share the same conceptual responsibilities: resource management, abstraction, and protection.

## A Day in the Life of a System Call

When your Python script calls `print("hello")`, here is the complete chain of events:

```
Python          C Library          Kernel                 Hardware
───────         ─────────          ──────                 ────────
print("hello")
  │
  └─► sys.stdout.write()
           │
           └─► write(fd=1, buf, len=5)    [libc wrapper]
                     │
                     │  syscall instruction (rax=1 on Linux x86-64)
                     │  CPU → ring 0
                     │
                     └─► sys_write()
                               │
                               ├── validate fd 1 (stdout)
                               ├── locate terminal driver
                               ├── copy "hello" to terminal buffer
                               └── return bytes written (5)
                     │
                     │  iretq (return from syscall)
                     │  CPU → ring 3
                     ▼
           return 5
  ▲
  └─ Python continues
```

The entire round trip typically takes a few hundred nanoseconds — invisible to humans but significant when called millions of times per second. A tight loop calling `write()` one byte at a time can be 10–100× slower than buffered I/O because of this overhead.

## The OS on Real Systems

**Linux (server context):** The kernel processes each timer interrupt every 4 ms by default (250 Hz), running the scheduler to possibly preempt the current process. On an 8-core server with 200 active threads, the scheduler makes 2,000 decisions per second before even considering I/O events.

**Windows:** Uses a similar design but with a 15.6 ms default timer interval (64 Hz) on the desktop, prioritizing smooth GUI over throughput. The Windows kernel exposes the Win32 API (rather than raw syscall numbers) which has been stable across NT versions since 1993.

**macOS (XNU kernel):** Combines Mach microkernel concepts (message-passing, IPC) with a BSD personality for POSIX compatibility. The Mach layer handles VM and IPC; the BSD layer handles file systems and the syscall table visible to applications.

## Key Takeaways

- The OS manages CPU, memory, and I/O while providing clean abstractions to programs.
- The **kernel** is the core privileged component; user applications run outside it in a restricted ring.
- Every hardware interaction by user code goes through an OS-provided **system call** — a controlled boundary crossing.
- The illusion of a private, infinite machine is created entirely by the OS — virtual address spaces, time-sharing, and file system namespaces.
- Layering (hardware → HAL → kernel → libc → app) makes the system modular and portable.
- Real-world OSes (Linux, Windows, macOS) differ in kernel architecture but share the same conceptual roles.
