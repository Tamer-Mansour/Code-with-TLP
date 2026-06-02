# Process Memory Layout: Text, Data, BSS, Heap, Stack

Every C++ program runs inside a process that owns a virtual address space. The operating system divides that space into well-defined segments, and understanding each one helps you reason about performance, security, and debugging.

## The Five Classic Segments

| Segment | Contents | Writable? | Lifetime |
|---------|----------|-----------|---------|
| **Text** (Code) | Compiled machine instructions | No | Program lifetime |
| **Data** | Initialized global & static variables | Yes | Program lifetime |
| **BSS** | Zero-initialized globals & statics | Yes | Program lifetime |
| **Heap** | Dynamic allocations (`new`, `malloc`) | Yes | Manually controlled |
| **Stack** | Local variables, return addresses, function frames | Yes | Function call lifetime |

On a typical x86-64 Linux process the layout looks like this (low address at top):

```
0x0000000000000000  (null — unmapped, catches null dereferences)
[Text segment]      read-only machine code + string literals
[Data segment]      initialized globals: int x = 42;
[BSS segment]       zero-initialized globals: int y;  // implicitly 0
[Heap]              grows upward via brk / mmap
    ...
[Stack]             grows downward from high address
0xFFFFFFFFFFFFFFFF  kernel space (inaccessible from user mode)
```

## Text Segment

The CPU fetches instructions from here. It is mapped read-only so that a wild pointer write does not silently corrupt program logic — it triggers a segmentation fault instead. String literals such as `"hello"` typically live here too, which is why writing through a `char*` literal is undefined behaviour.

```cpp
const char* s = "hello";
// s[0] = 'H';  // UB — may segfault; text segment is read-only
```

## Data Segment

Global and static variables that have a non-zero initializer are stored in the Data segment. The values are baked into the executable file itself.

```cpp
int counter = 10;          // Data segment
static double PI = 3.14;   // Data segment
```

## BSS Segment

BSS stands for "Block Started by Symbol." Variables placed here are guaranteed to be zero at program start. Because they are all zero, the OS does not need to store the actual bytes in the binary — it just records the size and zeroes the region at load time. This keeps executables small.

```cpp
int global_array[1024];    // BSS — 4 KB of zeroes, ~0 bytes in the binary
```

## Heap

The heap is the region managed by the allocator (`malloc`/`free` in C, `new`/`delete` in C++). It grows upward as you request memory and can be fragmented over time. The OS hands pages to the allocator in large chunks; the allocator then carves them up for individual requests.

```cpp
int* p = new int[1000];   // allocated on the heap
delete[] p;               // returned to the allocator
```

## Stack

Each thread has its own stack. When a function is called, a *stack frame* is pushed containing the function's local variables, saved registers, and the return address. When the function returns the frame is popped in O(1). The stack size is fixed at thread creation (commonly 1–8 MB on Linux).

```cpp
void foo() {
    int x = 5;        // lives on the stack
    double buf[256];  // 2 KB on the stack — be careful with large locals
}
```

## Why This Matters

- **Debugging segfaults:** a null-pointer dereference hits the unmapped page at address 0; a stack overflow hits the guard page beneath the stack.
- **Binary size:** large zero-initialized arrays cost nothing in the executable (BSS), but large initialized arrays bloat it (Data).
- **Security:** modern OSes use Address Space Layout Randomization (ASLR) to randomize segment base addresses, making exploits harder.

> **Interview answer:** A process's memory is divided into text (code), data (initialized globals), BSS (zero globals), heap (dynamic), and stack (local variables/frames). The heap grows upward; the stack grows downward.
