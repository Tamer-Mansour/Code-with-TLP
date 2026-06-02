# STL Overview: Containers, Iterators, Algorithms

The C++ Standard Template Library (STL) is a collection of generic data structures and algorithms that ship with every conforming C++ compiler. Understanding the STL is non-negotiable for systems programming: it gives you battle-tested, cache-aware building blocks that replace hand-rolled linked lists, hash tables, and sort routines.

## Three Pillars of the STL

The STL is built around three cooperating concepts:

| Pillar | What it provides | Examples |
|--------|-----------------|---------|
| **Containers** | Store and own objects | `vector`, `map`, `unordered_map`, `list`, `set` |
| **Iterators** | Uniform traversal of any container | `begin()`, `end()`, `rbegin()` |
| **Algorithms** | Generic operations on iterator ranges | `std::sort`, `std::find`, `std::transform` |

These three pillars are deliberately decoupled. An algorithm like `std::sort` does not know about `vector`; it only knows that it receives two iterators that satisfy the *RandomAccessIterator* concept. This lets you swap the container without rewriting the algorithm.

## Containers at a Glance

STL containers divide into three broad families:

- **Sequence containers** — maintain insertion order: `vector`, `array`, `deque`, `list`, `forward_list`.
- **Associative containers** — sorted by key, backed by a red-black tree: `map`, `set`, `multimap`, `multiset`.
- **Unordered associative containers** — hash-table backed, no ordering guarantee: `unordered_map`, `unordered_set`.

## Iterators: The Glue

Every container exposes a nested `iterator` type and `begin()`/`end()` member functions. Algorithms operate on half-open ranges `[begin, end)`.

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

int main() {
    std::vector<int> v = {5, 2, 8, 1, 9};

    std::sort(v.begin(), v.end());          // algorithm + iterators

    for (auto it = v.begin(); it != v.end(); ++it) {
        std::cout << *it << " ";            // 1 2 5 8 9
    }
}
```

Range-based `for` (C++11) is syntactic sugar over the iterator protocol:

```cpp
for (int x : v) { std::cout << x << " "; }
```

## Algorithms: Write Once, Use Everywhere

`<algorithm>` contains over 80 functions. A few you'll reach for constantly:

```cpp
#include <algorithm>
#include <numeric>

std::sort(v.begin(), v.end());           // O(N log N) intro-sort
auto it = std::find(v.begin(), v.end(), 8);  // linear search
int sum = std::accumulate(v.begin(), v.end(), 0);  // fold
std::reverse(v.begin(), v.end());
bool any = std::any_of(v.begin(), v.end(), [](int x){ return x > 5; });
```

All algorithms work with raw pointers too, because pointers satisfy the iterator contract.

## The Iterator Category Ladder

Algorithms advertise complexity guarantees through iterator categories:

| Category | Supports | Example container |
|----------|---------|-------------------|
| RandomAccess | `it + n`, `it[n]` | `vector`, `array` |
| Bidirectional | `--it` | `list`, `map` |
| Forward | `++it` | `forward_list` |
| Input / Output | single-pass | streams |

`std::sort` requires RandomAccess, so you cannot sort a `list` directly — use `list::sort()` instead.

## Common Pitfalls

- **Iterator invalidation** — many operations (e.g., `vector::push_back` triggering a reallocation) invalidate existing iterators. Always re-acquire iterators after mutating a container.
- **Signed/unsigned mismatch** — `size()` returns `size_t` (unsigned). Comparing it to an `int` loop variable triggers warnings and potential bugs.
- **Forgetting `<algorithm>`** — algorithms live in `<algorithm>`, not in the container headers.

## Worked Example: Sort and Deduplicate

```cpp
#include <vector>
#include <algorithm>

std::vector<int> dedup(std::vector<int> v) {
    std::sort(v.begin(), v.end());
    v.erase(std::unique(v.begin(), v.end()), v.end());
    return v;
}
```

`std::unique` collapses consecutive duplicates to the front and returns an iterator past the last unique element. `erase` then removes the garbage tail.

> **Interview answer:** The STL separates *what data is stored* (containers) from *how you traverse it* (iterators) and *what you do with it* (algorithms), so each can evolve independently and every algorithm works on any conforming container.
