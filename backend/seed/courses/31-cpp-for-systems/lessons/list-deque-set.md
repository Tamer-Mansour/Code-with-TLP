# list, deque, set, and When to Use Them

`vector` and `map` cover 80% of use cases, but the remaining containers solve specific problems that the big two handle poorly. This lesson covers `std::list`, `std::deque`, and `std::set` — what they guarantee, what they cost, and when they earn their keep.

## std::list: Doubly-Linked List

`std::list<T>` is a doubly-linked list. Each node is an independent heap allocation containing `{prev*, next*, T}`.

```cpp
#include <list>

std::list<int> L = {1, 2, 3, 4, 5};

// O(1) insert anywhere given an iterator
auto it = std::find(L.begin(), L.end(), 3);
L.insert(it, 99);     // inserts 99 before 3 — O(1)
L.erase(it);          // removes 3 — O(1)
```

### When list Wins

- **O(1) insert/erase anywhere** with a valid iterator — useful in LRU cache implementations where you splice nodes between front and back.
- **Iterator and reference stability** — inserting or erasing does not invalidate *any* other iterators or references. `vector` cannot offer this.
- **`splice`** — move nodes between lists in O(1) without copying elements.

```cpp
std::list<int> a = {1, 2, 3};
std::list<int> b = {10, 20, 30};
// Move all of b before the '2' in a — O(1)
a.splice(std::next(a.begin()), b);
// a = {1, 10, 20, 30, 2, 3}, b = {}
```

### When list Loses

- **Cache misses everywhere** — each node is a separate allocation; traversal is pointer-chasing.
- **No random access** — `L[5]` is not legal; you must iterate.
- **Higher memory overhead** — two extra pointers per element (16 bytes on 64-bit) plus allocator overhead.

> In practice, `deque` or `vector` beats `list` for most real workloads due to cache effects. Use `list` only when you need stable iterators AND frequent mid-sequence modifications.

## std::deque: Double-Ended Queue

`std::deque<T>` (pronounced "deck") is a sequence container that supports **O(1) push and pop at both ends** while maintaining O(1) random access.

```cpp
#include <deque>

std::deque<int> dq;
dq.push_back(1);    // O(1)
dq.push_front(0);   // O(1) — vector cannot do this efficiently
dq.push_back(2);
std::cout << dq[1]; // O(1) random access — 1
dq.pop_front();     // O(1)
```

### Internal Layout: Segmented Buffer

`deque` is implemented as an array of fixed-size chunks ("pages") with an index map. This gives:
- O(1) amortised push/pop at either end (no element copying like `vector`).
- O(1) random access (two-level index lookup).
- **No single contiguous allocation** — `dq.data()` does not exist.

### When deque Is the Right Call

| Scenario | Container |
|---------|-----------|
| FIFO queue (front pop, back push) | `deque` or `queue<T, deque<T>>` |
| Stack (back push, back pop) | `vector` (faster) |
| Sliding window / buffer | `deque` |
| `std::queue` / `std::stack` defaults | `deque` / `deque` |

`std::queue` and `std::stack` are adapters that use `deque` and `vector` as their underlying containers by default.

## std::set: Ordered Unique Keys

`std::set<T>` is `std::map` without the value — it stores a sorted collection of unique keys. The internal structure is the same red-black tree.

```cpp
#include <set>

std::set<int> s = {5, 1, 3, 3, 2};   // {1, 2, 3, 5} — sorted, no duplicates
s.insert(4);                           // O(log N)
s.erase(2);                            // O(log N)
bool found = s.count(3);              // 1 (true)
auto it = s.lower_bound(3);           // iterator to first element >= 3
```

### Use Cases

- **Membership testing with order** — "is this key in the set?" + sorted iteration.
- **Eliminating duplicates while keeping order** — insert all elements, iterate.
- **Ordered event queues** — `set<pair<int,int>>` where first element is priority.

### unordered_set

Just as `unordered_map` is the hash version of `map`, `std::unordered_set<T>` is the hash version of `set`: O(1) average lookup, no ordering.

```cpp
#include <unordered_set>
std::unordered_set<std::string> seen;
seen.insert("hello");
if (!seen.count("hello")) { /* not a duplicate */ }
```

## Complexity Summary

| Container | Access | Insert (front) | Insert (back) | Insert (mid) | Find |
|-----------|:------:|:--------------:|:-------------:|:------------:|:----:|
| `vector` | O(1) | O(N) | O(1)* | O(N) | O(N) |
| `list` | O(N) | O(1) | O(1) | O(1)** | O(N) |
| `deque` | O(1) | O(1)* | O(1)* | O(N) | O(N) |
| `set` | O(log N) | — | — | O(log N) | O(log N) |

\* amortised  ** given iterator

## Worked Example: LRU Cache Skeleton

The classic LRU cache uses `list` + `unordered_map` together:

```cpp
struct LRU {
    int cap;
    std::list<std::pair<int,int>> order;  // front = most recent
    std::unordered_map<int, std::list<std::pair<int,int>>::iterator> index;

    int get(int key) {
        auto it = index.find(key);
        if (it == index.end()) return -1;
        order.splice(order.begin(), order, it->second); // O(1) move to front
        return it->second->second;
    }
};
```

`list::splice` is the key — it moves a node to the front in O(1) without invalidating the stored iterator.

> **Interview answer:** Use `list` when you need O(1) mid-sequence insert/erase with stable iterators; use `deque` when you need O(1) push/pop at both ends; use `set` when you need a sorted collection of unique values with O(log N) membership testing.
