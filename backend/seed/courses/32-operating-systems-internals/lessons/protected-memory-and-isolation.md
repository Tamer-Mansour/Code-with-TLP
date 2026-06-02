# How Hardware Enforces Process Isolation

The operating system promises that one process cannot read or corrupt another's memory. This promise is not kept by software vigilance alone — it is enforced by dedicated hardware: the **Memory Management Unit (MMU)** working in combination with CPU privilege levels. Understanding this hardware mechanism is critical for systems interviews.

## The Core Tool: Virtual Memory and Page Tables

Every process lives in its own **virtual address space**. Virtual addresses are translated to physical addresses by the MMU on every memory access. Each process has its own **page table** — a data structure mapping virtual pages to physical frames.

When the OS schedules a process, it loads that process's top-level page table address into the CPU's page table base register (`CR3` on x86-64). Any virtual address the process uses is now translated through *its* page table, not another process's.

```
Process A page table          Process B page table
VA 0x400000 → PA 0x1A3000    VA 0x400000 → PA 0x2F7000
VA 0x401000 → PA 0x1A4000    VA 0x401000 → PA 0x2F8000

Both see "0x400000", but they land on different physical memory.
Neither can reach the other's frames because those frames are
not mapped in its page table at all.
```

## Page Table Entry Flags

Each Page Table Entry (PTE) carries permission flags the MMU checks on every access:

| Flag | Meaning |
|---|---|
| **Present (P)** | Page is in physical memory; if clear → page fault |
| **Read/Write (R/W)** | If clear, the page is read-only |
| **User/Supervisor (U/S)** | If clear, only Ring 0 can access it |
| **No-Execute (NX/XD)** | If set, code cannot be executed from this page |
| **Accessed / Dirty** | Set by hardware when page is read/written |

The **U/S bit** is the hardware mechanism that enforces user space vs kernel space. Kernel pages have `U/S=0`. The MMU rejects any Ring-3 access to such a page with a page fault, regardless of what value the virtual address has.

## What Happens on an Illegal Access

```
Process A
   │  mov rax, [0xFFFF800000000000]  ; try to read a kernel VA
   ▼
MMU translates → finds U/S=0 on that PTE (kernel page)
MMU raises Page Fault (#PF, vector 14)
   ▼
Kernel page fault handler:
   access was from Ring 3 to a supervisor page
   → send SIGSEGV to Process A
   → Process A terminates
```

No data was read. The fault fires before the memory bus transaction completes.

## SMEP and SMAP: Extra Hardware Guards

Modern x86 CPUs added two more protections controlled by bits in `CR4`:

- **SMEP (Supervisor Mode Execution Prevention, CR4.SMEP)**: Prevents Ring-0 code from executing instructions on pages marked user-accessible. This stops a kernel exploit from jumping to shellcode planted in user space.
- **SMAP (Supervisor Mode Access Prevention, CR4.SMAP)**: Prevents Ring-0 code from reading or writing user-space pages without explicitly setting the `AC` flag in EFLAGS. This forces the kernel to use dedicated copy functions (`copy_from_user` / `copy_to_user`) that include boundary checks.

## Address Space Layout Randomization (ASLR)

ASLR is a software policy (implemented by the OS loader) that randomizes where the stack, heap, and shared libraries are placed in the virtual address space on each execution. It does not change the hardware enforcement model but raises the bar for exploits that need to know exact addresses.

```bash
# On Linux, see ASLR setting:
cat /proc/sys/kernel/randomize_va_space
# 0 = disabled, 1 = partial, 2 = full (default)
```

## Isolation Is Not Just About Reads

The hardware also prevents one process from **writing** to another's memory and from **executing** data pages (NX bit). A combined use of R/W=0 and NX=1 on code pages, and R/W=1, NX=1 on data pages, is called **W^X (Write XOR Execute)** — a standard hardening policy that prevents injecting shellcode into a writable buffer and then jumping to it.

## Common Pitfalls

- **"The OS checks every memory access in software"**: No. The MMU checks every access in hardware — far too fast for software to be in the path.
- **"Shared memory breaks isolation"**: Shared memory (`mmap` with `MAP_SHARED`, `shmget`) is a deliberate, opt-in exception — both processes explicitly map the same physical frames. Isolation is not broken; it is intentionally relaxed under OS control.
- **"KASLR makes the kernel immune to exploitation"**: KASLR is a probabilistic mitigation, not a guarantee. It raises exploitation difficulty but is not a hard security boundary.

## Interview Answer

> **Q: How does hardware enforce that one process cannot access another's memory?**
>
> **Interview answer:** Each process has its own page table loaded into CR3 when it runs. The MMU translates every virtual address through that table; physical frames belonging to other processes simply are not mapped. Page table entries also carry permission bits (read/write, user/supervisor, NX) the MMU checks on every access — a violation raises a page fault before any data is transferred.
