# What Actually Causes a Segmentation Fault

A segmentation fault (SIGSEGV) is one of the most common crashes in systems programming. Despite the scary name, every segfault has a concrete, diagnosable root cause. This lesson catalogs the real causes and gives you a mental model for debugging them quickly.

## Root cause: the kernel rejected a memory access

SIGSEGV is delivered when the kernel's page-fault handler concludes that the access cannot be legally satisfied. The two top-level reasons are:

1. **No VMA covers the address** — the virtual address belongs to no mapped region at all.
2. **Permission mismatch** — the address is mapped, but the access type violates the VMA's permissions (e.g., writing to a read-only mapping, executing a non-executable page).

## Catalog of common causes

### 1. Null pointer dereference

```c
int *p = NULL;
printf("%d\n", *p);   // SIGSEGV at address 0x0
```

Address 0 is deliberately left unmapped on all major OSes. The kernel sends SIGSEGV immediately.

### 2. Use-after-free

```c
int *p = malloc(sizeof(int));
free(p);
*p = 99;   // undefined behavior; may segfault or silently corrupt
```

After `free()`, the allocator may have returned the pages to the OS. A subsequent access can fault if the pages are unmapped, or silently corrupt heap metadata if they are still mapped.

### 3. Stack overflow

```c
void recurse(void) { recurse(); }   // infinite recursion

int main(void) { recurse(); }       // stack grows until it hits the guard page
```

The OS places a *guard page* — a page with no permissions — just below the bottom of the stack segment. When the stack grows past the last valid frame, the next push hits the guard page, causing a SIGSEGV. The kernel does *not* automatically grow the stack further (it already tried and decided the stack is too large).

```
   ┌──────────────┐  ← high address (initial stack pointer)
   │  Stack frames │
   │  (grows down) │
   ├──────────────┤
   │  Guard page  │  ← no-permission page → SIGSEGV on access
   └──────────────┘
```

### 4. Writing to read-only memory

```c
char *s = "hello";    // literal in .rodata — read-only
s[0] = 'H';           // SIGSEGV: write to read-only VMA
```

The `.rodata` section is mapped with `PROT_READ` only. The write triggers a protection-violation page fault (error code: P=1, W=1), which the kernel converts to SIGSEGV.

### 5. Accessing unmapped memory via bad arithmetic

```c
int arr[10];
int *p = arr + 1000;   // points far outside the array
*p = 5;                // SIGSEGV if address is outside any VMA
```

### 6. Misaligned access on strict-alignment architectures

On x86-64, misaligned reads usually work. On ARM64 with strict alignment enabled, or on SPARC, accessing a 4-byte int at an odd address raises `SIGBUS`, not SIGSEGV — a related but distinct signal.

### 7. Executing non-executable memory (NX/DEP violation)

```c
char shellcode[] = { 0x90, 0x90, 0xc3 };   // NOP NOP RET
((void(*)(void))shellcode)();               // attempt to execute stack memory
// SIGSEGV: execute on page with PROT_READ|PROT_WRITE but not PROT_EXEC
```

Modern OSes enforce W^X (write XOR execute). The page-fault error code has the I/D bit set, the kernel sees no execute permission, and sends SIGSEGV.

## Debugging workflow

```bash
# 1. Get the address from the core dump or GDB
gdb ./program core
(gdb) bt          # backtrace
(gdb) info signal # show SIGSEGV details

# 2. Find what address was accessed
(gdb) p/x $cr2    # or check si_addr in siginfo

# 3. Cross-reference with /proc/self/maps
cat /proc/<PID>/maps   # see which VMA (if any) covers that address
```

## Sanitizer shortcut

```bash
# AddressSanitizer catches use-after-free and buffer overflows before SIGSEGV
clang -fsanitize=address -g program.c && ./a.out
```

ASan intercepts `malloc`/`free` and memory accesses, giving you a precise error report with stack traces instead of a raw crash.

**Interview answer:** A segfault happens when the kernel's page-fault handler finds either no VMA covering the accessed address or a permission mismatch (e.g., write to read-only); common causes are null pointer dereference, use-after-free, stack overflow hitting the guard page, and writing to `.rodata`.
