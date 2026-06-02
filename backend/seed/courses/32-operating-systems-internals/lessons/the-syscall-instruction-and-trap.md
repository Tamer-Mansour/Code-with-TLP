# The syscall/trap Instruction and the Dispatch Table

The CPU provides dedicated hardware support for entering the kernel safely. Understanding that mechanism — and how the kernel routes each call — is essential for writing low-level code and for systems design interviews.

## Two Entry Mechanisms on x86

### Legacy: `int 0x80` (32-bit Linux)

The old approach used a software interrupt. `int 0x80` triggers interrupt vector 0x80, which the kernel registers as its syscall gate. The CPU saves registers, looks up the interrupt descriptor table (IDT), and jumps to the handler.

Problems: IDT lookup is slow; interrupts have overhead (IRET is more expensive than SYSRET).

### Modern: `syscall` / `sysret` (64-bit)

Introduced in AMD64 and Intel EM64T. The `syscall` instruction uses Model-Specific Registers (MSRs) — CPU registers programmed at boot — instead of the IDT, eliminating the interrupt overhead.

Key MSRs:
| MSR | Purpose |
|---|---|
| `LSTAR` | Address of kernel syscall entry (`entry_SYSCALL_64`) |
| `STAR` | Kernel CS/SS segment selectors |
| `SFMASK` | Flags to clear on entry (e.g., IF to disable interrupts) |

```asm
; User space — issue a system call
mov rax, 1        ; syscall number (write)
mov rdi, 1        ; fd = stdout
lea rsi, [buf]    ; pointer to buffer
mov rdx, 6        ; byte count
syscall           ; trap to Ring 0

; On return: rax holds result (or negative errno)
```

## What `syscall` Does Atomically

1. Saves `rip` → `rcx` (return address).
2. Saves `rflags` → `r11`.
3. Masks flags specified in `SFMASK` (disables interrupts).
4. Loads CS/SS from `STAR`.
5. Loads new `rip` from `LSTAR` (jumps to kernel entry).
6. CPU is now in Ring 0 — no IDT lookup, no stack switch from the instruction itself.

Note: the kernel immediately swaps to the per-thread kernel stack using the `GSBASE` register which points to `cpu_entry_area`.

## The Dispatch Table

```c
// kernel/sys_ni.c + arch/x86/entry/syscall_64.c (simplified)
typedef long (*sys_call_ptr_t)(const struct pt_regs *);

const sys_call_ptr_t sys_call_table[__NR_syscall_max+1] = {
    [0]  = __x64_sys_read,
    [1]  = __x64_sys_write,
    [2]  = __x64_sys_open,
    [3]  = __x64_sys_close,
    // ... 300+ entries
};
```

The table is indexed by the number in `rax`. The kernel validates `rax < NR_syscalls` before indexing — an out-of-range number returns `-ENOSYS`.

## Syscall Numbers Are Architecture-Specific

| Syscall | x86-64 | x86 (32-bit) | ARM64 |
|---|---|---|---|
| `read` | 0 | 3 | 63 |
| `write` | 1 | 4 | 64 |
| `open` | 2 | 5 | 56 |
| `exit` | 60 | 1 | 93 |

This is why binaries are not portable across architectures even if the CPU could execute the instructions: the syscall numbers are baked in.

## Seccomp and the Table as a Security Surface

Linux's **seccomp** (secure computing mode) filter works by intercepting at the dispatch table. A BPF program inspects `rax` (and optionally arguments) before the kernel handler runs and can allow, kill, or trap the process.

```c
// Restricting syscalls with seccomp (simplified)
struct sock_filter filter[] = {
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write, 0, 1),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL),
};
```

Containers (Docker, Kubernetes) use seccomp profiles to limit which syscalls a container can make — this is a primary sandboxing mechanism.

## Common Pitfall

Developers sometimes confuse `syscall` (the instruction) with `syscall()` (a C library function in `<unistd.h>` that lets you invoke arbitrary syscalls by number). The C function is a convenience wrapper around the instruction; the instruction is the hardware mechanism.

**Interview answer:** The `syscall` instruction uses CPU MSRs to atomically save the return address, disable interrupts, and jump to the kernel entry point without an IDT lookup; the kernel then indexes `sys_call_table[rax]` to dispatch to the correct handler.
