# User Mode (U-Mode)

User Mode is the lowest privilege level in RISC-V. It is where application code runs — web servers, compilers, games, and every program an end user launches. U-Mode is intentionally limited: it cannot reconfigure hardware, cannot read kernel memory, and cannot execute privileged instructions.

## What U-Mode Can and Cannot Do

| Capability | U-Mode |
|---|---|
| Arithmetic, logic, branches | Yes |
| Memory load/store (within mapped pages) | Yes |
| Read/write any CSR | No |
| Execute `mret`, `sret` | No |
| Access kernel virtual addresses | No |
| Issue `ecall` to request OS services | Yes |

Attempting any forbidden operation raises an **illegal instruction** or **access fault** exception, which the kernel catches and typically converts to a signal (e.g., `SIGSEGV`, `SIGILL`).

## The Principle of Least Privilege in Practice

Restricting user code is not merely defensive — it is architecturally enabling. Because U-Mode code can only hurt itself, the OS can:

- **Run processes concurrently** without one corrupting another.
- **Kill a misbehaving process** without destabilizing the kernel.
- **Enforce resource quotas** — memory, CPU time, file descriptors — at the hardware boundary.

## How U-Mode Interacts with the Rest of the System

U-Mode programs interact with hardware indirectly, through a layered call chain:

```
User Program (U-Mode)
    │  ecall (syscall number in a7)
    ▼
OS Kernel (S-Mode)
    │  sbi_call (if hardware access needed)
    ▼
Firmware / OpenSBI (M-Mode)
    │  reads/writes hardware registers
    ▼
Physical hardware
```

The only intentional entry point from U-Mode into the kernel is the `ecall` instruction. Everything else that causes a privilege transition from U-Mode (a page fault, an illegal instruction, a timer interrupt) is an exception — not a requested service.

## The U-Mode Address Space

When the kernel runs a process, it sets `satp` to point at that process's page table and switches to U-Mode via `sret`. From that moment, the virtual address space the CPU sees is entirely dictated by the kernel-managed page table:

```
Virtual Address Space (Sv39 example)
┌────────────────────────┐ 0xFFFF_FFFF_FFFF_FFFF
│  Kernel (not accessible│
│  from U-Mode)          │
├────────────────────────┤ 0x0000_003F_FFFF_FFFF  (Sv39 top)
│  User stack            │
│  ...                   │
│  User heap             │
│  User text/data        │
└────────────────────────┘ 0x0000_0000_0000_0000
```

Kernel pages are mapped in the upper half but marked supervisor-only. Any U-Mode load or store to a supervisor-only page raises a page fault.

## A Simple U-Mode Program Issuing a Syscall

In RISC-V Linux, the calling convention for system calls matches the integer ABI:

```asm
# write(fd=1, buf, len)   — syscall 64 on RISC-V Linux
li    a7, 64          # sys_write
li    a0, 1           # fd = stdout
la    a1, message     # buffer address
li    a2, 13          # length
ecall                 # trap into kernel (S-Mode)
# return value is in a0 (bytes written, or -errno)
```

The kernel reads `a7` to identify the system call, performs the I/O using its own mappings, and returns the result in `a0` before issuing `sret` back to U-Mode.

## Common Pitfall

Developers porting bare-metal M-Mode code to a Linux environment sometimes try to read CSRs directly (e.g., `csrr t0, cycle` for performance measurement). On Linux, user access to `cycle` is only permitted when the kernel sets the `scounteren` bits. Without it, the instruction traps. Use `clock_gettime()` or `/proc/cpuinfo` instead.

## Worked Example: Detecting U-Mode at Runtime

Firmware or OS code that can run at multiple privilege levels sometimes needs to know the current mode. There is no direct instruction to query privilege level from U-Mode — the very attempt would cause a trap. This is intentional: privilege level is not a secret, but it is read-only hardware state invisible to user code.

```c
// U-Mode code: detect privilege indirectly by trying a CSR read
// (In production, just use uname() or a platform ABI)
#include <signal.h>
#include <setjmp.h>

static jmp_buf env;
static void sigill_handler(int s) { longjmp(env, 1); }

int running_privileged(void) {
    signal(SIGILL, sigill_handler);
    if (setjmp(env)) return 0;         // got SIGILL → U-Mode
    asm volatile("csrr t0, mstatus");  // triggers SIGILL in U-Mode
    return 1;
}
```

> **Interview answer:** User Mode is the lowest RISC-V privilege level where application code runs; it cannot access CSRs or kernel memory, and must use the ecall instruction to request any privileged operation from the operating system kernel.
