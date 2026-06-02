# Process Address Space: Text, Data, Heap, and Stack

Every process operates inside its own **virtual address space** — a private, contiguous range of memory addresses the OS presents to the program. The underlying physical RAM may be fragmented or shared, but the process sees a clean, isolated view. This address space is divided into well-defined **segments**, each serving a distinct purpose.

## The Classic Layout (x86-64 Linux)

```
High addresses
┌──────────────────────┐
│   Kernel space       │  (invisible/inaccessible to user code)
├──────────────────────┤ ← 0xFFFFFFFF_FFFFFFFF (canonical high)
│   Stack              │  grows downward ↓
│   (local vars,       │
│    return addresses, │
│    saved registers)  │
├──────────────────────┤
│   ...                │  unmapped gap (guard pages)
├──────────────────────┤
│   Memory-mapped      │  mmap() region — shared libs, files
│   regions            │
├──────────────────────┤
│   Heap               │  grows upward ↑
│   (dynamic alloc)    │
├──────────────────────┤
│   BSS segment        │  uninitialised globals (zero-filled)
├──────────────────────┤
│   Data segment       │  initialised globals & static vars
├──────────────────────┤
│   Text segment       │  read-only executable code
└──────────────────────┘ ← 0x0000000000400000 (typical)
Low addresses
```

## Segment-by-Segment Breakdown

### Text Segment (Code Segment)
- Contains the compiled machine instructions of the program.
- Mapped **read-only** and **executable**. Attempting to write to it causes a segmentation fault.
- Shared among all processes running the same binary (copy-on-write semantics), saving physical RAM.

### Data Segment
- Holds **initialised** global and static variables.
- Example: `int x = 42;` at file scope lives here.
- Writable but not executable.

### BSS Segment
- Holds **uninitialised** global and static variables (those declared without an explicit initialiser).
- Example: `static int counter;` — the compiler places this in BSS.
- The OS zero-fills BSS at process start; the segment occupies no space in the binary on disk (only a length is recorded).

### Heap
- Used for **dynamic memory allocation**: `malloc`/`free` in C, `new`/`delete` in C++, object creation in Python (under the hood).
- Grows **upward** toward higher addresses via the `brk`/`sbrk` system calls or `mmap`.
- Memory leaks occur here when allocated blocks are never freed.

### Stack
- Holds **stack frames**: local variables, function arguments, return addresses, and saved register values.
- Grows **downward** on x86. Each function call pushes a frame; each return pops it.
- The OS sets a hard limit (typically 8 MB on Linux, checked with `ulimit -s`).
- Stack overflow results from unbounded recursion or very large local arrays.

### Memory-Mapped Region
- Created by `mmap()` — used for loading shared libraries (`.so`/`.dll`), anonymous large allocations, and memory-mapped files.
- Sits between heap and stack in the virtual address space.

## Worked Example: Viewing Segments in C

```c
#include <stdio.h>
#include <stdlib.h>

int global_init   = 10;          // Data segment
int global_uninit;               // BSS segment

int main(void) {
    int local = 20;              // Stack
    int *heap = malloc(64);      // Heap

    printf("Text  (main):  %p\n", (void *)main);
    printf("Data  (g_init):%p\n", (void *)&global_init);
    printf("BSS   (g_uninit):%p\n", (void *)&global_uninit);
    printf("Heap  (malloc):%p\n", (void *)heap);
    printf("Stack (local): %p\n", (void *)&local);

    free(heap);
    return 0;
}
```

Run this on Linux and you will see addresses increasing from text → data → BSS → heap, with stack at a much higher address.

## Key Properties Table

| Segment | Readable | Writable | Executable | Grows |
|---------|----------|----------|------------|-------|
| Text    | Yes      | No       | Yes        | Fixed |
| Data    | Yes      | Yes      | No         | Fixed |
| BSS     | Yes      | Yes      | No         | Fixed |
| Heap    | Yes      | Yes      | No         | Up    |
| Stack   | Yes      | Yes      | No         | Down  |

## Common Pitfalls

- **Stack vs. heap confusion**: Large local arrays (e.g., `char buf[4194304]`) go on the stack and can silently overflow; allocate large buffers on the heap.
- **Writing to the text segment**: Modifying function pointers or casting away const can trigger a protection fault or enable code-injection attacks.
- **BSS is not in the binary**: Uninitialised globals add no size to the executable file, but they do consume virtual address space at runtime.

> **Interview answer:** A process address space is divided into the text segment (read-only code), data segment (initialised globals), BSS (zero-filled uninitialised globals), heap (dynamic allocations, grows up), and stack (call frames, grows down), all within the process's private virtual address space.
