# AddressSanitizer, UBSan, and ThreadSanitizer

The sanitizer suite is a collection of compiler-level instrumentation tools built into Clang and GCC. They catch different classes of bugs at runtime with much lower overhead than valgrind — making them practical to run in CI and during regular development.

## AddressSanitizer (ASan)

ASan detects:
- Out-of-bounds reads and writes (heap, stack, globals)
- Use-after-free and use-after-return
- Heap and stack buffer overflows
- Memory leaks (via LeakSanitizer, which is bundled by default)

```bash
g++ -fsanitize=address -fno-omit-frame-pointer -g -O1 -o myapp myapp.cpp
./myapp
```

The `-fno-omit-frame-pointer` flag preserves frame pointers so that ASan can print accurate stack traces. `-O1` gives slightly better error reporting than `-O0` while still being debuggable.

### Example: Heap Buffer Overflow

```cpp
int main() {
    int* arr = new int[5];
    arr[7] = 99;   // 2 elements past the end
    delete[] arr;
}
```

```
==9001==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x602000000038
READ of size 4 at 0x602000000038 thread T0
    #0 0x401152 in main overflow.cpp:3
    #1 0x7f2c libc-start-main
SUMMARY: AddressSanitizer: heap-buffer-overflow overflow.cpp:3 in main
```

ASan is approximately 2x slower than unmodified execution — far more practical than valgrind's 20–50x.

### Example: Use-After-Free

```cpp
int* p = new int(10);
delete p;
return *p;   // ASan: use-after-free
```

```
==9002==ERROR: AddressSanitizer: heap-use-after-free on address 0x602000000010
READ of size 4 at 0x602000000010
    #0 0x4011b2 in main uaf.cpp:3
```

## LeakSanitizer (LSan)

LSan is enabled automatically with ASan. To run it standalone (faster):

```bash
g++ -fsanitize=leak -g -o myapp myapp.cpp
./myapp
```

```
==9003==ERROR: LeakSanitizer: detected memory leaks
Direct leak of 1024 byte(s) in 1 object(s) allocated from:
    #0 operator new[](unsigned long) in ...
    #1 leak_function() at main.cpp:5
SUMMARY: LeakSanitizer: 1024 byte(s) leaked in 1 allocation(s).
```

## UndefinedBehaviorSanitizer (UBSan)

UBSan detects undefined behavior at runtime — bugs that may or may not crash, depending on compiler version, optimization level, and moon phase.

```bash
g++ -fsanitize=undefined -g -o myapp myapp.cpp
```

Catches:

| Behavior | Example |
|----------|---------|
| Signed integer overflow | `INT_MAX + 1` |
| Null pointer dereference | `*((int*)nullptr)` |
| Shift out of range | `1 << 64` |
| Division by zero | `x / 0` |
| Invalid enum value | casting `5` to a 2-value enum |
| Array out of bounds (VLA) | accessing past a VLA |

### Example: Signed Integer Overflow

```cpp
#include <climits>
int main() {
    int x = INT_MAX;
    return x + 1;  // UBSan: signed integer overflow
}
```

```
overflow.cpp:3:14: runtime error: signed integer overflow:
    2147483647 + 1 cannot be represented in type 'int'
```

### Combined Flags

```bash
# Use together for maximum coverage
g++ -fsanitize=address,undefined -fno-omit-frame-pointer -g -O1 -o myapp myapp.cpp
```

Note: ASan and TSan cannot be combined — they conflict at the memory model level.

## ThreadSanitizer (TSan)

TSan detects **data races** — concurrent accesses to shared memory where at least one access is a write and there is no synchronization.

```bash
g++ -fsanitize=thread -g -O1 -o myapp myapp.cpp
```

### Example: Data Race

```cpp
#include <thread>
int counter = 0;

void increment() {
    for (int i = 0; i < 100000; ++i)
        counter++;   // no lock — data race!
}

int main() {
    std::thread t1(increment);
    std::thread t2(increment);
    t1.join(); t2.join();
}
```

```
WARNING: ThreadSanitizer: data race (pid=9004)
  Write of size 4 at 0x... by thread T2:
    #0 increment() race.cpp:6

  Previous write of size 4 at 0x... by thread T1:
    #0 increment() race.cpp:6
SUMMARY: ThreadSanitizer: data race race.cpp:6 in increment()
```

TSan overhead is typically 5–15x slowdown and 5–10x memory usage.

## Sanitizer Comparison

| Sanitizer | Flag | Finds | Overhead |
|-----------|------|-------|----------|
| ASan | `-fsanitize=address` | Memory errors, leaks | ~2x |
| LSan | `-fsanitize=leak` | Leaks only | ~1.1x |
| UBSan | `-fsanitize=undefined` | Undefined behavior | ~1.5x |
| TSan | `-fsanitize=thread` | Data races | ~5–15x |

## CI Integration

```yaml
# .github/workflows/sanitize.yml
- name: Build with ASan + UBSan
  run: |
    g++ -fsanitize=address,undefined -fno-omit-frame-pointer -g -O1 \
        -o myapp myapp.cpp
    ./myapp

- name: Build with TSan
  run: |
    g++ -fsanitize=thread -g -O1 -o myapp myapp.cpp
    ./myapp
```

Run sanitized builds in parallel with your normal test suite so they don't slow down the critical path.

> **Interview answer:** AddressSanitizer catches memory errors (overflow, use-after-free, leaks) at ~2x overhead; UBSan catches undefined behavior (overflow, null deref, bad shifts) at ~1.5x overhead; ThreadSanitizer catches data races at ~5–15x overhead. They are compiler flags, require no external tools, and are ideal for CI pipelines.
