# Crossing the Boundary: Syscalls, Interrupts, and Exceptions

User mode code cannot do privileged work on its own — it must ask the kernel. There are exactly three ways the CPU crosses from user mode to kernel mode, each with a different trigger and different semantics: **system calls**, **hardware interrupts**, and **exceptions**. Understanding all three is essential for any OS interview.

## 1. System Calls — Intentional Kernel Requests

A **system call** (syscall) is a deliberate request from user code to the kernel. The program says: "I want to read a file / send a packet / allocate memory — please do it for me."

**x86-64 mechanism (`SYSCALL` instruction):**

1. User code places the syscall number in `rax` and arguments in `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`.
2. `SYSCALL` saves `rip` and `rflags` into `rcx` and `r11`, switches to Ring 0 using the address in `MSR_LSTAR`.
3. The kernel's syscall dispatcher reads `rax`, validates it, calls the appropriate handler.
4. `SYSRETQ` restores `rip`/`rflags` and returns to Ring 3.

```c
// C runtime wraps the raw syscall:
ssize_t n = read(fd, buf, count);

// Which internally does (simplified):
// mov rax, 0        (SYS_read = 0 on Linux x86-64)
// mov rdi, fd
// mov rsi, buf
// mov rdx, count
// syscall
// ; return value in rax
```

## 2. Hardware Interrupts — Asynchronous External Events

A **hardware interrupt** is triggered by a device (keyboard, NIC, timer chip) signaling the CPU via the interrupt controller (APIC on modern x86). It is **asynchronous** — it can arrive at any point during user-mode or kernel-mode execution.

**Flow:**

1. Device asserts an IRQ line.
2. CPU finishes the current instruction, checks interrupt flags.
3. If `IF` (interrupt flag) is set, CPU saves `rip`, `rsp`, `rflags`, `cs`, `ss` on the kernel stack.
4. CPU switches to Ring 0, looks up the handler address in the **IDT (Interrupt Descriptor Table)**, jumps to it.
5. Handler runs (e.g., reads keyboard scancode, wakes a sleeping process).
6. `IRETQ` restores saved state, returns to wherever execution was interrupted.

| Feature | Syscall | Hardware Interrupt |
|---|---|---|
| Triggered by | User code intentionally | External hardware |
| Synchronous? | Yes | No |
| Saves user state | Minimal (SYSCALL ABI) | Full (pushed to kernel stack) |
| Can interrupt kernel? | No (enters kernel deliberately) | Yes (if interrupts enabled) |

## 3. Exceptions — Synchronous CPU Faults

An **exception** is raised by the CPU itself when something goes wrong (or intentionally, for special traps). It is always synchronous — caused by a specific instruction.

Three categories:

| Type | Definition | Example |
|---|---|---|
| Fault | Recoverable; restarts the instruction | Page fault (#PF) — OS fixes the mapping, retries |
| Trap | Non-restartable; advances past the instruction | Breakpoint (`INT3`), syscall via `INT 0x80` |
| Abort | Unrecoverable; process or system must die | Double fault (#DF), machine check exception |

```
User code reads unmapped address
        │
        ▼
CPU raises Page Fault (#PF, vector 14)
        │
        ▼
Kernel page fault handler:
  is it a valid but not-yet-loaded page? → allocate frame, map it, IRETQ
  is it a stack growth opportunity?       → extend stack mapping, IRETQ
  is it a genuine bad address?            → SIGSEGV → process dies
```

## The Interrupt Descriptor Table (IDT)

All three entry paths ultimately go through the **IDT** — a kernel-owned table of 256 entries mapping interrupt/exception vectors to handler addresses. The kernel initializes the IDT at boot with `LIDT`. User code cannot modify it (writing to `IDTR` is a privileged operation).

```
IDT entries (selected):
  0   — #DE Divide Error
  6   — #UD Invalid Opcode
  13  — #GP General Protection Fault
  14  — #PF Page Fault
  32+ — Hardware IRQs (IRQ0 = timer at vector 32)
  128 — Linux legacy syscall (INT 0x80)
```

## Choosing the Right Mechanism

- Use **syscalls** for intentional kernel services.
- **Interrupts** are managed by hardware and the kernel; user code does not choose them.
- **Exceptions** are raised automatically; your code handles the consequences (e.g., catching `SIGSEGV`) or avoids the conditions.

## Common Pitfalls

- **"INT 0x80 is the only way to make syscalls"**: It is the legacy x86 (32-bit) method. Modern 64-bit Linux uses the faster `SYSCALL` instruction.
- **"Interrupts always preempt the CPU immediately"**: No — interrupts are held if `IF=0` (interrupts disabled). The kernel clears `IF` in critical sections.
- **"All exceptions kill the process"**: Faults like page faults are handled transparently by the kernel and the faulting instruction is retried.

## Interview Answer

> **Q: How does user-mode code enter the kernel?**
>
> **Interview answer:** Through three mechanisms: system calls (intentional, via the `SYSCALL` instruction), hardware interrupts (asynchronous signals from devices routed through the APIC and IDT), and exceptions (synchronous CPU faults like page faults or protection violations). All three cause the CPU to raise its privilege level to Ring 0 and jump to a kernel handler registered in the IDT.
