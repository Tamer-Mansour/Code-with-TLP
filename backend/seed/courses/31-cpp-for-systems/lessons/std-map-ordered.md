# std::map: Ordered, Tree-Based Lookup

`std::map<Key, Value>` is the STL's sorted associative container. It maps unique keys to values, keeps keys in ascending order at all times, and guarantees O(log N) for every modifying and lookup operation. Behind the scenes it is a **red-black tree** — a self-balancing binary search tree.

## Basic Usage

```cpp
#include <map>
#include <string>
#include <iostream>

int main() {
    std::map<std::string, int> scores;

    scores["Alice"] = 95;
    scores["Bob"]   = 87;
    scores["Carol"] = 92;

    // Iteration is always in key order (Alice, Bob, Carol)
    for (const auto& [name, score] : scores) {
        std::cout << name << ": " << score << "\n";
    }
}
```

Output:
```
Alice: 95
Bob: 87
Carol: 92
```

## Lookup Methods

| Method | Behaviour on miss | Return type |
|--------|------------------|-------------|
| `m[key]` | **Inserts** a default-constructed value | `Value&` |
| `m.at(key)` | Throws `std::out_of_range` | `Value&` |
| `m.find(key)` | Returns `m.end()` | `iterator` |
| `m.count(key)` | Returns 0 or 1 | `size_t` |
| `m.contains(key)` (C++20) | Returns `false` | `bool` |

The `operator[]` default-insert behaviour is a frequent source of bugs:

```cpp
std::map<std::string, int> m;
// This inserts "Dave" -> 0, even though we only meant to check!
if (m["Dave"] == 0) { /* ... */ }

// Safe alternatives:
if (m.count("Dave") == 0) { /* not found */ }
if (m.find("Dave") == m.end()) { /* not found */ }
```

## Insertion Methods

```cpp
m.insert({"Eve", 78});               // insert_or_ignore
m.insert_or_assign("Eve", 80);       // update if present (C++17)
m.emplace("Frank", 88);              // construct in-place
auto [it, ok] = m.emplace("Frank", 99); // ok=false, already exists
```

## Red-Black Tree Internals

Each node in the map stores:
- The `std::pair<const Key, Value>` (the value_type).
- Left child, right child, parent pointers.
- A color bit (red or black).

This means **every element is a separate heap allocation** — a point-of-difference from `vector` which allocates a single contiguous block. The tree ensures the longest path is at most 2× the shortest, giving guaranteed O(log N) worst-case performance.

```
         Bob
        /   \
     Alice  Carol
               \
               Eve
```

## Complexity Summary

| Operation | Complexity |
|-----------|-----------|
| Insert | O(log N) |
| Erase | O(log N) |
| Find / at | O(log N) |
| Iteration (all) | O(N) |
| Lower / upper bound | O(log N) |

## Range Queries: A Killer Feature

`std::map` exposes `lower_bound` and `upper_bound`, enabling efficient range queries that `unordered_map` cannot provide:

```cpp
std::map<int, std::string> events;
// ... populate with timestamps ...

// Find all events in [100, 200)
auto lo = events.lower_bound(100);
auto hi = events.lower_bound(200);
for (auto it = lo; it != hi; ++it) {
    std::cout << it->first << " -> " << it->second << "\n";
}
```

## Custom Comparators

The third template parameter lets you change the ordering:

```cpp
// Case-insensitive map
auto ci_less = [](const std::string& a, const std::string& b) {
    return std::lexicographical_compare(
        a.begin(), a.end(), b.begin(), b.end(),
        [](char x, char y){ return tolower(x) < tolower(y); });
};

std::map<std::string, int, decltype(ci_less)> m(ci_less);
m["Alice"] = 1;
m["alice"] = 2;  // same key — updates, not inserts
std::cout << m.size(); // 1
```

## Common Pitfalls

- **Accidental insertion via `[]`** — in read-only code always use `find` or `contains`.
- **Mutating the key** — keys are `const`; to change a key you must erase and re-insert.
- **Cache unfriendliness** — tree nodes are scattered across the heap; expect cache misses on large maps. For hot paths, `unordered_map` or a sorted `vector` of pairs may be faster.

## Worked Example: Histogram

```cpp
#include <map>
#include <string>
#include <vector>

std::map<char, int> char_histogram(const std::string& s) {
    std::map<char, int> hist;
    for (char c : s) ++hist[c];   // operator[] inserts 0, then ++
    return hist;
}
```

> **Interview answer:** `std::map` is a red-black tree giving O(log N) insert, erase, and lookup with keys always sorted — use it when you need ordered iteration or range queries; the cost over `unordered_map` is the log factor and poor cache locality.
