# Signed vs Unsigned: Overflow and Comparison Pitfalls

Signed/unsigned bugs are responsible for countless security vulnerabilities — from buffer overreads to integer-overflow exploits. The rules are subtle enough that even experienced engineers get burned.

## Overflow Behavior

The single most important rule: **signed integer overflow is undefined behavior (UB) in C++; unsigned overflow wraps modulo 2^N**.

```cpp
// Unsigned wrap-around — well defined, result is 0
uint8_t u = 255;
u += 1;  // u == 0  (modulo 256)

// Signed overflow — UNDEFINED BEHAVIOR
int8_t s = 127;
s += 1;  // could be -128, could be 128, could crash, compiler may assume it never happens
```

The compiler is allowed to assume signed overflow never occurs. This lets it optimize loops aggressively — and that is *exactly* why your "obvious" bug disappears at `-O2` but crashes at `-O0`.

## The Comparison Trap

When a signed and unsigned value are compared, the **signed value is implicitly converted to unsigned**. Negative signed values become huge unsigned numbers:

```cpp
int  size = -1;
unsigned int count = 10;

if (size < count) {           // you expect TRUE
    puts("size is smaller");  // this NEVER prints
}
// -1 as unsigned 32-bit = 4294967295, which is NOT < 10
```

Compilers warn about this with `-Wsign-compare` (enabled by `-Wall`). Always compile with warnings enabled in systems code.

### A Real-World Exploit Pattern

```cpp
// attacker controls `len`
void copy(char* dst, char* src, int len) {
    if (len > 0 && len < MAX_BUF) {  // guard
        memcpy(dst, src, len);        // len implicitly cast to size_t
    }                                 // if len < 0, guard passes but memcpy
}                                     // gets a huge size_t — heap overflow!
```

The fix: use `size_t` (or `uint32_t`) for lengths from the start.

## Detecting Overflow

### Compile-Time: `-ftrapv` and `-fsanitize=signed-integer-overflow`

```bash
g++ -fsanitize=signed-integer-overflow -o prog prog.cpp
```

This inserts runtime checks that abort on signed overflow — invaluable during development.

### Manual Overflow Check Before the Operation

```cpp
#include <climits>

bool add_overflows(int a, int b) {
    if (b > 0 && a > INT_MAX - b) return true;
    if (b < 0 && a < INT_MIN - b) return true;
    return false;
}
```

Or use the GCC/Clang built-ins available since C++17 context:

```cpp
int result;
if (__builtin_add_overflow(a, b, &result)) {
    // handle overflow
}
```

## Unsigned Subtraction — Another Classic Trap

```cpp
size_t a = 5, b = 10;
size_t diff = a - b;  // wraps to a huge number, not -5!

for (size_t i = n - 1; i >= 0; --i) {  // INFINITE LOOP: i is unsigned
    process(arr[i]);
}
```

Fix the loop by using a signed index or restructuring:

```cpp
for (size_t i = n; i-- > 0; ) {  // safe: post-decrement before comparison
    process(arr[i]);
}
```

## Practical Guidelines

- Use **unsigned types** for bit manipulation, sizes, and counts that cannot be negative.
- Use **signed types** for arithmetic where negative results are meaningful.
- Never mix signed and unsigned in comparisons without an explicit cast.
- Enable `-Wall -Wextra -Wsign-conversion` and treat warnings as errors in production builds.
- Audit every `memcpy`/`malloc` call site: the length argument should be `size_t`, not `int`.

| Situation | Recommended type |
|-----------|-----------------|
| Loop counter, array index | `std::size_t` (or `ptrdiff_t` for bidirectional) |
| Buffer length, byte count | `size_t` |
| File offset | `off_t` / `int64_t` |
| Error code | `int` (negative = error) |
| Bit flags | `uint32_t` or `uint64_t` |

**Interview answer:** "Signed overflow is undefined behavior — the compiler may eliminate your overflow checks. Unsigned wraps modulo 2^N but comparing signed and unsigned promotes the signed value to unsigned, turning -1 into UINT_MAX. Enable -Wsign-conversion to catch these at compile time."
