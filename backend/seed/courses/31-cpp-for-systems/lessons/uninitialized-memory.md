# Uninitialized Memory and Indeterminate Values

Reading an uninitialized variable in C++ yields an **indeterminate value** — a value the standard does not define. For most types this is UB; the program's behavior is completely unpredictable.

## Why Memory Is Not Automatically Zeroed

The OS provides zeroed pages (for security), but C++ does not zero local variables or uninitialized heap allocations. The cost of zeroing every allocation would be prohibitive in systems code. Instead, the language trusts the programmer to initialize before use.

```cpp
int x;        // local variable — indeterminate value
int* p = (int*)malloc(sizeof(int));   // heap — indeterminate value

// Reading x or *p here is UB
std::cout << x;    // UB
```

Note: `new int{}` (value-initialization) *does* zero-initialize:

```cpp
int* p = new int{};    // *p == 0, guaranteed
int* q = new int;      // *q is indeterminate
```

## Practical Consequences

- **Debug builds**: memory is often set to known patterns (`0xCC` on MSVC, `0xBE` with ASan) to make reads visible.
- **Release builds**: whatever bytes happened to be in that memory location are used — could be 0, could be a stale pointer, could be sensitive data from a previous allocation.

```cpp
bool flag;          // indeterminate
if (flag) {         // branch taken based on garbage
    launch_missiles();
}
```

## Partially Initialized Structs

```cpp
struct Point {
    int x;
    int y;
};

Point p;
p.x = 5;
// p.y is uninitialized
int dist = p.x * p.x + p.y * p.y;   // UB: reads p.y
```

The fix: always initialize all members.

```cpp
Point p{};     // zero-initializes both x and y
Point p{5, 0}; // explicit initialization
```

## Memory Patterns Inserted by Tools

| Tool / Mode | Fill Pattern | Meaning |
|---|---|---|
| MSVC Debug | `0xCC` | Uninitialized stack |
| MSVC Debug | `0xCD` | Heap allocated, not initialized |
| MSVC Debug | `0xDD` | Freed heap |
| Valgrind | tracks bits | Reports any use of uninit bits |
| ASan + MSan | poison shadow | Aborts on uninitialized read |

## MemorySanitizer (MSan)

MSan tracks which bytes have been written. Any branch or value that depends on uninitialized memory is reported:

```bash
clang++ -fsanitize=memory -fno-omit-frame-pointer -g prog.cpp -o prog
./prog
# WARNING: MemorySanitizer: use-of-uninitialized-value
#     #0 0x... in main prog.cpp:7
```

Note: MSan requires clang and cannot be combined with ASan.

## Common Pattern: Conditionally Initialized Variables

```cpp
int result;
if (condition) {
    result = compute();
}
// If condition is false, result is uninitialized
return result;   // UB on the false branch
```

The fix: initialize at the point of declaration.

```cpp
int result = 0;   // safe default
if (condition) {
    result = compute();
}
return result;
```

## Compiler Warnings

Enable `-Wuninitialized` (included in `-Wall`) to catch many (not all) cases at compile time:

```bash
g++ -Wall -Wextra -o prog prog.cpp
# warning: 'x' is used uninitialized [-Wuninitialized]
```

Static analyzers (clang-tidy, PVS-Studio) catch more complex paths the compiler misses.

## Key Takeaway

> **Interview answer:** Reading an uninitialized variable is UB in C++. The value is indeterminate — not zero, not predictable — and the compiler may generate code that assumes it is never read. Always initialize variables at the point of declaration, use value-initialization (`{}`), and run MemorySanitizer to catch cases that slip through.
