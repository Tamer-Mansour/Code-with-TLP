# What Is a Segfault and What Causes One?

A **segmentation fault** (segfault, SIGSEGV) is a signal the operating system sends to a process when it accesses memory it is not permitted to use. The OS terminates the process immediately — there is no cleanup, no destructor call, no stack unwinding.

## Why the OS Can Do This

Modern CPUs include a Memory Management Unit (MMU). Every memory access passes through the MMU, which maps virtual addresses to physical pages and checks permissions. If a virtual address falls outside any mapped region, or the access type violates the page permissions (e.g., writing to a read-only page), the CPU raises a page fault that the OS converts to SIGSEGV.

```
Process virtual address space
┌───────────────────────────────┐ high address
│         Stack                 │  (read/write)
│              ↓                │
│     (unmapped guard page)     │  ← accessing here → SIGSEGV
│              ↑                │
│         Heap                  │  (read/write)
│         BSS / Data            │  (read/write)
│         Text (code)           │  (read/execute)
└───────────────────────────────┘ low / null address (unmapped)
```

## The Most Common Causes

### 1. Null Pointer Dereference

```cpp
int* p = nullptr;
*p = 42;   // page 0 is never mapped → SIGSEGV
```

Address 0 is intentionally unmapped so that null dereferences reliably crash rather than silently corrupt.

### 2. Dangling Pointer (Use-After-Free)

```cpp
int* p = new int(5);
delete p;
*p = 10;   // memory may be unmapped or reused → SIGSEGV or silent corruption
```

After `delete`, the OS may reclaim the page. Future access can either segfault or silently corrupt a new object at that address.

### 3. Stack Buffer Overflow Reaching Unmapped Memory

```cpp
void foo() {
    char buf[64];
    memset(buf, 0, 10000);  // writes past stack into guard page → SIGSEGV
}
```

The OS places a guard page below the stack. Writing far enough past the end of a local buffer hits it.

### 4. Accessing a Pointer After the Object Leaves Scope

```cpp
int* dangling;
{
    int x = 7;
    dangling = &x;
}             // x is gone; stack frame reused
*dangling = 3; // may segfault or silently corrupt
```

### 5. Misaligned Access on Strict Platforms

On some architectures (older ARM, SPARC), reading a 4-byte `int` from an odd address raises a bus error (SIGBUS) rather than SIGSEGV, but the effect is the same: the process is killed.

## Reading a Core Dump

When a program segfaults with core dumps enabled, `gdb` can show exactly where it died:

```bash
ulimit -c unlimited        # enable core dump
./my_program               # segfaults → core file created
gdb ./my_program core      # open in debugger
(gdb) bt                   # print backtrace
```

The backtrace points directly to the faulting line.

## Using AddressSanitizer

ASan intercepts every memory operation and reports the violation before it reaches the OS:

```bash
g++ -fsanitize=address -g -O1 prog.cpp -o prog
./prog
# ==ERROR: AddressSanitizer: heap-use-after-free on address 0x...
```

ASan output includes the allocation site, the free site, and the use site — far more informative than a bare segfault.

## Key Takeaway

> **Interview answer:** A segfault occurs when the CPU's MMU detects a memory access to an unmapped or permission-violating address and the OS delivers SIGSEGV. The most common causes are null dereference, use-after-free, and writing past a local buffer into a guard page.
