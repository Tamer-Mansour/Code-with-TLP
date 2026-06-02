# Privileged Instructions and Why They Trap

Not all CPU instructions are created equal. Some are so powerful that allowing any program to execute them would destroy the isolation the OS depends on. These are called **privileged instructions**, and the CPU will not execute them in user mode — instead it raises a hardware exception called a **trap**.

## What Makes an Instruction "Privileged"?

An instruction is privileged when executing it from untrusted code could:

- Alter the CPU's core configuration (interrupt descriptor table, page tables, segment descriptors)
- Directly access hardware devices, bypassing OS-managed access control
- Halt or reset the processor
- Change the current privilege level arbitrarily

Examples on x86-64:

| Instruction | What It Does | Why It Must Be Privileged |
|---|---|---|
| `HLT` | Halts the CPU until next interrupt | Any app could freeze the machine |
| `CLI` / `STI` | Disables / enables hardware interrupts | Disabling interrupts breaks scheduling |
| `LGDT` / `LIDT` | Loads global/interrupt descriptor table | Redirects all exception handling |
| `MOV CR0/CR3` | Writes control registers (paging, WP bit…) | Can disable memory protection or swap page tables |
| `IN` / `OUT` | Reads / writes I/O ports directly | Can talk to any device, bypassing drivers |
| `WRMSR` | Writes model-specific register | Reconfigures CPU features (e.g., disabling SMEP) |

## What "Trap" Means Here

When Ring-3 code executes a privileged instruction, the CPU does **not** execute it. Instead:

1. The CPU raises a **General Protection Fault (#GP, interrupt vector 13)** — or in some cases a specific fault type.
2. The CPU saves the faulting instruction's address (and other state) on the kernel stack.
3. Execution jumps to the kernel's registered #GP handler.
4. The kernel decides what to do — usually: send `SIGSEGV` to the process and terminate it.

```
User code                 CPU                     Kernel
─────────────────         ───────────────────      ───────────────────
mov eax, 0
OUT 0x80, eax   ──trap──▶  #GP fault raised  ──▶  gp_fault_handler()
[never reaches              save registers          kill process / log
 next line]                 switch to ring 0        and return
```

## A Concrete Example: Trying to Halt the CPU

```asm
section .text
global _start
_start:
    hlt          ; Attempt HLT from user space (Ring 3)
                 ; CPU raises #GP immediately
                 ; Kernel delivers SIGSEGV — process dies
```

On Linux, running this produces:
```bash
$ nasm -f elf64 halt.asm && ld halt.o -o halt && ./halt
Segmentation fault (core dumped)
```

The `hlt` instruction was never executed. The trap fired first.

## Semi-Privileged Instructions: IOPL and the I/O Permission Bitmap

Interestingly, x86 has a partial mechanism: the **I/O Privilege Level (IOPL)** field in EFLAGS and the **I/O Permission Bitmap (IOPB)** in the TSS. A process can be granted access to *specific* I/O ports without giving it full Ring 0. Real-time applications and old DOS emulators used this. But it is rare in modern OS design.

## Why Not Just Ignore the Instruction?

Some hypervisors use **binary translation** or **trap-and-emulate** to handle privileged instructions from a guest OS: the instruction traps, the hypervisor catches it, simulates its effect, and returns. This is how VMware worked on CPUs that lacked hardware virtualization. It is slow but correct.

Hardware virtualization (Intel VT-x) avoids most of this overhead by adding a new "Ring −1" so the guest OS can truly run in Ring 0 under the hypervisor's supervision.

## Common Pitfalls

- **Thinking the instruction is "blocked by software"**: It is the CPU itself that refuses to execute it. The kernel does not have a filter in the instruction path.
- **Assuming all traps are errors**: A `SYSCALL` instruction intentionally traps into the kernel. "Trap" means a synchronous CPU exception — it can be intentional or a fault.
- **Forgetting that some instructions are conditionally privileged**: `CPUID` runs in any ring; `RDTSC` is unprivileged by default but can be restricted via `CR4.TSD`.

## Interview Answer

> **Q: What happens when user-mode code executes a privileged instruction?**
>
> **Interview answer:** The CPU does not execute it. Instead it raises a General Protection Fault (#GP), saves the current execution context, and jumps to the kernel's fault handler, which typically terminates the offending process. The privileged instruction is enforced entirely in hardware — no software check is involved.
