# User Mode vs Kernel Mode: What's the Difference?

Every modern CPU runs code at one of two privilege levels at any given moment: **user mode** or **kernel mode**. This distinction is the cornerstone of operating system security and stability. Without it, any buggy or malicious program could crash the entire machine or steal data from another process.

## The Core Idea

Think of it like a hospital. Patients (user programs) can walk the halls and use the cafeteria, but they cannot enter the surgery suite or access medical records directly. Doctors (the kernel) have unrestricted access to everything. The hospital enforces these rules — patients cannot simply walk past the locked doors.

Your CPU enforces the same idea in hardware.

| Aspect | User Mode | Kernel Mode |
|---|---|---|
| Also called | Ring 3, unprivileged | Ring 0, privileged, supervisor mode |
| Memory access | Own virtual address space only | All physical and virtual memory |
| I/O access | Prohibited (must ask kernel) | Direct hardware I/O permitted |
| Restricted instructions | Blocked — cause a trap | All instructions available |
| Crash impact | Only the process crashes | Entire system can crash (kernel panic) |

## Why Two Modes Exist

When you run a web browser, you do not want it able to:

- Read another process's memory (steal passwords from a password manager)
- Write directly to disk (bypass file permission checks)
- Disable interrupts (freeze the machine)
- Reprogram the CPU's memory map (escape its own address space)

User mode makes all of these physically impossible. The CPU hardware refuses to execute the relevant instructions and instead **traps** — jumping to a kernel handler that decides what to do (usually: terminate the offending process).

## What Happens in Each Mode

**User mode code** runs your application logic. It can do arithmetic, call library functions, allocate heap memory (which the C runtime manages in user space), and make **system calls** to request kernel services.

**Kernel mode code** runs the OS itself: scheduling, memory management, device drivers, file systems, and network stacks. The kernel is trusted; it can do anything the hardware permits.

```c
// This runs in user mode — reading memory you own
int arr[10];
arr[5] = 42;  // Fine: your own stack memory

// This is a system call — crosses into kernel mode
int fd = open("/etc/passwd", O_RDONLY);  // kernel does the real work
```

## The Mode Bit

The current privilege level is tracked by a single flag in a CPU status register. On x86-64 this lives in the **CPL (Current Privilege Level)** field of the `CS` (code segment) register — 2 bits, value 0 for kernel, 3 for user. The CPU checks this flag on every privileged operation.

You cannot change this bit yourself from user mode. Only specific CPU mechanisms (system calls, interrupts, exceptions) can change it — and those mechanisms are controlled by the kernel.

## Common Pitfalls

- **Confusing mode with scheduling**: Being in kernel mode does not mean you are "the OS". Your thread can enter kernel mode (via a syscall), do work there, and return — it is still your process's thread, just temporarily running privileged code.
- **Thinking kernel mode = infinite power**: Kernel code can still crash (kernel panic / blue screen). The mode just removes hardware restrictions; buggy code is still buggy.
- **Assuming context switches require kernel mode**: A mode switch (user → kernel) and a context switch (process A → process B) are separate events covered in a later lesson.

## Interview Answer

> **Q: What is the difference between user mode and kernel mode?**
>
> **Interview answer:** User mode restricts code to its own address space and blocks privileged CPU instructions. Kernel mode has unrestricted access to hardware and memory. The CPU enforces the boundary in hardware — a user-mode program that attempts a privileged operation triggers a trap into the kernel rather than executing the instruction.
