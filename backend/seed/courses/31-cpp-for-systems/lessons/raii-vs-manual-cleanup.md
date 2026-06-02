# RAII vs goto-Cleanup in C

C has no destructors, so every function that acquires multiple resources must release them manually. The most disciplined C pattern for this is the **goto-cleanup** idiom, sometimes called the "error label" pattern. Understanding it — and its limitations — explains why RAII was a foundational addition to C++.

## The goto-Cleanup Pattern in C

```c
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

int process_file(const char* path) {
    int ret = -1;
    int fd = -1;
    char* buf = NULL;

    fd = open(path, O_RDONLY);
    if (fd == -1) goto done;

    buf = malloc(4096);
    if (!buf) goto done;

    if (read(fd, buf, 4096) < 0) goto done;

    // ... do work ...
    ret = 0;

done:
    free(buf);        /* safe: free(NULL) is a no-op */
    if (fd != -1) close(fd);
    return ret;
}
```

This pattern is used extensively in the Linux kernel. It ensures all cleanup happens at one labeled point regardless of which early exit was taken. The Linux kernel style guide explicitly endorses it for this exact reason.

## Why goto-Cleanup Works in C

- All resources that might be initialized are set to a sentinel value (`NULL`, `-1`) before the acquisition attempts.
- Every path jumps to the same `done` label.
- The cleanup code handles partially initialized state by checking the sentinel before releasing.

## Limitations of goto-Cleanup

| Limitation | Impact |
|---|---|
| Manual sentinel initialization | Easy to forget; wrong sentinel causes UB or missed cleanup |
| Cleanup order must be manually reversed | Adding a new resource requires updating the cleanup block |
| Does not compose across function calls | Each function must implement its own pattern |
| No automatic cleanup on C++ exception propagation | C++ exceptions bypass `goto done` |
| Scales poorly | 10 resources = 10 sentinel checks in one block |

## The Same Logic in C++ with RAII

```cpp
#include <stdexcept>
#include <vector>

void process_file(const char* path) {
    FileDescriptor fd(path, O_RDONLY);     // throws on failure
    std::vector<char> buf(4096);           // throws on failure

    if (read(fd.get(), buf.data(), 4096) < 0)
        throw std::system_error(errno, std::generic_category());

    // ... do work ...
}   // fd and buf destroyed automatically — correct cleanup order guaranteed
```

No labels, no sentinels, no cleanup block. Adding a new resource is one line; removing one does not require updating a cleanup section.

## Cleanup Order: a Critical Difference

In goto-cleanup, the programmer must write cleanup in the correct reverse-acquisition order:

```c
// Must clean up in reverse: buf first, then fd
done:
    free(buf);
    if (fd != -1) close(fd);
```

In C++ with RAII, destructors run in reverse order of construction automatically. The compiler enforces this — no discipline required.

## When goto-Cleanup Is Still Appropriate

- **Kernel code.** The Linux kernel is C; RAII is unavailable. The goto pattern is the sanctioned alternative.
- **Embedded C.** Where C++ is not available or the runtime is constrained.
- **Interfacing with C libraries from C files.** Using RAII wrappers in C++ that call C APIs is better; pure C must use goto-cleanup.
- **Performance-critical paths where C++ exception overhead matters.** Though in most modern systems this concern is overstated.

## Mixing C and C++ Safely

When calling a C API from C++:

```cpp
// Wrap the C resource immediately in a RAII type
void use_c_library() {
    // c_lib_open returns a raw handle — wrap it instantly
    auto handle = CLibHandle(c_lib_open("resource_name"));
    c_lib_do_work(handle.get());
    // handle's destructor calls c_lib_close
}
```

Never let a raw C handle exist as a local variable for more than one line. Acquire and wrap in a single step.

## Side-by-Side Comparison

```c
/* C: goto-cleanup */
int two_resources(const char* a, const char* b) {
    int ret = -1;
    int fd_a = open(a, O_RDONLY);
    if (fd_a == -1) goto done;
    int fd_b = open(b, O_RDONLY);
    if (fd_b == -1) goto close_a;
    ret = 0;
    close(fd_b);
close_a:
    close(fd_a);
done:
    return ret;
}
```

```cpp
// C++: RAII
void two_resources(const char* a, const char* b) {
    FileDescriptor fd_a(a, O_RDONLY);
    FileDescriptor fd_b(b, O_RDONLY);
    // both closed automatically, in reverse order
}
```

**Interview answer:** The C goto-cleanup pattern centralizes resource release at a single labeled exit point and is correct but requires manual sentinels and careful ordering. RAII automates this: destructors run in guaranteed reverse-construction order on every exit path, including exceptions, which C lacks entirely.
