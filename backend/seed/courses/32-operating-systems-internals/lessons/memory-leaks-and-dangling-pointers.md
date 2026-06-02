# Memory Leaks, Dangling Pointers, and Use-After-Free

Manual memory management gives you control but demands discipline. Three of the most common and costly bugs in systems programming — **memory leaks**, **dangling pointers**, and **use-after-free** — all stem from losing track of the relationship between a pointer and the lifetime of the memory it points to.

## Memory Leaks

A memory leak occurs when heap memory is allocated but never freed, and all pointers to it are lost. The memory is neither usable by your program nor returnable to the OS (until the process exits).

```c
void process_data(void) {
    int *buf = malloc(1024 * sizeof(int));
    if (some_error_condition()) {
        return;         // BUG: forgot to free(buf) on this path
    }
    // ... use buf ...
    free(buf);
}
```

Leaks are especially dangerous in:
- Long-running servers — even a 1 KB leak per request becomes gigabytes over time.
- Embedded systems — physical memory is scarce and the process may never restart.

**Detection tools:**

```bash
# Valgrind: reports all leaks with allocation stack traces
valgrind --leak-check=full ./my_program

# AddressSanitizer (compile-time instrumentation, much faster)
gcc -fsanitize=address -g -o my_program my_program.c
./my_program
```

## Dangling Pointers

A dangling pointer is a pointer that still holds an address, but the memory at that address has already been freed (or the stack frame that owned it has been destroyed).

```c
int *get_dangling(void) {
    int x = 5;
    return &x;   // UB: x is destroyed when the function returns
}

void heap_dangle(void) {
    int *p = malloc(sizeof(int));
    *p = 42;
    free(p);
    printf("%d\n", *p);   // UB: use after free — p is now dangling
}
```

The danger: dereferencing a dangling pointer is **undefined behavior**. It may:
- Silently read a garbage value (the freed memory was reused).
- Crash with SIGSEGV.
- Corrupt data if the freed region was re-allocated for something else.

Best practice: **null the pointer immediately after freeing**.

```c
free(p);
p = NULL;   // safe — dereferencing NULL gives a clear crash (SIGSEGV)
```

## Use-After-Free

Use-after-free (UAF) is the specific case of reading from or writing to heap memory after it has been `free()`d. It is a critical security vulnerability — exploits can place attacker-controlled data in the freed region before it is accessed again.

```c
char *msg = malloc(32);
snprintf(msg, 32, "hello");
free(msg);

// ... later in the code ...
printf("%s\n", msg);   // use-after-free — security vulnerability
```

Modern allocators often poison freed memory (fill with a sentinel value like `0xFEEEFEEE`) in debug builds to make UAF bugs easier to detect.

## Double Free

Calling `free()` on the same pointer twice corrupts the allocator's internal free list, which can lead to heap corruption and security exploits.

```c
int *p = malloc(sizeof(int));
free(p);
free(p);   // double free — undefined behavior, often crashes
```

The null-after-free pattern prevents this too: `free(NULL)` is a no-op in C, so nulling the pointer makes accidental double-free harmless.

## Summary of Rules

| Rule | Why |
|---|---|
| Every `malloc` must have exactly one `free` | Prevents leaks and double-free |
| Null the pointer after `free` | Prevents dangling pointer use |
| Never return a pointer to a local variable | Prevents stack dangling |
| Check `malloc` return value | Prevents null-dereference on OOM |
| Prefer RAII / smart pointers in C++ | Automates the above rules |

## C++ Smart Pointers

C++ provides RAII wrappers that eliminate most manual memory errors:

```cpp
#include <memory>

auto p = std::make_unique<int>(42);  // freed automatically when p goes out of scope
auto s = std::make_shared<int>(99);  // reference-counted; freed when last owner gone
```

## Interview Answer

> "A memory leak is failing to free heap memory you no longer reference. A dangling pointer points to freed or out-of-scope memory; using it is undefined behavior and a security risk (use-after-free). Mitigations include nulling pointers after free, using tools like Valgrind or AddressSanitizer, and preferring RAII or smart pointers in C++."
