# Standard Algorithms: find, sort, transform, accumulate

The `<algorithm>` and `<numeric>` headers provide more than 100 generic algorithms. Rather than rolling your own loops, prefer these functions — they are well-tested, often optimized by the standard library implementation, and immediately communicate intent to a reader.

## std::find and std::find_if

```cpp
#include <algorithm>
#include <vector>

std::vector<int> v = {3, 1, 4, 1, 5, 9};

// Linear search — returns iterator to first match, or end() if not found
auto it = std::find(v.begin(), v.end(), 4);
if (it != v.end())
    std::cout << "found at index " << std::distance(v.begin(), it) << "\n"; // 2

// Predicate version
auto big = std::find_if(v.begin(), v.end(), [](int x){ return x > 6; });
// *big == 9
```

`find` requires `==`; `find_if` accepts any callable returning `bool`. Complexity: O(n).

## std::sort

```cpp
#include <algorithm>
#include <vector>

std::vector<int> v = {5, 3, 8, 1, 2};

std::sort(v.begin(), v.end());                         // ascending: {1,2,3,5,8}
std::sort(v.begin(), v.end(), std::greater<int>{});    // descending: {8,5,3,2,1}

// Custom comparator for struct fields
struct Person { std::string name; int age; };
std::vector<Person> people = {{"Alice", 30}, {"Bob", 25}};
std::sort(people.begin(), people.end(),
          [](const Person& a, const Person& b){ return a.age < b.age; });
// people[0] == {"Bob", 25}
```

- Requires **random-access iterators**.
- Complexity: O(n log n) average (typically introsort).
- Not stable — equal elements may be reordered. Use `std::stable_sort` to preserve relative order.

## std::transform

`transform` applies a function to each element, writing the result to an output range.

```cpp
#include <algorithm>
#include <vector>
#include <string>
#include <cctype>

// Unary: square each element
std::vector<int> src = {1, 2, 3, 4};
std::vector<int> dst(src.size());
std::transform(src.begin(), src.end(), dst.begin(),
               [](int x){ return x * x; });
// dst == {1, 4, 9, 16}

// Binary: element-wise sum of two ranges
std::vector<int> a = {1, 2, 3}, b = {10, 20, 30};
std::vector<int> c(3);
std::transform(a.begin(), a.end(), b.begin(), c.begin(),
               [](int x, int y){ return x + y; });
// c == {11, 22, 33}

// String to uppercase
std::string s = "hello";
std::transform(s.begin(), s.end(), s.begin(),
               [](unsigned char c){ return std::toupper(c); });
// s == "HELLO"
```

The output iterator can alias the input (in-place transform is valid).

## std::accumulate

From `<numeric>`, `accumulate` folds a range with a binary operation.

```cpp
#include <numeric>
#include <vector>
#include <string>

std::vector<int> v = {1, 2, 3, 4, 5};

int sum     = std::accumulate(v.begin(), v.end(), 0);          // 15
int product = std::accumulate(v.begin(), v.end(), 1,
                              std::multiplies<int>{});          // 120

// Concatenate strings
std::vector<std::string> words = {"C++", " ", "is", " ", "fast"};
std::string sentence = std::accumulate(words.begin(), words.end(),
                                       std::string{});
// sentence == "C++ is fast"
```

The **init value** sets the starting accumulator and determines the return type. A common pitfall: passing `0` when summing `double` values causes integer arithmetic — pass `0.0` instead.

## Combining Algorithms: A Worked Example

Count the number of positive squares greater than 10:

```cpp
#include <algorithm>
#include <numeric>
#include <vector>

std::vector<int> data = {-3, 1, 4, -1, 5, 2};

std::vector<int> squares(data.size());
std::transform(data.begin(), data.end(), squares.begin(),
               [](int x){ return x * x; });
// squares == {9, 1, 16, 1, 25, 4}

int count = std::count_if(squares.begin(), squares.end(),
                          [](int x){ return x > 10; });
// count == 2  (16 and 25)
```

## Other Frequently Used Algorithms

| Algorithm | Header | What it does |
|---|---|---|
| `std::copy` | `<algorithm>` | Copy range to output iterator |
| `std::fill` | `<algorithm>` | Set all elements to a value |
| `std::count_if` | `<algorithm>` | Count elements matching predicate |
| `std::any_of` / `all_of` | `<algorithm>` | Boolean checks over a range |
| `std::min_element` / `max_element` | `<algorithm>` | Iterator to min/max |
| `std::partial_sum` | `<numeric>` | Running prefix sums |
| `std::iota` | `<numeric>` | Fill with incrementing values |

## Common Pitfalls

- Passing an empty output range to `transform` or `copy` — the output must have at least as many elements as the input (or use `back_inserter`).
- Forgetting that `sort` requires random-access iterators — you cannot sort a `std::list` directly; use `list::sort()` member function.
- `accumulate` processes left-to-right; subtraction and division are order-sensitive.

> **Interview answer:** "Standard algorithms operate on iterator ranges, separating algorithms from data structures. `sort` is O(n log n) introsort, `transform` maps a function over a range, and `accumulate` performs a left-fold. Prefer them over hand-written loops for clarity and correctness."
