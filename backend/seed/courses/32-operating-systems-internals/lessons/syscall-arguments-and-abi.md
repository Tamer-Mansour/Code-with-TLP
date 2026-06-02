# Passing Arguments: The System Call ABI

The Application Binary Interface (ABI) for system calls specifies exactly how arguments travel from user space into the kernel. This is lower-level than the C calling convention and differs between architectures and between 32-bit and 64-bit modes.

## Why a Separate ABI?

The C function-call ABI (e.g., System V AMD64 ABI) uses the stack for arguments beyond the sixth. System calls cannot use the user-space stack safely — the kernel runs on its own stack and cannot trust the user stack pointer. Therefore, **all syscall arguments go in registers**, and the number of arguments is capped at six.

## x86-64 Linux Syscall ABI

| Role | Register |
|---|---|
| Syscall number | `rax` |
| Argument 1 | `rdi` |
| Argument 2 | `rsi` |
| Argument 3 | `rdx` |
| Argument 4 | `r10` |
| Argument 5 | `r8` |
| Argument 6 | `r9` |
| Return value | `rax` |
| Saved by kernel | `rcx`, `r11` (clobbered by `syscall`) |

Note: argument 4 is `r10`, **not** `rcx`. This is because `syscall` clobbers `rcx` (it saves `rip` there), so `r10` takes over as arg 4 in the syscall ABI even though `rcx` is arg 4 in the C ABI.

```asm
; Manually invoke write(1, "hi\n", 3) using raw syscall
section .data
    msg db "hi", 10    ; "hi\n"

section .text
global _start
_start:
    mov rax, 1         ; __NR_write
    mov rdi, 1         ; fd = stdout
    lea rsi, [msg]     ; buf pointer
    mov rdx, 3         ; count
    syscall

    mov rax, 60        ; __NR_exit
    xor rdi, rdi       ; status = 0
    syscall
```

## Comparison: C ABI vs Syscall ABI (x86-64)

| Position | C ABI (System V) | Syscall ABI |
|---|---|---|
| Number/name | — | `rax` |
| Arg 1 | `rdi` | `rdi` |
| Arg 2 | `rsi` | `rsi` |
| Arg 3 | `rdx` | `rdx` |
| Arg 4 | `rcx` | `r10` |
| Arg 5 | `r8` | `r8` |
| Arg 6 | `r9` | `r9` |
| Arg 7+ | stack | not supported |

## ARM64 Syscall ABI

On AArch64 (ARM64), the convention differs:

- Syscall number: `x8`
- Arguments: `x0`–`x5`
- Return value: `x0`

```asm
// ARM64 write(1, buf, n)
mov x8, #64      // __NR_write on ARM64
mov x0, #1       // fd
ldr x1, =buf     // buf
mov x2, #6       // count
svc #0           // supervisor call
```

`svc #0` is the ARM64 equivalent of `syscall`.

## Kernel-Side: struct pt_regs

The kernel receives all arguments packaged in `struct pt_regs`, which is the saved snapshot of all user registers:

```c
// Macro that unpacks arguments from pt_regs
SYSCALL_DEFINE3(write, unsigned int, fd,
                const char __user *, buf,
                size_t, count)
{
    // fd   ← regs->di (rdi)
    // buf  ← regs->si (rsi)
    // count← regs->dx (rdx)
}
```

The `SYSCALL_DEFINE3` macro expands to a function that extracts the arguments from the register save area — you never see raw register manipulation in C kernel code.

## Return Values and errno

- Return value arrives in `rax`.
- If `rax` is in the range `[-4095, -1]`, it represents a negative errno code.
- glibc detects this, stores `-rax` in the thread-local `errno`, and returns `-1` to the caller.

```c
// glibc errno mapping (simplified)
if ((unsigned long)ret > -4096UL) {
    errno = -ret;
    return -1;
}
return ret;
```

## Pitfalls

- **Never pass more than 6 arguments to a syscall.** Syscalls with more data use a pointer to a struct as one of the six arguments (e.g., `socketcall`, `clone`).
- **Pointer arguments must point to user space.** The kernel rejects kernel-space pointers from user context — `copy_from_user`/`copy_to_user` validate the range.
- **Strings are not null-terminated in the ABI.** The kernel always requires a separate length or uses `strncpy_from_user` with a bound.

**Interview answer:** On x86-64, the syscall number goes in `rax`, up to six arguments go in `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9` (note `r10` not `rcx` because `syscall` clobbers `rcx`), and the return value comes back in `rax` as a negative errno on failure.
