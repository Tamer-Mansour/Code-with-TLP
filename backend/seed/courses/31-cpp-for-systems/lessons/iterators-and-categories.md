# Iterators and Their Categories

An iterator is an object that behaves like a pointer — it points into a sequence and lets you move through it. The C++ standard library defines **five iterator categories** that form a hierarchy of capability. Knowing which category a given iterator belongs to tells you exactly what operations you can call and what complexity to expect.

## The Five Categories

| Category | Move | Read | Write | Random jump |
|---|---|---|---|---|
| Input | forward only | once | no | no |
| Output | forward only | no | once | no |
| Forward | forward only | multi | yes | no |
| Bidirectional | forward + backward | multi | yes | no |
| Random Access | forward + backward | multi | yes | yes (`it + n`, `it[n]`) |

C++20 added a sixth, **Contiguous**, which additionally guarantees that elements lie in a consecutive block of memory (like `std::vector` or plain arrays).

## Why Categories Matter

Algorithms in `<algorithm>` advertise their minimum required category. `std::sort` needs random-access iterators; calling it on a `std::list` (bidirectional) is a compile error. `std::advance` is O(1) for random-access but O(n) for lesser categories because it must step one-by-one.

```cpp
#include <iterator>  // std::advance, std::distance
#include <list>
#include <vector>

std::vector<int> v = {1, 2, 3, 4, 5};
auto it = v.begin();
std::advance(it, 3);   // O(1) — random access
// *it == 4

std::list<int> lst = {1, 2, 3, 4, 5};
auto lit = lst.begin();
std::advance(lit, 3);  // O(n) — bidirectional, steps one at a time
```

## Iterator Traits

The type system uses `std::iterator_traits<It>` to introspect an iterator at compile time:

```cpp
#include <iterator>
#include <type_traits>

template <typename It>
void inspect(It) {
    using Cat = typename std::iterator_traits<It>::iterator_category;
    if constexpr (std::is_same_v<Cat, std::random_access_iterator_tag>) {
        // fast path
    }
}
```

Key nested types exposed by `iterator_traits`:

- `value_type` — the type the iterator dereferences to
- `difference_type` — signed integer type for distances (`ptrdiff_t` usually)
- `pointer`, `reference`
- `iterator_category` — one of the five tag structs

## Common Iterator Sources

- `container.begin()` / `container.end()` — typical range
- `std::istream_iterator<T>` — input iterator over a stream
- `std::ostream_iterator<T>` — output iterator into a stream
- `std::back_insert_iterator` (via `std::back_inserter`) — output iterator that calls `push_back`
- `std::reverse_iterator` — wraps any bidirectional iterator and reverses direction

```cpp
#include <algorithm>
#include <vector>
#include <iterator>

std::vector<int> src = {1, 2, 3};
std::vector<int> dst;

// back_inserter gives an output iterator; copy needs only InputIterator + OutputIterator
std::copy(src.begin(), src.end(), std::back_inserter(dst));
// dst == {1, 2, 3}
```

## Worked Example: Generic Distance Function

```cpp
#include <iterator>

// Efficient for random access, linear otherwise — mirrors std::distance
template <typename It>
typename std::iterator_traits<It>::difference_type
my_distance(It first, It last) {
    if constexpr (std::is_same_v<
            typename std::iterator_traits<It>::iterator_category,
            std::random_access_iterator_tag>) {
        return last - first;          // O(1)
    } else {
        typename std::iterator_traits<It>::difference_type n = 0;
        while (first != last) { ++first; ++n; }
        return n;                     // O(n)
    }
}
```

## Common Pitfalls

- Comparing iterators from **different containers** is undefined behavior.
- Dereferencing `end()` is UB — it is a one-past-the-end sentinel.
- Input iterators are **single-pass**: once you read and advance, the old position is gone (e.g., `istream_iterator`).
- Do not assume `++it` and `it++` are equivalent in performance; prefer pre-increment (`++it`) to avoid creating a temporary.

> **Interview answer:** "Iterator categories describe a hierarchy of capabilities — random-access is the most powerful, input/output are the most restricted. The category controls which algorithms accept a given iterator and what complexity guarantees apply."
