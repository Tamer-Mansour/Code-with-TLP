# Common Sources of UB in Real Code

Undefined behavior appears in many patterns that look innocent at first glance. Knowing the most frequent sources lets you read code defensively and catch bugs before they bite.

## 1. Out-of-Bounds Array Access

```cpp
int buf[4];
buf[4] = 99;   // UB: index 4 is one past the end
buf[-1] = 0;   // UB: negative index
```

The compiler does not insert a guard. The write lands in adjacent stack memory — possibly overwriting a return address or another variable.

## 2. Dereferencing Null or Dangling Pointers

```cpp
int* p = nullptr;
*p = 5;           // UB: null dereference

int* q = new int(7);
delete q;
*q = 3;           // UB: dangling pointer (use-after-free)
```

`use-after-free` is a leading vulnerability class. The memory may have been reallocated to something else, silently corrupting unrelated data.

## 3. Signed Integer Overflow

```cpp
int x = INT_MAX;
int y = x + 1;   // UB: signed overflow
```

Signed overflow is UB; the compiler assumes it never happens. It may optimize away checks that only make sense if overflow is possible (see the optimizer lesson).

## 4. Strict Aliasing Violations

```cpp
float f = 3.14f;
int* ip = reinterpret_cast<int*>(&f);
int n = *ip;      // UB: violates strict aliasing rule
```

The compiler assumes that a pointer of type `int*` never points to a `float` object. Reading through the wrong pointer type breaks the alias analysis the optimizer relies on. The portable alternative is `memcpy`.

## 5. Data Races

```cpp
// Thread 1
counter++;

// Thread 2 (concurrent, no synchronization)
counter++;
```

Any unsynchronized access to a shared variable where at least one thread writes is UB under the C++11 memory model. The fix is `std::atomic<int>` or a mutex.

## 6. Shifting Beyond the Width of a Type

```cpp
uint32_t x = 1;
uint32_t y = x << 32;  // UB: shift amount >= bit width
int z = -1 << 1;       // UB: left-shift of a negative value
```

The result is not "zero" or "wrapped" — it is undefined. This trips up bit-manipulation code dealing with edge cases like full masks.

## 7. Returning a Reference to a Local Variable

```cpp
int& bad() {
    int local = 42;
    return local;    // UB: dangling reference after return
}
```

The caller receives a reference to stack memory that is no longer valid once `bad()` returns. Using that reference is UB.

## 8. Infinite Loops Without Side Effects

```cpp
while (true) {}   // UB if the compiler can prove no side effects
```

The C++ standard assumes all loops eventually terminate (or have observable side effects). A provably non-terminating, side-effect-free loop is UB, allowing the compiler to delete it or hoist code past it.

## Summary Table

| UB Source | Common Symptom | Sanitizer |
|---|---|---|
| Out-of-bounds access | Heap corruption, crash | ASan |
| Null/dangling dereference | Segfault | ASan |
| Signed overflow | Wrong math in release | UBSan |
| Strict aliasing | Misread values | UBSan |
| Data race | Flaky failures | TSan |
| Bad shift | Wrong bits | UBSan |
| Dangling reference | Crash on caller site | ASan |

## Pitfall: "It Works in Debug"

Debug builds often use `-O0` (no optimization). Many UB manifestations only appear when the optimizer makes assumptions. Always test release builds with sanitizers enabled.

> **Interview answer:** The most common UB sources are out-of-bounds access, null/dangling pointer dereference, signed integer overflow, strict aliasing violations, and data races. Each allows the compiler to generate surprising code because it assumes these conditions never occur.
