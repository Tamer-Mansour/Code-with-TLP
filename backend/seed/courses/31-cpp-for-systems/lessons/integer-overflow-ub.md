# Signed Integer Overflow and Optimizer Assumptions

Signed integer overflow is undefined behavior in C and C++. This surprises many programmers who expect arithmetic to "wrap around" like unsigned arithmetic does. The difference has significant implications for how compilers optimize your code.

## The Rule

- **Unsigned overflow**: defined — wraps modulo 2^N (e.g., `UINT_MAX + 1 == 0`).
- **Signed overflow**: **undefined behavior** — the standard imposes no requirement.

```cpp
int x = INT_MAX;   // 2147483647
int y = x + 1;     // UB — not guaranteed to be INT_MIN
```

On most hardware `INT_MAX + 1` does wrap to `INT_MIN` in two's complement, but the compiler is *not required* to produce that result and often does not.

## Why the Standard Chose UB

Allowing UB for signed overflow lets the compiler make algebraic transformations that are only valid for non-overflowing integers. For example:

```cpp
// If signed overflow is UB, the compiler can rewrite:
(x + 1) > x
// as:
true   // always, because overflow is assumed not to happen
```

This transformation is valid for mathematical integers and, by the UB assumption, for C++ signed integers too. The compiled code becomes a simple constant without any arithmetic.

## A Classic Optimizer Exploit of Signed Overflow

```cpp
void process(int i) {
    if (i + 1 > i) {        // programmer intends: "check for overflow"
        do_work(i);
    }
}
```

The compiler sees: "if signed overflow is UB, then `i + 1 > i` is always true." It eliminates the branch entirely and always calls `do_work(i)`. The overflow check the programmer wrote does nothing.

**Correct overflow check:**

```cpp
#include <climits>

if (i < INT_MAX) {   // check before the operation, not after
    do_work(i + 1);
}
// Or use __builtin_add_overflow (GCC/Clang):
int result;
if (!__builtin_add_overflow(i, 1, &result)) {
    do_work(result);
}
```

## Loop Induction Variables

```cpp
for (int i = 0; i <= n; ++i) {   // UB if i reaches INT_MAX and increments
    arr[i] = 0;
}
```

The compiler may assume `i` never overflows and generate code that runs indefinitely if `n == INT_MAX`.

## Detecting Signed Overflow

```bash
# UBSan catches signed overflow at runtime
g++ -fsanitize=undefined -g prog.cpp -o prog
./prog
# runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'
```

You can also compile with `-ftrapv` to make overflow trap immediately (useful in testing):

```bash
g++ -ftrapv prog.cpp -o prog
```

## Using Unsigned Types

For bit manipulation and counters where wraparound is the intended behavior, use unsigned types explicitly:

```cpp
uint32_t mask = 0xFFFFFFFFu;
uint32_t next = mask + 1u;   // defined: wraps to 0
```

## When Compilers Add `-fwrapv`

GCC's `-fwrapv` flag makes signed overflow wrap in two's complement and suppresses all overflow-based optimizations. This is sometimes used in kernels or security-sensitive code that relies on wrapping behavior, at the cost of missed optimizations.

```bash
g++ -fwrapv prog.cpp -o prog
```

## Key Takeaway

> **Interview answer:** Signed integer overflow is UB in C++, so the compiler assumes it never happens and uses that assumption to eliminate checks and transform expressions. Never check for overflow after the fact; use pre-checks, `__builtin_add_overflow`, or unsigned types with defined wrapping semantics. Detect violations with UBSan.
