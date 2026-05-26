# Kernel Mode vs User Mode

Modern CPUs enforce a strict boundary between **privileged kernel code** and **unprivileged user code**. This hardware mechanism is the foundation of OS security and stability — without it, a buggy application could overwrite the OS itself.

## Privilege Rings

Intel and AMD x86-64 processors define four **privilege rings** (0–3), though most operating systems use only two:

```
Ring 0 — Kernel mode   (full hardware access: I/O ports, page tables, interrupts)
Ring 1 — (unused by most OSes)
Ring 2 — (unused by most OSes)
Ring 3 — User mode     (restricted: no direct hardware, no kernel memory)
```

ARM processors call these **Exception Levels**: EL0 (user) through EL3 (secure monitor). RISC-V uses Machine (M), Supervisor (S), and User (U) modes. The principle is identical across architectures: some instructions are privileged and cause a fault if executed at the wrong level.

## What Kernel Mode Can Do That User Mode Cannot

| Operation | User Mode | Kernel Mode |
|-----------|-----------|-------------|
| Read/write any physical address | No | Yes |
| Configure page tables | No | Yes |
| Enable/disable hardware interrupts | No | Yes |
| Execute privileged instructions (`HLT`, `LGDT`, `CLI`) | No | Yes |
| Access I/O ports directly | No | Yes |
| Load/store from the kernel's virtual address range | No | Yes |

A user-mode program that attempts to access kernel memory receives a **segmentation fault** (SIGSEGV on Linux) — the CPU raises a protection fault before any damage is done. The program is killed; the kernel survives.

## Why Two Modes?

Without the separation:

- A buggy app could overwrite the OS kernel itself, corrupting every other process.
- A malicious app could steal another process's memory (passwords, session tokens).
- A crashed app could set a spinlock inside the kernel, locking the system permanently.

The hardware enforces the boundary; no software instruction can bypass it. An attempted privilege escalation always traps to the kernel, which can terminate the offending process.

## The System Call Interface

The only legitimate way for user code to request privileged operations is the **system call** interface — a table of well-defined entry points into the kernel.

```
User Space                      Kernel Space
──────────────────────────────────────────────
  open("log.txt", O_RDONLY)
       │
       │ syscall instruction
       │ (rax = 2 for open on Linux x86-64)
       ▼
  [CPU switches to ring 0, loads kernel stack]
       │
       ▼
  sys_open() in kernel
       ├── check: does the process have permission?
       ├── resolve path through the VFS
       ├── allocate a file descriptor
       └── return fd (or -ENOENT / -EACCES)
       │
  [CPU returns to ring 3, restores user stack]
       ▼
  fd = 5  (or -1 on error)
```

On Linux x86-64, the `syscall` instruction stores the system call number in `rax` and arguments in `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`. Return value comes back in `rax`. The kernel's **system call table** (an array of function pointers) maps numbers to handler functions at kernel startup.

## Anatomy of a Mode Switch: Step by Step

When a user-space program issues `syscall`:

```
1. CPU saves rip (next user instruction) and rsp (user stack) internally
2. CPU loads new rip from MSR_LSTAR (kernel entry point, set at boot)
3. CPU loads new rsp from MSR_SYSCALL_MASK / kernel stack pointer
4. CPU atomically sets CPL (Current Privilege Level) from 3 → 0
5. Kernel handler runs in ring 0
   - Saves all user registers to the kernel stack
   - Dispatches to the correct syscall handler (via syscall_table[rax])
   - Handler executes (may block, may sleep)
   - Restores user registers from kernel stack
6. `sysretq` instruction: CPL 0 → 3, restores rip and rsp, user continues
```

The entire user → kernel → user round trip for a fast syscall (e.g., `getpid`) takes roughly 100–300 ns on modern hardware. A blocking syscall (e.g., `read` on a network socket) can take arbitrarily long.

## Three Triggers for Mode Switches

| Trigger | Direction | Example |
|---------|-----------|---------|
| **System call** | User → Kernel (deliberate) | `read()`, `write()`, `fork()` |
| **Exception / Fault** | User → Kernel (accidental) | Page fault, divide-by-zero, illegal instruction |
| **Hardware interrupt** | Any → Kernel (asynchronous) | Timer tick, keyboard press, NIC packet arrival |

After every mode switch, the kernel runs its handler and then decides whether to return to the *same* user process or to a *different* one (a context switch). The timer interrupt in particular is what enables preemptive multitasking.

## Monolithic vs. Microkernel vs. Hybrid

| Design | Where Drivers Run | Crash Impact | Example |
|--------|------------------|--------------|---------|
| **Monolithic kernel** | Ring 0 (fast, but a bad driver crashes the OS) | Kernel panic | Linux, Windows NT |
| **Microkernel** | Ring 3 (isolated user-space servers) | Only the driver restarts | MINIX 3, seL4, L4 |
| **Hybrid** | Mix: core in ring 0, some drivers in ring 3 | Better isolation than monolithic | macOS (XNU), Windows (user-mode drivers for some classes) |

Linux is monolithic but uses **loadable kernel modules (LKMs)** to add or remove drivers without rebooting (`insmod`/`rmmod`). A module crash still brings down the kernel — the isolation is organizational, not hardware-enforced. By contrast, seL4's microkernel proof guarantees functional correctness of the kernel itself.

## KPTI: Protecting Kernel Memory from User Space

The **Meltdown** CPU vulnerability (2018) allowed user-mode code to speculatively read kernel memory via side-channels. The OS response was **Kernel Page-Table Isolation (KPTI)**: the kernel's pages are completely unmapped from the user-mode page table. Every system call now requires loading a second, full page table — adding ~5–30% overhead on some workloads, but eliminating the attack surface.

KPTI illustrates that the user/kernel boundary is not just a software policy — it must be defended with hardware-enforced page table isolation.

## Practical Demonstration

On Linux you can see the current privilege level of a process indirectly:

```bash
# Count system calls made by a program
strace -c ls /tmp

# See mode switches per second system-wide
perf stat -e syscalls:sys_enter_read sleep 1
```

A typical interactive shell session makes hundreds of system calls per second (for prompt rendering, readline, tab completion). A CPU-bound numerical computation may make fewer than 10 per second.

## Key Takeaways

- CPUs enforce a hardware boundary between **kernel mode** (ring 0) and **user mode** (ring 3).
- User code cannot directly access hardware — it must request services via **system calls**, which are the OS's public API.
- Mode switches are triggered by system calls, exceptions (page faults, divide-by-zero), and hardware interrupts.
- The `syscall` instruction atomically changes the privilege level and jumps to a kernel entry point.
- Monolithic kernels run drivers in ring 0 for speed; microkernels run them in ring 3 for isolation.
- Modern vulnerabilities like Meltdown motivated **KPTI**, showing the boundary must be actively defended.
