# Compile-Time vs Runtime Error: How to Tell Them Apart

Every C++ error falls into one of two broad categories: errors the compiler (or linker) catches before the program runs, and errors that only manifest during execution. Knowing which category an error belongs to tells you where to look for it and how to fix it faster.

## Compile-Time Errors

A **compile-time error** prevents the program from being built. The compiler or linker rejects your code and produces an error message with a file name and line number. No executable is produced.

### Types of compile-time errors

**Syntax errors** — the source text violates C++ grammar:

```cpp
int x = 5     // missing semicolon → error: expected ';'
int y = 5 +;  // incomplete expression
```

**Type errors** — an operation is applied to incompatible types:

```cpp
std::string s = 42;  // error: cannot convert 'int' to 'std::string'
int* p = 0.5;        // error: invalid conversion from 'double' to 'int*'
```

**Undeclared identifier** — using a name before declaring it:

```cpp
int main() {
    foo();   // error: 'foo' was not declared in this scope
}
```

**Linker errors** — declaration exists but no definition:

```cpp
// header says void process(int);
// no .cpp file ever defines process(int)
// → undefined reference to 'process(int)'
```

Linker errors are technically post-compile, but they still prevent the program from running, so they are grouped with compile-time errors in practice.

### Compile-time errors are the best kind

The compiler found the bug for you. The error message includes the exact file and line. Fix it before running.

## Runtime Errors

A **runtime error** occurs while the program is executing. The binary was produced successfully; the error only appears under specific inputs or conditions.

### Categories of runtime errors

**Logic errors** — the program produces wrong output because the algorithm is incorrect. No crash, no signal — just wrong answers.

```cpp
int average(int a, int b) {
    return a + b / 2;   // bug: operator precedence — should be (a + b) / 2
}
```

**Memory errors** — undefined behavior from incorrect memory access:

```cpp
int arr[5];
arr[10] = 99;   // out-of-bounds write — undefined behavior, may crash or corrupt data

int* p = nullptr;
*p = 1;          // null dereference — almost always a segfault (SIGSEGV)
```

**Resource exhaustion** — stack overflow from unbounded recursion, heap exhaustion from memory leaks.

**Exceptions** — C++ exceptions are thrown at runtime:

```cpp
std::vector<int> v = {1, 2, 3};
int x = v.at(100);   // throws std::out_of_range at runtime
```

## Side-by-Side Comparison

| Property | Compile-Time Error | Runtime Error |
|---|---|---|
| When detected | During build | During execution |
| Binary produced? | No | Yes |
| Error message quality | Precise (file + line) | Varies (crash, wrong output) |
| Reproducibility | Always | May depend on input or state |
| Examples | Syntax, type mismatch, ODR | Segfault, wrong answer, exception |

## Tools That Bridge the Gap

Modern C++ lets you move some runtime checks to compile time:

```cpp
static_assert(sizeof(int) == 4, "Expected 32-bit int");   // compile-time check
```

**AddressSanitizer (ASan)** detects memory errors at runtime with detailed diagnostics:

```bash
g++ -std=c++17 -fsanitize=address -g main.cpp -o main
./main
```

**UndefinedBehaviorSanitizer (UBSan)** catches signed integer overflow, null dereference, and other UB:

```bash
g++ -std=c++17 -fsanitize=undefined -g main.cpp -o main
```

## Worked Example — Spotting the Difference

```cpp
#include <vector>

int sum(std::vector<int> v) {
    int total = 0;
    for (int i = 0; i <= v.size(); ++i)  // bug: <= should be <
        total += v[i];                    // out-of-bounds on last iteration
    return total;
}
```

- The compiler accepts this code — no compile-time error.
- At runtime, `v[v.size()]` reads one element past the end — undefined behavior that may crash or produce garbage results.

Fixing `<=` to `<` eliminates the runtime error without any compiler help — you must reason about the algorithm yourself (or use tools like ASan to catch it dynamically).

## Common Pitfall

**Undefined behavior is not always a runtime crash.** A program with UB may appear to work correctly on your machine and fail on the CI server, or fail only in release builds where the compiler optimizes aggressively. Never rely on "it doesn't crash" as proof of correctness.

> **Interview answer:** "Compile-time errors are caught by the compiler or linker before the program runs — they always produce a clear error message with a line number. Runtime errors occur during execution and include logic bugs, memory corruption, and exceptions. In C++, undefined behavior (like out-of-bounds access) is a runtime error that may not crash immediately, making sanitizers like ASan and UBSan essential diagnostic tools."
