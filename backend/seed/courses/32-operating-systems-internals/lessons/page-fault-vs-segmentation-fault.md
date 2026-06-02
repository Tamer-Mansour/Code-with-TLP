# Page Fault vs Segmentation Fault: Key Difference

Developers routinely confuse "page fault" and "segmentation fault." They are related but distinct: one is a mechanism inside the kernel, the other is a signal delivered to a process. Understanding the relationship is fundamental to debugging crashes and acing systems interviews.

## What each term actually means

| Term | What it is | Who sees it |
|---|---|---|
| Page fault | A hardware CPU exception (trap) handled by the kernel | Only the kernel (invisible to user process) |
| Segmentation fault (SIGSEGV) | A POSIX signal sent to a process | The process (and its crash handler / debugger) |

A segmentation fault is *caused by* a page fault — but not every page fault becomes a segfault.

## The decision tree

```
CPU raises page-fault exception
          │
          ▼
   Kernel examines CR2 (faulting address) and VMA list
          │
    ┌─────┴──────┐
    │            │
Address valid?  No ──► No VMA covers this address
    │                   → kernel sends SIGSEGV
    Yes
    │
Permission OK?  No ──► Write to read-only page, exec on no-exec
    │                   → kernel sends SIGSEGV
    Yes
    │
    ▼
Kernel resolves fault (loads page, updates PTE)
Process continues — no SIGSEGV, no crash
```

## Concrete examples

### Page fault that resolves silently (no segfault)

```c
// First access to a demand-paged heap allocation
char *buf = malloc(65536);
buf[0] = 1;   // page fault → kernel zero-fills page → PTE updated → continues
```

The process never knows a fault happened. This is the normal case.

### Page fault that becomes a segfault

```c
int *p = NULL;
*p = 42;       // page fault at address 0x0
               // → no VMA covers address 0
               // → kernel sends SIGSEGV
               // → default handler: "Segmentation fault (core dumped)"
```

### Protection fault that becomes a segfault

```c
// Write to read-only memory (.rodata segment)
const char *s = "hello";
((char *)s)[0] = 'H';   // page fault, present bit=1, but write to read-only
                         // → error code P=1, W=1
                         // → kernel checks: write attempted on read-only VMA
                         // → SIGSEGV
```

## Why people conflate them

In everyday conversation, "the program segfaulted" means it crashed due to a bad memory access. Under the hood, every segfault *starts* as a page fault — but the kernel decided the access was invalid and sent the signal rather than resolving the fault. So the two events are always chained, just with very different outcomes.

The historic name "segmentation fault" comes from older architectures with hardware segmentation (x86 real mode, Multics) where a segment-limit violation was directly detected in hardware. On modern systems with flat virtual address spaces, the term is kept as the name of SIGSEGV, but the underlying hardware mechanism is always the page-fault exception.

## What about `SIGBUS`?

A related signal, `SIGBUS` (bus error), is sent instead of SIGSEGV in specific cases:

- Accessing memory beyond the end of an `mmap`'d file (the file is smaller than the mapping).
- Unaligned memory access on strict-alignment architectures (SPARC, older MIPS).

On Linux x86-64 you rarely see SIGBUS; SIGSEGV covers most invalid-access scenarios.

## Debugger perspective

```bash
# GDB shows the signal that killed the process — not the page fault
(gdb) run
Program received signal SIGSEGV, Segmentation fault.
0x000000000040115a in main () at bad.c:5
5           *p = 42;
(gdb) info registers cr2   # shows the faulting address if kernel exports it
```

The debugger intercepts SIGSEGV before the default handler kills the process. The fault address is available via `siginfo_t.si_addr` in a signal handler.

**Interview answer:** A page fault is a kernel-internal hardware exception that the OS either resolves (loads the missing page) or converts into SIGSEGV; a segmentation fault is that signal delivered to the process when the kernel decides the access was illegal — every segfault starts as a page fault, but not every page fault becomes a segfault.
