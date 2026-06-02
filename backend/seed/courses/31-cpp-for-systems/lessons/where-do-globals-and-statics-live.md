# Where Do Globals, Statics, and Literals Live?

Not every variable goes on the stack or heap. Globals, statics, and string/numeric literals occupy their own dedicated memory segments that the OS sets up before `main` even begins.

## Mapping Variable Types to Segments

| Variable | Segment | Notes |
|----------|---------|-------|
| Initialized global / static | Data (.data) | Value baked into the binary |
| Zero-initialized global / static | BSS (.bss) | Not stored in binary — OS zeroes at load time |
| `const` global (POD) | Read-only Data (.rodata) | Often in the same ELF section as text |
| String literal | .rodata | Shared across uses; writing is UB |
| Function-local `static` | Data or BSS | Initialized on first call (thread-safe since C++11) |
| `thread_local` variable | TLS segment | Per-thread copy |

## Initialized Globals (.data)

```cpp
int x = 42;            // .data  — 4 bytes in binary with value 42
double ratio = 1.618;  // .data  — 8 bytes in binary
```

The linker embeds the initial value directly in the executable. The OS memory-maps the segment as read-write.

## Zero-Initialized Globals (.bss)

```cpp
int counter;           // .bss  — zero by C++ guarantee
static char buf[4096]; // .bss  — 4 KB of zeroes, 0 bytes in binary
```

BSS is just a record of "this region should be zeroed." The OS uses copy-on-write zero pages, so BSS barely costs any physical RAM until written.

## Read-Only Data (.rodata)

```cpp
const int MAX = 1024;      // .rodata
const char* msg = "hello"; // .rodata — the string "hello\0" lives here
```

The page is mapped read-only. A write triggers a segfault — intentionally, to catch bugs.

```cpp
char* p = (char*)"hello";
p[0] = 'H';   // SIGSEGV — .rodata is read-only
```

## Function-Local Statics

A `static` inside a function has static storage duration (lives for the whole program) but is only accessible by name within that function. Since C++11, the initialization is guaranteed to be thread-safe (the compiler inserts a guard variable).

```cpp
int& id_generator() {
    static int counter = 0;  // initialized once, on first call
    return ++counter;
}
```

Checking the binary:

```bash
objdump -t a.out | grep counter
# shows counter in .bss (zero-init) or .data (non-zero init)
```

## Thread-Local Storage (TLS)

`thread_local` variables get their own per-thread copy. The runtime allocates TLS blocks when a thread starts and frees them when it exits.

```cpp
thread_local int errno_copy = 0;   // the real errno works like this
```

On Linux the TLS block is pointed to by the `FS` segment register. Access looks like a normal memory load from the compiler's perspective but addresses a thread-private region.

## String Literals

Every string literal in C++ has type `const char[]` and lives in `.rodata`. The compiler may merge identical literals:

```cpp
const char* a = "test";
const char* b = "test";
// a == b may be true (implementation-defined merging)
```

This is why storing a `const char*` to a literal is safe (it lives forever), but casting away `const` and writing is undefined behaviour.

## Verifying with Tools

```bash
# View section sizes
size a.out
#    text    data     bss     dec     hex  filename
#    2048     512    4096    6656    1a00  a.out

# View symbols and their sections
nm -n a.out | head -20
```

> **Interview answer:** Initialized globals and statics live in the `.data` segment (value in the binary); zero-initialized ones live in `.bss` (not stored, OS zeroes them); string literals and `const` POD globals live in `.rodata` (read-only). All are allocated before `main` runs and freed after it exits.
