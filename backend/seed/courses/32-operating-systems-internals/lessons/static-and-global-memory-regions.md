# Static, Global, and BSS Memory Regions

Beyond the stack and heap, a process image contains several other memory regions that exist for the lifetime of the process. Understanding the **process image layout** is essential for reasoning about global state, startup costs, and binary size.

## The Classic Process Image Layout

```
High address
+---------------------------+
|   Stack (grows down)      |
+---------------------------+
|   (unmapped / guard page) |
+---------------------------+
|   Heap (grows up)         |
+---------------------------+
|   BSS  (zero-init globals)|
+---------------------------+
|   Data (init globals)     |
+---------------------------+
|   Text (code / rodata)    |
+---------------------------+
Low address (0x400000 on Linux)
```

## The Text Segment

The **text segment** holds:
- Compiled machine code (executable instructions)
- Read-only data: string literals, `const` globals, jump tables

It is mapped **read-only and executable** to prevent accidental or malicious modification. String literals live here, which is why modifying them is undefined behavior:

```c
char *s = "hello";
s[0] = 'H';   // UB — "hello" is in the read-only text segment
```

## The Data Segment (Initialized Data)

Global and static variables that are **explicitly initialized to a non-zero value** live in the `.data` section. Their initial values are stored directly in the executable file and loaded into memory at startup.

```c
int global_count = 42;         // .data — stored in the binary
static float ratio = 3.14f;   // .data — file-size cost
```

Because these values are embedded in the binary, large initialized arrays increase the executable size on disk.

## The BSS Segment (Zero-Initialized)

**BSS** stands for "Block Started by Symbol" (a historical name). It holds global and static variables that are **zero-initialized** — either explicitly with `= 0` or left uninitialized (C guarantees zero for globals).

```c
int counters[10000];        // BSS — 10 000 ints, all zero
static char buf[4096];      // BSS — zero-initialized
int explicit_zero = 0;      // BSS — same as above
```

The critical insight: BSS **does not store the zeros in the binary**. The OS simply maps zero pages on demand. A large BSS array adds almost nothing to the executable file size — only a record saying "reserve N bytes here."

| Property | .data | .bss |
|---|---|---|
| Initialized? | Yes (non-zero) | Yes (zero) |
| Stored in binary? | Yes (costs disk space) | No (only size recorded) |
| Set by | Loader copies from file | OS zero-fills pages |

## Static Variables Inside Functions

`static` local variables are **not on the stack** — they live in `.data` or `.bss` and persist across calls:

```c
int counter(void) {
    static int calls = 0;   // lives in BSS (zero-initialized)
    return ++calls;
}

int main(void) {
    printf("%d\n", counter()); // 1
    printf("%d\n", counter()); // 2
    printf("%d\n", counter()); // 3
}
```

This is thread-unsafe without synchronization because all threads share the same static variable.

## Read-Only Data (rodata)

Many compilers place `const` global data and string literals in a separate `.rodata` section (mapped within the text segment or alongside it), distinct from mutable `.data`. This allows the OS to share these pages across multiple processes running the same binary.

```c
const int LIMIT = 1000;        // likely .rodata
const char MSG[] = "ready";   // likely .rodata
```

## Inspecting Sections with System Tools

```bash
# View section sizes in a compiled binary
size my_program

# List all ELF sections
readelf -S my_program

# Show symbols and their sections
nm my_program | sort -k2
```

## Interview Answer

> "A process image has text (code + read-only data), data (initialized globals), BSS (zero-initialized globals — not stored on disk), heap, and stack. BSS is space-efficient because the OS zero-fills pages lazily rather than storing zeros in the binary."
