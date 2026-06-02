# Iterator Invalidation Rules

An iterator becomes **invalidated** when the container it points into is modified in a way that changes the memory or logical structure the iterator relied on. Using an invalidated iterator is undefined behavior — one of the most common sources of subtle bugs in C++ programs.

## Why Invalidation Happens

Containers store elements in memory. When you insert or erase elements, the container may:

1. **Reallocate** its internal buffer (e.g., `vector` growing beyond capacity).
2. **Shift elements** in memory (e.g., `vector` insert in the middle).
3. **Re-link nodes** in a node-based structure (less common, but erasure invalidates the erased node).

## Invalidation Rules by Container

| Container | Insert invalidates | Erase invalidates |
|---|---|---|
| `vector` | All iterators if reallocation; else iterators at/after insert point | Iterators at/after erase point |
| `deque` | All iterators (always) | All iterators (always) |
| `list` | Nothing | Only iterators to erased element |
| `forward_list` | Nothing | Only iterators to erased element |
| `set` / `map` | Nothing | Only iterators to erased element |
| `unordered_set` / `unordered_map` | All iterators on rehash; else nothing | Only iterators to erased element |

Memorize this table — it is a frequent interview topic.

## The Classic Bug: Erasing in a Loop

```cpp
#include <vector>
#include <iostream>

std::vector<int> v = {1, 2, 3, 4, 5};

// WRONG — erasing invalidates 'it' and increments a dangling iterator
for (auto it = v.begin(); it != v.end(); ++it) {
    if (*it % 2 == 0)
        v.erase(it);   // UB on the next iteration
}

// CORRECT — erase returns the next valid iterator
for (auto it = v.begin(); it != v.end(); ) {
    if (*it % 2 == 0)
        it = v.erase(it);  // advance via return value
    else
        ++it;
}
// v == {1, 3, 5}
```

## The Erase-Remove Idiom

For `vector` and `deque`, the idiomatic way to remove elements matching a predicate is the **erase-remove idiom**:

```cpp
#include <vector>
#include <algorithm>

std::vector<int> v = {1, 2, 3, 4, 5};

// std::remove shifts non-matching elements to the front, returns new logical end
auto new_end = std::remove_if(v.begin(), v.end(),
                              [](int x){ return x % 2 == 0; });
v.erase(new_end, v.end());   // chop off the "junk" tail
// v == {1, 3, 5}
```

C++20 collapses this into `std::erase_if(v, pred)`.

## vector Reserve and Invalidation

```cpp
#include <vector>

std::vector<int> v;
v.reserve(10);    // allocates capacity without changing size

auto it = v.begin();   // valid until capacity is exceeded

v.push_back(42);  // safe — no reallocation, it still valid
v.push_back(43);  // still safe (capacity is 10)
// ... after 10 pushes without reserve, the next push_back WILL reallocate
// and 'it' becomes invalid
```

`reserve` lets you pre-allocate capacity and avoid iterator invalidation due to growth — critical in performance-sensitive code.

## Invalidation with map / unordered_map

```cpp
#include <unordered_map>

std::unordered_map<int, int> m = {{1, 10}, {2, 20}};

auto it = m.find(1);   // valid

m.insert({3, 30});     // might trigger rehash — 'it' potentially invalidated!

// Safe: use the value before any further mutation
std::cout << it->second;   // UB if rehash occurred
```

Check `max_load_factor` and `bucket_count` to predict rehashes, or call `m.reserve(n)` upfront.

## Pitfalls at a Glance

- References and pointers into a container are subject to the **same** invalidation rules as iterators.
- `std::string` iterators are invalidated on any modification (treated like `vector<char>`).
- Range-based `for` loops internally use iterators; mutating the container inside the loop is unsafe unless you switch to an index-based loop.

> **Interview answer:** "Iterator invalidation occurs when a container modifies its internal structure after an iterator is taken. For `vector`, any insertion that causes reallocation invalidates all iterators; for node-based containers like `list` or `map`, only iterators to the erased node are invalidated. The fix is to use the return value of `erase`, or the erase-remove idiom."
