# std::vector vs C Array vs std::array

Three array-like abstractions live side by side in C++. Choosing the right one is not style — it has concrete performance, safety, and API implications.

## At a Glance

| Feature | C array `T[N]` | `std::array<T, N>` | `std::vector<T>` |
|--------|:---:|:---:|:---:|
| Size known at compile time | Yes | Yes | No |
| Heap allocation | No | No | Yes |
| Size stored at runtime | No | No | Yes |
| Bounds checking (`.at()`) | No | Yes | Yes |
| STL iterator support | Pointer-based | Full | Full |
| Can return from function safely | No (decays to ptr) | Yes | Yes |
| Resize at runtime | No | No | Yes |

## C Array: The Unsafe Baseline

```cpp
int arr[5] = {1, 2, 3, 4, 5};
int* p = arr;           // decays to pointer — size is lost
void foo(int a[], int n);   // must pass size separately
```

C arrays decay to pointers on almost any value context, discarding size information. They cannot be returned from functions safely (returning a local array returns a dangling pointer) and have no bounds checking.

Use C arrays only when interfacing with C APIs or in extremely low-level, size-critical code (e.g., embedded firmware with no heap).

## std::array: Zero-Cost Wrapper Around C Array

`std::array<T, N>` is a lightweight wrapper that gives C arrays STL citizenship:

```cpp
#include <array>
#include <algorithm>

std::array<int, 5> a = {5, 2, 8, 1, 9};
std::sort(a.begin(), a.end());       // works with any STL algorithm
std::cout << a.size();               // 5 — never lost
std::cout << a.at(10);               // throws std::out_of_range
```

Key properties:
- **Stack-allocated** — no heap, no dynamic allocation overhead.
- **Size is a compile-time constant** — `std::array::size()` is `constexpr`.
- **Aggregate-initialized** — works in `constexpr` contexts.
- **Copyable and returnable** — unlike C arrays.

The layout is exactly `T[N]` in memory — the compiler generates the same machine code as a C array when optimised.

```cpp
constexpr std::array<int, 4> LUT = {0, 1, 4, 9};
static_assert(LUT[3] == 9);   // compile-time evaluation
```

## std::vector: Heap-Allocated, Dynamically Sized

`std::vector` is the right choice when the number of elements is not known at compile time:

```cpp
#include <vector>

int n;
std::cin >> n;
std::vector<int> v(n, 0);   // runtime size — impossible with std::array
v.push_back(42);             // grow beyond initial size
```

The costs vs `std::array`:
- One heap allocation per vector (plus more on reallocation).
- Three words of overhead (pointer, size, capacity) vs zero for `std::array`.
- Data is on the heap — a cache miss to reach it if the vector object is on the stack.

## Memory Layout Comparison

```
std::array<int, 4>          std::vector<int> (size=4, cap=4)
 Stack                        Stack            Heap
┌───┬───┬───┬───┐           ┌────────┐        ┌───┬───┬───┬───┐
│ 1 │ 2 │ 3 │ 4 │           │ ptr ───┼───────►│ 1 │ 2 │ 3 │ 4 │
└───┴───┴───┴───┘           │ size=4 │        └───┴───┴───┴───┘
                             │ cap=4  │
                             └────────┘
```

## Decision Guide

```
Do you know the size at compile time?
  Yes ──► Is the size very large (risk of stack overflow)?
            No  ──► std::array<T, N>
            Yes ──► std::vector<T> with reserve()
  No  ──► std::vector<T>

Are you calling a C API that expects T*?
  ──► Use .data() on either std::array or std::vector — both guarantee contiguous storage.
```

## Passing to Functions

```cpp
// Accepts any contiguous range (C++20 span, or use .data() + .size())
void process(const int* data, size_t n);

std::array<int, 4> a = {1,2,3,4};
std::vector<int>   v = {5,6,7,8};

process(a.data(), a.size());   // both work identically
process(v.data(), v.size());
```

## Common Pitfalls

- **Returning a C array** — undefined behaviour; the caller gets a dangling pointer.
- **Using `new int[N]`** when `std::vector` or `std::array` would do — raw `new[]` gives you no RAII and no iterator support.
- **Stack overflow with large `std::array`** — `std::array<double, 1000000>` on the stack will crash; put it on the heap via `std::vector` or `make_unique`.

> **Interview answer:** Use `std::array` when the size is fixed at compile time and you need stack allocation with no overhead; use `std::vector` when the size is dynamic or unknown at compile time; avoid raw C arrays in new C++ code because they lose size information on decay.
