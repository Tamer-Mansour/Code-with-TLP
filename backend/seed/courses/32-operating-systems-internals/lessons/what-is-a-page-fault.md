# What Is a Page Fault?

A page fault is a hardware exception raised by the CPU's Memory Management Unit (MMU) when a running process tries to access a virtual address that has no valid mapping in the current page table. Rather than silently returning garbage data, the CPU traps into the kernel so the OS can decide what to do next.

## Why virtual memory creates this trap

Modern OSes give every process a private virtual address space — a fiction that the process owns all of memory. Physical RAM, however, is finite and shared. The page table is the translation map from virtual page numbers to physical frame numbers. When a virtual page has no entry, or when the present bit in its page-table entry (PTE) is zero, the hardware cannot complete the translation and fires a page-fault exception.

```
Virtual Address: 0x00401000
  │
  ▼
Page Table Entry ──► present bit = 0  ──► #PF exception raised
                                          kernel handler invoked
```

## What information the fault carries

When a page fault occurs on x86-64, the CPU:

1. Saves the faulting instruction pointer (RIP) and registers on the kernel stack.
2. Loads the faulting *virtual address* into the special `CR2` register.
3. Pushes an *error code* onto the stack encoding three key bits:
   - **P bit** (0 = page not present, 1 = protection violation)
   - **W/R bit** (0 = read, 1 = write attempt)
   - **U/S bit** (0 = supervisor mode, 1 = user mode)

```c
// Linux x86-64 page-fault handler signature (simplified)
void do_page_fault(struct pt_regs *regs, unsigned long error_code)
{
    unsigned long address = read_cr2();   // faulting virtual address
    // ...determine cause and fix or signal SIGSEGV
}
```

## Three broad outcomes

| Situation | What the OS does |
|---|---|
| Page is on disk (swapped out) | Load page from swap, update PTE, resume |
| Page is legitimately not loaded yet (demand paging) | Load from file/zero-fill, update PTE, resume |
| Invalid access (bad pointer, stack overflow) | Deliver `SIGSEGV` — process dies |

The first two outcomes are *recoverable* faults. The third is fatal from the process's point of view.

## A page fault is not always a bug

This surprises many newcomers. Every `mmap`'d file and every lazily-allocated heap page starts with a zero present bit. The very first access to each such page intentionally causes a fault — that is how the OS defers physical allocation until it is truly needed. A process with 100 MB of virtual heap may only ever fault in 10 MB of actual pages.

## Worked example: first access to a heap page

```c
char *buf = malloc(4096);   // just updates bookkeeping; no physical page yet
buf[0] = 'A';               // PAGE FAULT here — kernel allocates a frame,
                            // zeros it, maps it, and returns; write succeeds
```

The process never sees the fault. From its perspective the write just takes a few microseconds longer than usual.

## Quick reference: is it a page fault or a segfault?

- **Page fault** — kernel can resolve it (or chooses to send SIGSEGV afterward).
- **Segfault (SIGSEGV)** — the kernel *sends the signal* after deciding the access is invalid. SIGSEGV is the *outcome*, not the hardware trap itself.

**Interview answer:** A page fault is a CPU exception triggered by the MMU when a virtual address has no valid present mapping; the kernel handler either resolves it (loads the missing page) or terminates the process with SIGSEGV.
