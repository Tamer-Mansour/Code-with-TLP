# The Per-Process Virtual Address Space Layout

Every process on a modern OS gets its own virtual address space. The OS, linker, and runtime cooperate to divide that space into well-defined **regions** with distinct purposes and permission sets. Knowing the layout explains why stack overflows crash programs, why `NULL` dereferences fault, and where your heap memory actually lives.

## Canonical Layout on 64-bit Linux (x86-64)

```
High address  0xFFFF_FFFF_FFFF_FFFF
              ┌─────────────────────────┐
              │   Kernel space          │  Supervisor-only; user access → fault
              │   (128 TB)              │
0xFFFF_8000_0000_0000
              ├─────────────────────────┤  ← Kernel/user split (canonical hole)
              │   (non-canonical hole)  │  Addresses here are always invalid
0x0000_8000_0000_0000
              ├─────────────────────────┤
              │   Stack                 │  Grows downward; one per thread
              │   (ASLR-randomized)     │
              ├─────────────────────────┤
              │   mmap / shared libs    │  libc.so, anonymous mmap, file maps
              │   (ASLR-randomized)     │
              ├─────────────────────────┤
              │   Heap                  │  Grows upward via brk/sbrk or mmap
              │   (ASLR-randomized)     │
              ├─────────────────────────┤
              │   BSS segment           │  Uninitialized globals (zeroed)
              ├─────────────────────────┤
              │   Data segment          │  Initialized globals & statics
              ├─────────────────────────┤
              │   Text segment          │  Executable code (read + execute)
Low address   0x0000_0000_0040_0000   (typical ELF load address before PIE)
              │   Null guard page       │  Unmapped; catches NULL dereferences
              0x0000_0000_0000_0000
```

## Each Region Explained

### Text (Code) Segment
- Contains compiled machine instructions.
- Permissions: **read + execute**, never writable (W^X policy).
- Shared among processes running the same binary (one physical copy, many virtual mappings).

### Data Segment
- Holds **initialized** global and static variables (`int x = 5;`).
- Permissions: read + write.
- Loaded from the ELF binary by the dynamic linker at startup.

### BSS Segment
- Holds **uninitialized** (zero-initialized) globals (`int y;`).
- Takes no space in the binary file — the OS zero-maps fresh pages at load time.

### Heap
- Dynamic allocations via `malloc` / `new`.
- Grows upward; managed by the allocator library (`jemalloc`, `ptmalloc`, etc.).
- Backed by `brk()`/`sbrk()` for small allocations, `mmap(MAP_ANONYMOUS)` for large ones.

### mmap Region
- Memory-mapped files, shared memory, and anonymous mappings.
- Also where shared libraries are loaded (`.so` / `.dll`).
- Each `mmap` call carves out a virtual range; physical pages are demand-paged.

### Stack
- Local variables, return addresses, saved registers — per-thread.
- Grows **downward** on x86.
- Default limit: 8 MB on Linux (`ulimit -s`). Exceeding it → stack overflow (guard page fault → SIGSEGV).

### Kernel Space
- The top half of the virtual address space is reserved for the kernel on every process.
- User-mode code cannot access it; a protection fault occurs immediately.
- Kernel code mapped here can access user memory only through explicit copy routines (`copy_from_user`).

## ASLR and Randomization

**Address Space Layout Randomization** (ASLR) randomizes the base addresses of the stack, heap, and mmap regions at each process launch. This defeats return-oriented programming (ROP) exploits that depend on knowing exact addresses.

```bash
# Check ASLR level on Linux (0=off, 1=partial, 2=full)
cat /proc/sys/kernel/randomize_va_space
```

## Practical Inspection

```bash
# View a running process's memory map (PID 1234)
cat /proc/1234/maps

# Example output columns:
# start-end        perms  offset  dev  inode  path
# 7f3a2b000000-7f3a2b200000 r-xp 00000000 fd:01 12345 /lib/x86_64-linux-gnu/libc.so.6
```

**Common pitfall:** Writing past the end of a stack-allocated array can silently overwrite the saved return address before the guard page is hit, enabling classic stack-smashing attacks — which is exactly why modern compilers add stack canaries.

**Interview answer:** A process's virtual address space is divided into fixed regions — text (code), data, BSS, heap (grows up), mmap area, and stack (grows down) — with the kernel occupying the upper half, all enforced by MMU permissions and guard pages.
