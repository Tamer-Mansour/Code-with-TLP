# What Causes a Stack Overflow?

A stack overflow is not a software exception you can catch with a try/catch — it is a hardware memory-protection fault triggered when the stack grows beyond its allocated limit. Understanding it prevents entire classes of runtime crashes.

## How the Stack Limit is Enforced

The OS maps the stack as a region of virtual memory. Directly beneath the bottom of the stack it places an unmapped *guard page* (typically one page = 4 KB). When RSP moves into that page, the hardware raises a page-fault that the OS converts into a signal (`SIGSEGV` on Linux, `EXCEPTION_STACK_OVERFLOW` on Windows).

```
High address
[Stack region — mapped, grows downward]
[Guard page — unmapped, 4 KB]
[Other mappings or unmapped space]
Low address
```

Default stack sizes:
- Linux: **8 MB** per thread (`ulimit -s`)
- macOS: 8 MB (main thread), 512 KB (pthreads)
- Windows: **1 MB** per thread by default

## Common Causes

### 1. Unbounded Recursion

The most frequent cause. Each recursive call pushes a new frame; without a reachable base case the stack fills up.

```cpp
int infinite(int n) {
    return infinite(n + 1);  // no base case — stack overflow
}
```

Even correct recursion can overflow on deep inputs:

```cpp
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);   // ~O(n) stack depth
}
// fib(100000) will stack overflow on most systems
```

**Fix:** Convert to iteration or use `std::stack`-based explicit recursion.

### 2. Very Large Stack Allocations

Declaring a large array as a local variable consumes stack space immediately.

```cpp
void bad() {
    char buffer[4 * 1024 * 1024];  // 4 MB on the stack — overflow on Linux defaults
    memset(buffer, 0, sizeof(buffer));
}
```

**Fix:** Allocate large buffers on the heap (`std::vector`, `std::make_unique`).

### 3. Deep Call Chains

Even without recursion, a very deep call graph consumes stack space. Each frame is typically 32–512 bytes depending on locals.

```cpp
void a() { /* ... locals ... */ b(); }
void b() { /* ... locals ... */ c(); }
// ... 10,000 levels deep
```

### 4. Stack Corruption (Overflows into Guard Page)

A buffer overflow in a local array can write past the guard page. This is also a common security vulnerability (stack smashing).

```cpp
void vulnerable(const char* input) {
    char buf[64];
    strcpy(buf, input);   // no length check — can overflow stack frame
}
```

## Diagnosing a Stack Overflow

- **Linux:** `ulimit -s` shows the stack limit; increase with `ulimit -s unlimited` for testing.
- **Debugger:** GDB shows `SIGSEGV` in a recursive function — check the backtrace depth with `bt`.
- **AddressSanitizer:** compile with `-fsanitize=address` to catch stack-buffer overflows at the point of corruption.

```bash
g++ -fsanitize=address -g -o prog prog.cpp
./prog   # ASAN reports exact location of overflow
```

## Tail-Call Optimization as a Fix

If a recursive call is in tail position and the compiler applies TCO, no new frame is needed:

```cpp
// With -O2, many compilers optimize this to a loop
int sum(int n, int acc = 0) {
    if (n == 0) return acc;
    return sum(n - 1, acc + n);   // tail call — can be optimized
}
```

C++ does **not** guarantee TCO (unlike Scheme or Scala). Verify with the assembly output.

> **Interview answer:** A stack overflow occurs when the call stack exceeds its size limit — typically caused by infinite or very deep recursion, or by allocating huge local arrays. The OS guard page triggers a SIGSEGV when RSP crosses the boundary.
