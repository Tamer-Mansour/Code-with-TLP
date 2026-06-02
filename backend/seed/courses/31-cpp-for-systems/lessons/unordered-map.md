# std::unordered_map and Hashing

`std::unordered_map<Key, Value>` is the STL's hash table. It trades the guaranteed ordering of `std::map` for average-case **O(1)** lookup, insert, and erase. For most key–value workloads it is the faster choice — but only if you understand what happens when the hash is bad.

## Basic Usage

```cpp
#include <unordered_map>
#include <string>
#include <iostream>

int main() {
    std::unordered_map<std::string, int> freq;

    for (const char* word : {"cat", "dog", "cat", "fish", "dog", "cat"})
        ++freq[word];

    // Iteration order is unspecified
    for (const auto& [word, count] : freq)
        std::cout << word << ": " << count << "\n";
}
```

## Internal Structure: Bucket Array + Chains

The hash table is an array of **buckets**. Each bucket is a linked list (or similar) of entries whose keys hash to the same index.

```
buckets:
 [0] -> (empty)
 [1] -> "cat" -> nullptr
 [2] -> "fish" -> nullptr
 [3] -> "dog" -> nullptr
 [4] -> (empty)
```

The bucket index is computed as:

```
index = hash(key) % bucket_count
```

Insertion, lookup, and erase all require:
1. Compute `hash(key)` — O(key length) for strings.
2. Index into the bucket array — O(1), cache-friendly.
3. Walk the chain — O(1) average if load factor is controlled.

## Load Factor and Rehashing

The **load factor** is `size / bucket_count`. When it exceeds `max_load_factor` (default 1.0), the table **rehashes**:

1. Allocate a new bucket array (typically 2× larger).
2. Re-insert every existing key into the new table.

This is O(N) and invalidates **all** iterators. Like `vector::reserve`, you can pre-empt rehashing:

```cpp
std::unordered_map<int, int> m;
m.reserve(10000);        // pre-allocates enough buckets for 10000 elements
m.max_load_factor(0.7);  // rehash when 70% full (improves collision rate)
```

## Complexity

| Operation | Average | Worst case |
|-----------|:-------:|:----------:|
| Insert | O(1) | O(N) |
| Erase | O(1) | O(N) |
| Find | O(1) | O(N) |
| Rehash | — | O(N) |

Worst case occurs when all keys hash to the same bucket (a pathological hash or a hash-flooding attack).

## std::hash and Custom Types

The standard library provides `std::hash` specialisations for all built-in types, `std::string`, and `std::string_view`. For custom types you must provide a hasher:

```cpp
struct Point { int x, y; };

struct PointHash {
    size_t operator()(const Point& p) const noexcept {
        // Combine hashes with XOR + bit shift (simple, not cryptographic)
        size_t hx = std::hash<int>{}(p.x);
        size_t hy = std::hash<int>{}(p.y);
        return hx ^ (hy << 32) ^ (hy >> 32);
    }
};

struct PointEq {
    bool operator()(const Point& a, const Point& b) const noexcept {
        return a.x == b.x && a.y == b.y;
    }
};

std::unordered_map<Point, std::string, PointHash, PointEq> grid;
grid[{0, 0}] = "origin";
```

## Hash Quality Matters

A poor hash causes **clustering** — many keys in the same bucket, degrading to O(N) lookup:

```cpp
// Bad hasher — all integers hash to 0!
struct BadHash {
    size_t operator()(int) const { return 0; }
};
std::unordered_map<int, int, BadHash> m;
// Every lookup is O(N) linear scan
```

For integer keys in competitive programming, a common trick is to XOR with a random seed to prevent hash-flooding:

```cpp
struct SafeIntHash {
    static const size_t SEED;
    size_t operator()(int x) const {
        return std::hash<int>{}(x) ^ SEED;
    }
};
```

## Lookup API

The API mirrors `std::map` closely:

```cpp
auto it = m.find("key");
if (it != m.end()) {
    std::cout << it->second;
}
bool exists = m.contains("key");  // C++20
int val = m.at("key");            // throws if missing
m["new_key"] = 42;                // inserts default if missing
```

## Common Pitfalls

- **No ordering** — do not rely on iteration order; it can change after a rehash.
- **Iterator invalidation on rehash** — even a `[]` insertion that triggers rehash kills all iterators.
- **Hashing `float`/`double` keys** — legal but fragile: `0.0` and `-0.0` compare equal but may have different bit patterns; prefer integer or string keys.
- **Using user-defined types without a custom hash** — fails to compile; you must specialise `std::hash` or pass a hasher.

> **Interview answer:** `std::unordered_map` is a hash table with average O(1) insert and lookup; worst case is O(N) when all keys collide into one bucket, so a good hash function and a bounded load factor are essential for predictable performance.
