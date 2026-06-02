# valgrind: Detecting Leaks and Invalid Access

valgrind is a dynamic instrumentation framework that runs your program inside a virtual CPU, tracking every memory allocation and access. It catches bugs that may never crash during normal testing — leaks, out-of-bounds reads, use-after-free — and reports the exact call stack where each error occurred.

## How valgrind Works

valgrind intercepts all memory operations at runtime. Its primary tool, **Memcheck**, maintains a shadow memory map: for every byte in the process's address space it tracks whether that byte is addressable and whether its value is defined. When your code violates these properties, Memcheck reports an error immediately, along with the full call stack.

The cost is significant: programs typically run 20–50x slower under valgrind. This is acceptable for testing but not for production.

## Basic Usage

```bash
g++ -g -O0 -o myapp myapp.cpp    # always compile with -g first
valgrind ./myapp
valgrind --leak-check=full ./myapp
valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./myapp
```

| Flag | Effect |
|------|--------|
| `--leak-check=full` | Show each leak with a full call stack |
| `--show-leak-kinds=all` | Include indirect and still-reachable leaks |
| `--track-origins=yes` | Track where uninitialized values come from |
| `--error-exitcode=1` | Exit with non-zero status if errors found (good for CI) |
| `--log-file=val.log` | Write report to a file instead of stderr |

## Memory Error Categories

### Invalid Read / Invalid Write

```cpp
int* arr = new int[5];
arr[5] = 99;   // one past the end
delete[] arr;
```

```
==1234== Invalid write of size 4
==1234==    at 0x401152: main (test.cpp:3)
==1234==  Address 0x5204e64 is 0 bytes after a block of size 20 alloc'd
==1234==    at 0x4C2FB0F: operator new[](unsigned long) (in /usr/lib/valgrind/vgpreload_memcheck.so)
==1234==    at 0x401140: main (test.cpp:1)
```

### Use After Free

```cpp
int* p = new int(42);
delete p;
*p = 99;   // undefined behavior — valgrind catches it
```

```
==1234== Invalid write of size 4
==1234==    at 0x40115A: main (test.cpp:3)
==1234==  Address 0x5204e80 is 4 bytes inside a block of size 4 free'd
==1234==    at 0x4C30D3B: operator delete(void*) (in ...)
==1234==    at 0x401155: main (test.cpp:2)
```

### Uninitialized Value

```cpp
int x;
if (x > 0) { /* valgrind: Conditional jump depends on uninitialised value */ }
```

The `--track-origins=yes` flag adds a second report showing exactly where the uninitialized variable was allocated.

### Memory Leak

```cpp
void leak() {
    char* buf = new char[1024];
    // no delete — leaked
}
```

```
==1234== LEAK SUMMARY:
==1234==    definitely lost: 1,024 bytes in 1 blocks
==1234==    indirectly lost: 0 bytes in 0 blocks
==1234==      possibly lost: 0 bytes in 0 blocks
==1234==    still reachable: 0 bytes in 0 blocks

==1234== 1,024 bytes in 1 blocks are definitely lost in loss record 1 of 1
==1234==    at 0x4C2FB0F: operator new[](unsigned long)
==1234==    at 0x4011A0: leak() (test.cpp:2)
==1234==    at 0x4011B5: main (test.cpp:6)
```

Leak categories:

| Category | Meaning |
|----------|---------|
| Definitely lost | No pointer to this block exists anywhere |
| Indirectly lost | Lost because a parent block is also lost |
| Possibly lost | Interior pointer exists — could be intentional |
| Still reachable | Pointer exists but `free()` was never called |

## Worked Example: Finding a Double Free

```cpp
// double_free.cpp
#include <cstring>

char* make_copy(const char* s) {
    char* buf = new char[strlen(s) + 1];
    strcpy(buf, s);
    return buf;
}

int main() {
    char* a = make_copy("hello");
    char* b = a;   // aliased pointer
    delete[] a;
    delete[] b;    // double free!
    return 0;
}
```

```bash
valgrind --leak-check=full ./double_free
```

```
==5678== Invalid free() / delete / delete[] / realloc()
==5678==    at 0x4C30D3B: operator delete[](void*)
==5678==    at 0x4011EA: main (double_free.cpp:13)
==5678==  Address 0x5204e80 is 6 bytes inside a block of size 6 free'd
==5678==    at 0x4C30D3B: operator delete[](void*)
==5678==    at 0x4011DF: main (double_free.cpp:12)
```

The report shows both the second (invalid) free and the first (valid) free, with line numbers.

## Suppression Files

Third-party libraries sometimes trigger false positives. Suppress known benign issues:

```bash
valgrind --gen-suppressions=all ./myapp 2>suppressions.txt
valgrind --suppressions=suppressions.txt ./myapp
```

## valgrind vs AddressSanitizer

| Aspect | valgrind | AddressSanitizer |
|--------|----------|-----------------|
| Compilation change | None needed | `-fsanitize=address` |
| Slowdown | 20–50x | 2–4x |
| Needs recompile | No | Yes |
| Detects leaks | Yes | Yes (with LeakSanitizer) |
| Stack overflows | Partial | Yes |

> **Interview answer:** valgrind runs your program in an instrumented virtual CPU and tracks every allocation. It reliably catches invalid reads/writes, use-after-free, and memory leaks, reporting the exact allocation and access call stacks. Run it with `--leak-check=full --track-origins=yes` for maximum detail.
