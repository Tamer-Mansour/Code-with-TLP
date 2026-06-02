# Recursion and How It Uses the Call Stack

Recursion is a function calling itself (directly or indirectly) to break a problem into smaller sub-problems. Understanding how it maps to the call stack is essential for predicting performance, avoiding stack overflows, and reasoning about tail-call optimization.

## The Call Stack

Every function call pushes a **stack frame** (also called an activation record) onto the process stack. The frame contains:

- Return address (where execution resumes after the call)
- Saved registers (caller-preserved registers the function will modify)
- Local variables and parameters
- Alignment padding

```
High address  ┌──────────────┐
              │  main frame  │
              ├──────────────┤
              │  fact(5)     │  <- first recursive call
              ├──────────────┤
              │  fact(4)     │
              ├──────────────┤
              │  fact(3)     │
              ├──────────────┤  <- stack grows downward
              │  ...         │
Low address
```

The default stack size on Linux is 8 MB; on Windows, 1 MB. Each frame is typically 16–256 bytes depending on local variables, so deep recursion (tens of thousands of frames) can exhaust the stack.

## Anatomy of a Recursive Function

Every recursive function needs:

1. **Base case** — a condition that stops recursion.
2. **Recursive case** — the function calls itself with a smaller or simpler input.

```cpp
// Factorial
long long fact(int n) {
    if (n <= 1) return 1;          // base case
    return n * fact(n - 1);        // recursive case
}
```

## Stack Depth and Stack Overflow

`fact(100000)` would create 100,000 frames and overflow the stack. When the OS detects the stack pointer crossing the guard page, the process receives a segmentation fault (Linux) or a stack overflow exception (Windows).

```cpp
// This will crash on typical systems
long long boom = fact(1'000'000);  // stack overflow
```

Always reason about the maximum recursion depth:

- Binary search: O(log N) depth — safe for any realistic N.
- Fibonacci (naive): O(N) depth — dangerous for large N; also exponential time.
- DFS on a tree of depth D: O(D) frames.

## Tail Recursion and Tail-Call Optimization (TCO)

A **tail call** is a recursive call that is the **last operation** in the function — nothing happens after it returns.

```cpp
// NOT a tail call — must multiply after return
long long fact(int n) { return n * fact(n - 1); }

// Tail-recursive with accumulator
long long fact_tail(int n, long long acc = 1) {
    if (n <= 1) return acc;
    return fact_tail(n - 1, acc * n);  // tail call
}
```

A compiler performing TCO can reuse the current stack frame instead of pushing a new one, converting the recursion into a loop with O(1) stack space. GCC and Clang apply TCO at `-O2` when they can prove it is safe.

```bash
# Check whether TCO was applied (look for jmp instead of call):
gcc -O2 -S fact_tail.cpp && grep -A2 'fact_tail:' fact_tail.s
```

C++ does **not** guarantee TCO (unlike Scheme or Haskell), so do not rely on it for correctness — only for performance.

## Mutual Recursion

Two functions that call each other:

```cpp
bool is_even(unsigned n);
bool is_odd(unsigned n);

bool is_even(unsigned n) { return n == 0 || is_odd(n - 1); }
bool is_odd(unsigned n)  { return n != 0 && is_even(n - 1); }
```

Mutual recursion requires a **forward declaration** so each function knows the other exists.

## Worked Example: Binary Search (Recursive)

```cpp
#include <cstdio>

int bsearch(const int* arr, int lo, int hi, int target) {
    if (lo > hi) return -1;                // base case: not found
    int mid = lo + (hi - lo) / 2;
    if (arr[mid] == target) return mid;    // base case: found
    if (arr[mid] < target)
        return bsearch(arr, mid + 1, hi, target);   // right half
    else
        return bsearch(arr, lo, mid - 1, target);   // left half
}

int main() {
    int arr[] = {2, 5, 8, 12, 16, 23, 38, 56};
    int n = 8;
    printf("index of 23: %d\n", bsearch(arr, 0, n - 1, 23));  // 5
    printf("index of 10: %d\n", bsearch(arr, 0, n - 1, 10));  // -1
}
```

The maximum depth is log2(8) = 3 frames — completely safe.

## Pitfalls

- **Missing base case** — infinite recursion until stack overflow.
- **Wrong reduction** — recursive call does not move toward the base case.
- **Exponential blowup** — naive Fibonacci recomputes the same sub-problems; memoize or use iteration instead.
- **Large local variables** — a function with a 4 KB local array 1000 levels deep uses 4 MB of stack.

## When to Prefer Iteration

Use recursion when:
- The problem structure is inherently recursive (tree traversal, divide-and-conquer, parsing).
- The depth is bounded and shallow.

Prefer iteration when:
- Depth is proportional to input size (risk of stack overflow).
- Performance is critical and TCO cannot be guaranteed.

> **Interview answer:** Each recursive call pushes a stack frame; too many levels cause a stack overflow. Tail-recursive calls — where the recursive call is the last operation — can be optimized by the compiler to reuse the current frame (TCO), but C++ does not guarantee this. When depth is unbounded, convert to an explicit stack-based iteration.
