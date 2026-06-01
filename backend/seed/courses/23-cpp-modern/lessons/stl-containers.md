# STL Containers

The STL (Standard Template Library) ships with generic containers. They cover almost every shape of data you need.

## Sequence containers

| Container          | Backing       | When to use                          |
|--------------------|---------------|--------------------------------------|
| `std::vector<T>`   | dynamic array | **The default.** O(1) push_back, indexing |
| `std::array<T,N>`  | fixed array   | Compile-time-sized, on the stack     |
| `std::deque<T>`    | block array   | O(1) push at both ends               |
| `std::list<T>`     | doubly linked | Frequent middle insertion (rare)     |

```cpp
std::vector<int> v = {1, 2, 3};
v.push_back(4);
v.size();
v.empty();
v[0];
v.at(0);                  // bounds-checked, throws on overflow
v.front(); v.back();
v.pop_back();
v.clear();

for (int x : v) std::cout << x << ' ';
```

`std::vector` should be your default. It's cache-friendly, has O(1) push_back, and access is just pointer arithmetic.

## Associative containers

| Container                  | Ordering        | Lookup       |
|----------------------------|-----------------|--------------|
| `std::map<K, V>`           | sorted (RB-tree)| O(log n)     |
| `std::unordered_map<K, V>` | hash table      | O(1) amortized |
| `std::set<T>`              | sorted          | O(log n)     |
| `std::unordered_set<T>`    | hash table      | O(1)         |

```cpp
std::unordered_map<std::string, int> counts;
counts["apple"]++;            // creates entry with 0, increments to 1
counts.contains("apple");     // C++20
counts.at("apple");           // throws if missing
counts.erase("apple");

for (const auto& [key, value] : counts) ...
```

Use `unordered_map`/`unordered_set` unless you need iteration in sorted order.

## Container adapters

```cpp
std::stack<int>          // LIFO, defaults to deque
std::queue<int>          // FIFO, defaults to deque
std::priority_queue<int> // max-heap, defaults to vector
```

Thin wrappers — `push`, `pop`, `top` (or `front`/`back` for queue).

## Iterators

Every container has iterators:

```cpp
for (auto it = v.begin(); it != v.end(); ++it) {
    std::cout << *it;
}

// reverse
for (auto it = v.rbegin(); it != v.rend(); ++it) ...
```

You rarely write loops like this — use range-based `for` or algorithms.

## Initializing

```cpp
std::vector<int> v(10);             // 10 zeros
std::vector<int> v(10, 42);         // 10 forty-twos
std::vector<int> v = {1, 2, 3};
std::vector<int> v(other.begin(), other.end());
```

## emplace vs push

`emplace_back(args...)` constructs the element in place; `push_back(x)` copies/moves `x`. For complex types, `emplace_back` avoids a temporary:

```cpp
v.push_back(std::string("hello"));    // builds temporary, moves
v.emplace_back("hello");              // builds in place
```

## Reserve for known sizes

```cpp
std::vector<int> v;
v.reserve(1000);                      // pre-allocate; no growth reallocations
for (int i = 0; i < 1000; ++i) v.push_back(i);
```

Without `reserve`, vector grows geometrically (typically 2× or 1.5×). With it, you allocate once.

## std::string_view

A non-owning view into a string:

```cpp
void print(std::string_view s) {
    std::cout << s;
}

print("literal");
print(std::string("dynamic"));
print(some_string.substr(0, 5));
```

Cheap to copy (`{ptr, length}`), avoids unnecessary string copies in function signatures.

## When NOT to use the STL

- Embedded with tight memory budgets — STL allocations can surprise you.
- When you need a specific layout (game ECS, GPU buffers).
- When you have a measured profiling reason.

Otherwise, default to STL. Hand-rolling a linked list in 2025 is almost always the wrong call.
