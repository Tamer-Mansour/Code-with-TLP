# Monolithic vs Microkernel Architectures

Kernel architecture defines what code runs in privileged mode. Two philosophies dominate the landscape: **monolithic kernels**, which pack almost everything into kernel space, and **microkernels**, which keep the kernel minimal and push services into user space.

## Monolithic Kernel

In a monolithic kernel, all OS services — process scheduling, memory management, file systems, network stacks, and device drivers — execute in a single large binary in kernel mode.

```
+------------------------------------------------------+
|  Applications                              [User]    |
+------------------------------------------------------+
|  System call interface                               |
+------------------------------------------------------+
|  Scheduler | VM | VFS | TCP/IP | Drivers  [Kernel]  |
+------------------------------------------------------+
|  Hardware                                            |
+------------------------------------------------------+
```

**Examples:** Linux, FreeBSD, traditional UNIX (SVR4).

**Advantages:**
- **Performance** — no mode switches between subsystems; a scheduler can call into the file system directly.
- **Shared data structures** — subsystems share kernel memory, avoiding data copying.
- **Mature ecosystem** — decades of optimization; loadable kernel modules let drivers be added without recompiling.

**Disadvantages:**
- **Reliability** — a buggy driver runs in kernel mode; one null pointer dereference can crash the whole system.
- **Security surface** — a driver vulnerability gives an attacker full kernel privilege.
- **Maintainability** — millions of lines of tightly-coupled C; modifying one subsystem risks breaking another.

## Microkernel

A microkernel provides only the absolute minimum in kernel mode: address space management, thread scheduling, and basic IPC. Everything else — file servers, device drivers, network stacks — runs as isolated user-space servers.

```
+------------------------------------------------------+
|  Applications                              [User]    |
+------------------+-----------------------------------+
|  File Server     |  Device Driver  |  Network Server |
+------------------+-----------------------------------+
|  IPC | Scheduler | Address Space   [Microkernel]     |
+------------------------------------------------------+
|  Hardware                                            |
+------------------------------------------------------+
```

**Examples:** Mach (foundation of macOS/iOS kernel), L4, seL4, QNX.

**Advantages:**
- **Fault isolation** — a driver crash is contained; the server restarts without rebooting the system.
- **Security** — formal verification is feasible (seL4 is mathematically proven correct).
- **Flexibility** — multiple file systems or network stacks can coexist as servers.

**Disadvantages:**
- **IPC overhead** — every cross-service call is a message-passing round trip involving at least two mode switches.
- **Historical performance gap** — early microkernels (Mach) were significantly slower than monolithic kernels for this reason.
- **Complexity** — distributed architecture in user space; deadlocks between servers are harder to debug.

## Side-by-Side Comparison

| Property | Monolithic | Microkernel |
|----------|-----------|-------------|
| Code in kernel mode | All subsystems | IPC + scheduler + address spaces |
| Driver crash impact | System crash | Server restart |
| IPC cost | Near zero (function call) | High (mode switches + copy) |
| Formal verification | Impractical | Feasible (seL4) |
| Real-world examples | Linux, FreeBSD | QNX, seL4, Mach |
| Performance (typical) | Higher | Lower (but improving) |

## The Tanenbaum-Torvalds Debate (1992)

This debate is famous in OS history. Andrew Tanenbaum argued that Linux (monolithic) was obsolete design; Linus Torvalds countered that monolithic kernels with loadable modules offer practical performance and flexibility. Decades later, Linux dominates servers and mobile while microkernels dominate safety-critical and embedded systems (QNX in cars, seL4 in aerospace).

The lesson: architecture choice depends on the **threat model and performance requirements**, not ideology.

> **Interview answer:** "Monolithic kernels run all services in kernel mode for performance but sacrifice isolation; microkernels run only IPC and scheduling in kernel mode, gaining fault isolation and verifiability at the cost of IPC overhead."
