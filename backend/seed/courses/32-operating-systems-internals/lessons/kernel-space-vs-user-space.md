# Kernel Space vs User Space Memory

Every process on a modern OS sees a large, flat **virtual address space**. But that space is split in two: a portion reserved exclusively for the kernel, and the rest available to the process. This split is called the **kernel space / user space divide**, and it is enforced by the CPU's memory management unit (MMU).

## The Address Space Split

On a 32-bit Linux system the classic split is **3 GB user / 1 GB kernel**:

```
0x00000000 ──────────────────────────────────── 0xBFFFFFFF
  User space (3 GB)
  ┌─────────────────────────────────────┐
  │ text segment (code)                 │
  │ data / BSS (globals)                │
  │ heap  (grows ↑)                     │
  │        ...                          │
  │ stack (grows ↓)                     │
  └─────────────────────────────────────┘

0xC0000000 ──────────────────────────────────── 0xFFFFFFFF
  Kernel space (1 GB)  — same in every process's page table
  ┌─────────────────────────────────────┐
  │ kernel code and data                │
  │ kernel stacks (one per process)     │
  │ hardware mappings                   │
  └─────────────────────────────────────┘
```

On 64-bit systems the address space is vastly larger (128 TiB each in a typical Linux configuration), so the split is less of a practical constraint, but the principle is identical.

## Why Map the Kernel Into Every Process?

The kernel's pages appear in every process's page table because a **system call or interrupt must transition to kernel mode without switching page tables**. Switching page tables is expensive — it flushes the TLB. By keeping the kernel mapped at a fixed high address, the CPU can jump from user code to a kernel handler instantly.

The kernel pages are marked **supervisor-only** in the page table entries. The MMU checks this flag on every memory access. A Ring-3 instruction that tries to read `0xC0000000` gets a page fault — not the kernel's data.

## Meltdown and the End of Full Kernel Mapping

The **Meltdown** vulnerability (2018) showed that speculative execution could leak kernel memory to user space via side channels, even though direct access was blocked. The fix — **Kernel Page-Table Isolation (KPTI)** on Linux, **KVA Shadow** on Windows — dramatically reduced the kernel's footprint in user-space page tables. Only the minimal "trampoline" pages needed to enter the kernel are kept mapped; the rest of the kernel is unmapped while the CPU is in user mode.

This made mode switches more expensive (because now the page table must be switched too), a cost discussed further in the performance lesson.

## Heap and Stack Are User Space

```c
#include <stdlib.h>

int global = 5;        // data segment — user space
int main(void) {
    int local = 10;    // stack — user space
    int *p = malloc(4);// heap — user space (sbrk/mmap syscall sets it up)
    *p = 99;
    free(p);
    return 0;
}
```

All three live in user space. `malloc` may internally call `brk` or `mmap` (both system calls) to grow the heap, but the memory the returned pointer points to is user-space memory.

## Kernel Stack vs User Stack

Each thread has **two stacks**:

| Stack | Location | Used when |
|---|---|---|
| User stack | User space | Normal function calls in application code |
| Kernel stack | Kernel space | Executing inside the kernel on behalf of this thread |

When a system call is made, the CPU saves the user-space stack pointer and switches to the thread's kernel stack. The kernel stack is typically small (4–16 KB on Linux) because deep recursion in kernel code is dangerous and avoided by design.

## Common Pitfalls

- **Thinking "kernel space" is a separate physical region**: It is a virtual address range. The same physical RAM can back kernel pages in many processes' page tables simultaneously.
- **Assuming a process cannot see kernel addresses**: It can see the virtual addresses exist (unless KASLR hides them), but it cannot read or write them without a privilege trap.
- **Confusing kernel stack with user stack**: Stack overflows in user space produce a segfault; a kernel stack overflow is catastrophic (kernel panic).

## Interview Answer

> **Q: What is the difference between kernel space and user space?**
>
> **Interview answer:** They are two regions of a process's virtual address space. User space holds the application's code, heap, and stack — accessible from Ring 3. Kernel space holds the OS code and data — mapped into every process's page table but marked supervisor-only, so any Ring-3 access triggers a page fault.
