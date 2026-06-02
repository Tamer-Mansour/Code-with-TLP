# std::vector: Growth, Capacity, and Reallocation

`std::vector` is C++'s workhorse sequence container — a heap-allocated, contiguous array that grows automatically. Knowing its internal mechanics separates engineers who use it from engineers who use it *correctly*.

## What vector Stores

Internally, a vector maintains three pointers (or equivalent):

```
[ data ptr ]  ──►  [ e0 | e1 | e2 | e3 | __ | __ ]
[ size      ]  = 4
[ capacity  ]  = 6
```

- **size** — the number of live elements.
- **capacity** — the number of elements that fit in the current allocation before a reallocation is needed.

```cpp
#include <vector>
#include <iostream>

int main() {
    std::vector<int> v;
    v.push_back(1);
    v.push_back(2);
    v.push_back(3);
    std::cout << v.size()     << "\n";  // 3
    std::cout << v.capacity() << "\n";  // likely 4 (implementation-defined)
}
```

## The Growth Factor

When `size == capacity` and you call `push_back`, the vector must reallocate:

1. Allocate a new buffer — typically **2× the current capacity** (GCC/Clang) or **1.5×** (MSVC).
2. **Move-construct** existing elements into the new buffer (or copy if move is not available).
3. Destroy the old elements and free the old buffer.

This is O(N) for a single reallocation, but amortized O(1) per `push_back` over N insertions because the doubling strategy ensures each element is moved at most O(log N) times.

## Reallocation Invalidates Everything

Any operation that changes `capacity` invalidates **all** iterators, pointers, and references into the vector:

```cpp
std::vector<int> v = {1, 2, 3};
int* p = &v[0];       // raw pointer to first element
v.push_back(4);       // may reallocate!
// p is now dangling — undefined behaviour to dereference
```

This is one of the most common bugs when mixing raw pointers with vectors.

## Reserving Capacity Upfront

If you know the final size (or a good upper bound), call `reserve` before filling the vector:

```cpp
std::vector<int> v;
v.reserve(1000);      // single allocation, no reallocation during push_backs

for (int i = 0; i < 1000; ++i)
    v.push_back(i);   // zero reallocations
```

`reserve` sets capacity but **not** size. Elements are not default-constructed.

## resize vs reserve

| Function | Changes size? | Changes capacity? | Constructs elements? |
|---------|:---:|:---:|:---:|
| `reserve(n)` | No | Yes (if n > cap) | No |
| `resize(n)` | Yes | Yes (if needed) | Yes (default/zero) |
| `shrink_to_fit()` | No | Might reduce | No |

```cpp
std::vector<int> v;
v.resize(5);          // v = {0, 0, 0, 0, 0}, size=5, cap>=5
v.reserve(20);        // size still 5, cap>=20
```

## emplace_back vs push_back

`emplace_back` constructs the element **in-place** inside the vector's buffer, avoiding a copy or move:

```cpp
struct Point { int x, y; };

std::vector<Point> pts;
pts.push_back({1, 2});       // constructs a temporary, then moves it in
pts.emplace_back(3, 4);      // constructs directly — no temporary
```

For small trivial types the difference is negligible, but for complex objects `emplace_back` can be meaningfully faster.

## Common Pitfalls

- **Holding iterators across push_back** — reallocation silently invalidates them.
- **Using `[]` without bounds checking** — use `.at()` during debugging; it throws `std::out_of_range`.
- **Forgetting `reserve` in tight loops** — causes O(log N) allocations where zero were needed.
- **`clear()` does not free memory** — size becomes 0 but capacity stays. Use `v = {}` or `std::vector<T>().swap(v)` to release memory.

## Worked Example: Building a Filtered List

```cpp
#include <vector>
#include <string>

std::vector<std::string> filter_long(const std::vector<std::string>& words,
                                     size_t min_len) {
    std::vector<std::string> result;
    result.reserve(words.size());   // worst-case reservation
    for (const auto& w : words)
        if (w.size() >= min_len)
            result.push_back(w);
    result.shrink_to_fit();         // release excess
    return result;                  // NRVO — no copy
}
```

> **Interview answer:** `push_back` is amortized O(1) because the geometric growth factor (2×) bounds the total number of copies across all insertions to O(N); a reallocation is expensive but happens exponentially less often as the vector grows.
