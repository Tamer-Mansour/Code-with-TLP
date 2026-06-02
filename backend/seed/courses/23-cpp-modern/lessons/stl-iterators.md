# STL Iterators and Iterator Categories

Iterators are the glue between containers and algorithms in the STL. An iterator is an object that acts like a pointer: you dereference it to get a value and increment it to advance to the next element. Algorithms are written in terms of iterators, so they work with any conforming container.

## Iterator Categories

The STL defines a hierarchy of iterator categories. Each level adds capabilities:

| Category | Supports | Example sources |
|----------|----------|-----------------|
| **Input** | Read once, forward only | `std::istream_iterator` |
| **Output** | Write once, forward only | `std::ostream_iterator`, `std::back_inserter` |
| **Forward** | Read/write, multiple passes | `std::forward_list` |
| **Bidirectional** | Forward + backward (`--`) | `std::list`, `std::map` |
| **Random Access** | Jump by offset (`+n`, `-n`, `[]`) | `std::vector`, `std::deque`, arrays |
| **Contiguous** (C++17) | Random access + contiguous memory | `std::vector`, `std::array`, raw arrays |

Algorithms document which category they need. `std::sort` requires random-access; `std::find` only needs input.

## Using Iterators

```cpp
#include <vector>
#include <algorithm>
#include <iostream>

int main() {
    std::vector<int> v = {3, 1, 4, 1, 5, 9};

    // begin() / end() give iterator range [begin, end)
    auto it = v.begin();
    std::cout << *it << "\n";   // 3
    ++it;
    std::cout << *it << "\n";   // 1

    // Range-based for desugars to iterators
    for (int x : v) std::cout << x << " ";   // 3 1 4 1 5 9

    // Passing iterator pairs to algorithms
    std::sort(v.begin(), v.end());
    std::for_each(v.cbegin(), v.cend(),
                  [](int x){ std::cout << x << " "; });
}
```

## Reverse Iterators

```cpp
std::vector<int> v = {1, 2, 3, 4, 5};
for (auto it = v.rbegin(); it != v.rend(); ++it)
    std::cout << *it << " ";   // 5 4 3 2 1
```

`rbegin()` points to the last element; `++` advances toward the front.

## Insert Iterators

Insert iterators let algorithms write into a container by inserting rather than overwriting:

```cpp
#include <iterator>
std::vector<int> src = {1, 2, 3};
std::vector<int> dst;
std::copy(src.begin(), src.end(), std::back_inserter(dst));
// dst == {1, 2, 3}
```

| Adaptor | Inserts at |
|---------|-----------|
| `std::back_inserter(c)` | Back (`push_back`) |
| `std::front_inserter(c)` | Front (`push_front`) |
| `std::inserter(c, pos)` | Before `pos` |

## Stream Iterators

```cpp
#include <iterator>
#include <sstream>

std::istringstream ss("1 2 3 4 5");
std::istream_iterator<int> first(ss), last;
std::vector<int> v(first, last);   // reads all ints from stream
```

## Iterator Arithmetic (Random-Access Only)

```cpp
std::vector<int> v = {10, 20, 30, 40};
auto it = v.begin();
it += 2;                   // points to 30
std::cout << *(it - 1);    // 20
std::cout << v.end() - v.begin();   // 4 (size)
```

## C++20: Ranges and Sentinels

C++20's `<ranges>` library introduces **sentinels** — an end marker that does not have to be the same type as the iterator. This allows lazy ranges and infinite generators:

```cpp
#include <ranges>
#include <iostream>

auto squares = std::views::iota(1, 10)
             | std::views::transform([](int x){ return x * x; });

for (int sq : squares)
    std::cout << sq << " ";   // 1 4 9 16 25 36 49 64 81
```

Ranges are covered in depth in the C++20 module.

## Key Takeaways

- Iterators abstract container traversal behind a pointer-like interface.
- Algorithms are parameterized on iterator categories — use the right container for the required category.
- `begin()`/`end()` return half-open ranges `[begin, end)`.
- Insert iterators bridge algorithms that produce output with containers that grow on demand.
