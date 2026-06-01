# STL Algorithms and Lambdas

The `<algorithm>` header has 100+ generic functions that work on any iterator pair. Combine them with lambdas for short, expressive code.

## Lambdas

```cpp
auto sq = [](int x) { return x * x; };
auto add = [](int a, int b) { return a + b; };

std::vector<int> v = {1, 2, 3, 4, 5};
std::transform(v.begin(), v.end(), v.begin(), sq);
// v is now {1, 4, 9, 16, 25}
```

Captures:

```cpp
int n = 10;
auto less_than_n = [n](int x) { return x < n; };       // by value
auto add_to_n    = [&n](int x) { n += x; };            // by reference
auto generic     = [=](int x) { return x + n; };        // by value, all
auto everything  = [&](int x) { n += x; return n; };    // by reference, all
```

Mutable lambdas (modify by-value captures):

```cpp
auto counter = [count = 0]() mutable { return ++count; };
counter(); counter(); counter();    // 1, 2, 3
```

## Common algorithms

```cpp
#include <algorithm>
#include <numeric>

std::sort(v.begin(), v.end());
std::sort(v.begin(), v.end(), std::greater<>{});
std::sort(v.begin(), v.end(), [](auto& a, auto& b) { return a.score > b.score; });

auto it = std::find(v.begin(), v.end(), 42);            // ==
auto it2 = std::find_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; });

int total = std::accumulate(v.begin(), v.end(), 0);    // sum
int product = std::accumulate(v.begin(), v.end(), 1, std::multiplies<>{});

bool any_even = std::any_of(v.begin(), v.end(), [](int x) { return x % 2 == 0; });
bool all_pos = std::all_of(v.begin(), v.end(), [](int x) { return x > 0; });

std::count(v.begin(), v.end(), 5);
std::count_if(v.begin(), v.end(), [](int x) { return x > 10; });

auto [min, max] = std::minmax_element(v.begin(), v.end());

std::reverse(v.begin(), v.end());
std::shuffle(v.begin(), v.end(), gen);

v.erase(std::remove_if(v.begin(), v.end(),
                       [](int x) { return x % 2 == 0; }),
        v.end());                                       // erase-remove idiom
```

## C++20 Ranges

The ranges library makes the above much cleaner:

```cpp
#include <ranges>
namespace rg = std::ranges;
namespace rv = std::views;

auto result = v
    | rv::filter([](int x) { return x % 2 == 0; })
    | rv::transform([](int x) { return x * x; })
    | rg::to<std::vector>();           // C++23

int sum = std::ranges::fold_left(v, 0, std::plus<>{});   // C++23
```

Pipeable, lazy, and the algorithm names live in `std::ranges::` so you can pass containers directly without `begin()`/`end()`.

## Function objects

```cpp
#include <functional>

std::function<int(int)> f = [](int x) { return x + 1; };
auto bound = std::bind(some_function, std::placeholders::_1, 42);

// hashable lambdas as map keys (C++20)
std::unordered_map<int, std::function<int(int)>> handlers;
```

`std::function` is type-erased — useful when you store callbacks but slower than a templated function. Prefer templates when you can.

## A real-world example

```cpp
struct Order { int customer_id; double amount; std::string status; };

std::vector<Order> orders = ...;

// total paid amount per customer
std::unordered_map<int, double> totals;
for (const auto& o : orders) {
    if (o.status == "paid") totals[o.customer_id] += o.amount;
}

// top 10 customers
std::vector<std::pair<int, double>> items(totals.begin(), totals.end());
std::partial_sort(items.begin(), items.begin() + 10, items.end(),
                  [](auto& a, auto& b) { return a.second > b.second; });
items.resize(10);
```

Modern, allocation-light, runs fast.
