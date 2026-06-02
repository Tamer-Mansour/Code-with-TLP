# Exokernels and Unikernels

Beyond the monolithic/microkernel axis, two more radical designs challenge the traditional OS abstraction: **exokernels** and **unikernels**. Both question whether the kernel should provide rich abstractions at all.

## Exokernels

The exokernel philosophy (MIT, 1995 — Engler, Kaashoek, O'Toole) argues that traditional OS abstractions (processes, virtual memory, file systems) are **too rigid**. A general-purpose virtual memory system cannot be optimal for every workload — a database wants to manage its own buffer cache; a web server wants to control how its connections are scheduled.

The solution: let the kernel do **only one thing** — securely multiplex raw hardware resources among applications.

```
+----------------------------------------------+
|  App A                     App B   [User]     |
|  +----------------+        +----------------+ |
|  | LibOS A        |        | LibOS B        | |
|  | (its own VM,   |        | (different FS, | |
|  |  FS, scheduler)|        |  scheduling)   | |
|  +----------------+        +----------------+ |
+----------------------------------------------+
|  Exokernel: secure binding + resource alloc  |
+----------------------------------------------+
|  Hardware                                     |
+----------------------------------------------+
```

Each application links a **library OS (LibOS)** that implements whatever abstractions it needs. The exokernel guarantees only:

- **Secure binding** — only the owner of a resource can use it.
- **Visible resource revocation** — the app is notified before a resource is reclaimed.
- **Abort protocol** — the kernel can forcibly reclaim resources if necessary.

**Advantage:** Applications can tune every OS abstraction for their specific workload. A database can implement its own page replacement policy without patching the kernel.

**Disadvantage:** Every application (or every LibOS) reimplements security-sensitive logic. This is complex and error-prone. Exokernels remain mostly a research design; Aegis and XoK are the notable prototypes.

## Unikernels

A **unikernel** takes the opposite approach from generality: instead of letting every app have its own OS, you compile a single application together with only the OS libraries it needs into a single-address-space image that runs directly on a hypervisor or bare metal.

```
Traditional VM stack:           Unikernel stack:
+--------------------+          +--------------------+
|  Application       |          |  App + LibOS (1 AS)|
+--------------------+          +--------------------+
|  Libc, runtime     |          |  Hypervisor / HW   |
+--------------------+          +--------------------+
|  Guest OS (Linux)  |
+--------------------+
|  Hypervisor        |
+--------------------+
```

**Examples:** MirageOS (OCaml), IncludeOS (C++), Unikraft, OSv.

**Advantages:**
- **Tiny footprint** — a MirageOS DNS server can be under 2 MB; a full Linux VM is hundreds of MB.
- **Fast boot** — milliseconds vs seconds.
- **Reduced attack surface** — no shell, no unused drivers, no multi-user support.
- **No user/kernel mode overhead** — everything is trusted (one address space).

**Disadvantages:**
- **Single application only** — you cannot run two workloads in the same unikernel instance.
- **No memory isolation** — a bug in library code crashes the whole "OS".
- **Toolchain complexity** — porting existing software requires rewriting POSIX-dependent code.
- **Limited debugging** — traditional tools (gdb, strace) do not work the same way.

## Comparing the Design Space

| Design | Kernel role | Address spaces | Abstraction owner | Key use case |
|--------|-------------|---------------|-------------------|--------------|
| Monolithic | Full OS | Many (user/kernel) | Kernel | General-purpose servers |
| Microkernel | IPC + scheduling | Many + servers | User-space servers | Safety-critical, embedded |
| Exokernel | Secure multiplexing | Many | Application LibOS | Research, extreme tuning |
| Unikernel | None (hypervisor) | One | Application | Cloud functions, IoT |

## Unikernels and the Cloud

Unikernels fit naturally into function-as-a-service (FaaS) and microservice deployments where:
- Each function is a single-purpose workload.
- Cold start latency matters.
- Security through isolation is provided by the hypervisor, not the guest OS.

Projects like **Unikraft** and AWS Firecracker (a microVM manager, not a unikernel, but similar philosophy) are bringing these ideas into production.

> **Interview answer:** "An exokernel securely multiplexes raw hardware and delegates all abstractions to per-application library OSes; a unikernel compiles a single application with only the OS libraries it needs into one address space, trading generality and isolation for tiny size and fast boot."
