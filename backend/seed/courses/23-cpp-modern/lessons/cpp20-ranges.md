# C++20 Ranges and Views

The Ranges library (`<ranges>`) in C++20 replaces the begin/end iterator-pair idiom with composable, lazy **views**. Code becomes more readable and often avoids unnecessary intermediate copies.

## The Problem with Iterator Pairs

Classic STL algorithms take `(begin, end)` pairs. Chaining operations requires temporary containers:

```cpp
// Old style: filter even numbers then square them
std::vector<int> v = {1, 2, 3, 4, 5, 6};
std::vector<int> evens, squares;

std::copy_if(v.begin(), v.end(), std::back_inserter(evens),
             [](int x){ return x % 2 == 0; });   // {2, 4, 6}

std::transform(evens.begin(), evens.end(), std::back_inserter(squares),
               [](int x){ return x * x; });       // {4, 16, 36}
```

## Ranges: Composable Pipelines

```cpp
#include <ranges>
#include <vector>
#include <iostream>

int main() {
    std::vector<int> v = {1, 2, 3, 4, 5, 6};

    auto result = v
        | std::views::filter([](int x){ return x % 2 == 0; })
        | std::views::transform([](int x){ return x * x; });

    for (int x : result)
        std::cout << x << " ";   // 4 16 36
}
```

`result` is a **lazy view** — no intermediate `std::vector` is allocated. Elements are computed on demand as you iterate.

## Common Views

| View | Effect |
|------|--------|
| `std::views::filter(pred)` | Keep only elements satisfying pred |
| `std::views::transform(f)` | Apply f to each element |
| `std::views::take(n)` | First n elements |
| `std::views::drop(n)` | Skip first n elements |
| `std::views::reverse` | Iterate in reverse |
| `std::views::iota(a, b)` | Generate integers [a, b) |
| `std::views::enumerate` (C++23) | Pairs of (index, value) |
| `std::views::zip` (C++23) | Zip multiple ranges |
| `std::views::split(delim)` | Split range on delimiter |

## Range Algorithms

C++20 also provides `std::ranges::` versions of all STL algorithms that accept a range directly:

```cpp
std::vector<int> v = {3, 1, 4, 1, 5, 9};

std::ranges::sort(v);                 // sort the whole range
std::ranges::sort(v, std::greater{});  // descending

auto it = std::ranges::find(v, 4);    // no begin/end needed
```

These versions also accept **projections** — a function applied to elements before comparing:

```cpp
struct Person { std::string name; int age; };
std::vector<Person> people = {{"Alice", 30}, {"Bob", 25}};

std::ranges::sort(people, {}, &Person::age);  // sort by age
```

## Lazy Evaluation Example

Views are lazy — nothing runs until you iterate:

```cpp
auto first10squares = std::views::iota(1)              // 1, 2, 3, ... (infinite)
                    | std::views::transform([](int x){ return x*x; })
                    | std::views::take(10);

for (int sq : first10squares)
    std::cout << sq << " ";   // 1 4 9 16 25 36 49 64 81 100
```

## Materializing a View into a Container

Use `std::ranges::to<std::vector>` (C++23) or the manual pattern:

```cpp
// C++20 manual
std::vector<int> v;
std::ranges::copy(result, std::back_inserter(v));

// C++23
auto v2 = result | std::ranges::to<std::vector>();
```

## Key Takeaways

- Ranges pipelines (`|`) express data transformations without intermediate allocations.
- Views are lazy — they do not compute anything until iterated.
- `std::ranges::` algorithm overloads accept whole ranges and support projections.
- For production code today, ranges work well in GCC 10+, Clang 13+, and MSVC 2019 16.9+.
