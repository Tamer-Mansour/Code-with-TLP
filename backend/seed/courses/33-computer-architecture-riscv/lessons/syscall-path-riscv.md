# The System Call Path via ECALL

System calls are the controlled gateway from user-mode code into the kernel. On RISC-V this gateway is the `ecall` instruction — a single opcode that triggers a trap from the current privilege level to the next one up.

## Why ECALL Exists

User processes cannot directly execute privileged instructions or access kernel memory — the hardware will raise an illegal-instruction exception if they try. `ecall` is the safe, architecture-defined way for software to request OS services: file I/O, memory allocation, process creation, and more.

## The ECALL Instruction

`ecall` has no operands. Its behavior depends entirely on the current privilege level:

| Executing Mode | Trap Taken To |
|---------------|---------------|
| User (U)      | Supervisor (S) kernel — `scause = 8` |
| Supervisor (S) | Machine (M) firmware — `scause = 9` |
| Machine (M)   | (reserved / implementation defined) |

The OS identifies which system call is being requested by convention — Linux RISC-V uses `a7` to hold the syscall number, and `a0`–`a5` carry arguments. The return value is placed back in `a0` (with `a1` for a second return value on some ABIs).

## Step-by-Step: A Read() System Call

```c
// User program calls POSIX read()
ssize_t n = read(fd, buf, len);
```

The C library (glibc / musl) translates this into:

```asm
li   a7, 63        # syscall number for read (Linux RISC-V ABI)
mv   a0, fd        # first argument: file descriptor
mv   a1, buf       # second argument: buffer pointer
mv   a2, len       # third argument: byte count
ecall              # trap into the kernel
# on return, a0 holds bytes read or negative errno
```

**Inside the kernel, the full path is:**

1. `ecall` fires — hardware saves `pc` to `sepc`, sets `scause = 8`, switches to S-mode, jumps to `stvec`.
2. The assembly trap entry saves all 32 registers to the trapframe.
3. The C trap dispatcher reads `scause`, sees environment call from U-mode.
4. The syscall table is indexed by `a7` — the kernel calls `sys_read()`.
5. `sys_read()` validates the user pointer (ensures it maps to U-mode memory), copies data, and returns the byte count.
6. The return value is written to `trapframe->a0`.
7. The kernel increments `sepc` by 4 (to skip past the `ecall` instruction — without this, the process will loop forever re-executing `ecall`).
8. `sret` restores registers and resumes the user program.

## Validating User Pointers

A critical security step: the kernel must never dereference a raw user-space pointer without validation. An attacker can pass a pointer into kernel memory.

```c
// xv6-style copyin: safe copy from user virtual address
int copyin(pagetable_t pt, char *dst, uint64 srcva, uint64 len) {
    // walk the page table, check U-mode bit, then memcpy
}
```

RISC-V helps here: with the `SUM` bit (permit Supervisor User Memory access) in `sstatus` cleared, any kernel access to a page not marked user-accessible raises a page fault — hardware-enforced protection.

## Fast Path vs. Full Trap

Some OSes implement a vDSO (virtual dynamic shared object) — a small kernel-provided page mapped read-only into every process's address space containing code that can answer certain syscalls (like `clock_gettime`) without actually trapping. On RISC-V this avoids the full `ecall` overhead for performance-critical time queries.

## Common Pitfalls

- Forgetting to increment `sepc` by 4 after an `ecall` trap — causes infinite loop.
- Using `a0` as both the argument and the return register — the kernel must overwrite it carefully.
- Not checking that the user-provided pointer is within the U-mode address space before dereferencing it.

> **Interview answer:** `ecall` on RISC-V triggers a synchronous trap: the hardware saves the PC to `sepc`, sets `scause = 8` (U-mode env call), switches to S-mode, and jumps to `stvec`; the kernel reads the syscall number from `a7`, dispatches the handler, writes the result to `trapframe->a0`, increments `sepc` by 4, and uses `sret` to return.
