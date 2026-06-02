# Quiz: C++20 Features

**Q1. Which C++20 feature replaces the need for `enable_if` and SFINAE to constrain templates?**
- [ ] Ranges
- [x] Concepts
- [ ] Modules
- [ ] Coroutines

**Q2. What is the result of the following range pipeline?**
```cpp
std::views::iota(1, 6) | std::views::transform([](int x){ return x*2; })
```
- [ ] `{1, 2, 3, 4, 5}`
- [x] `{2, 4, 6, 8, 10}`
- [ ] `{1, 4, 9, 16, 25}`
- [ ] `{2, 3, 4, 5, 6}`

**Q3. In C++20, `std::ranges::sort(v, {}, &Person::age)` — what does the third argument do?**
- [ ] Provides a custom comparator
- [x] Provides a projection — extracts the comparison key from each element
- [ ] Specifies the sort algorithm
- [ ] Specifies the allocator

**Q4. Which coroutine keyword yields a value to the caller and then suspends?**
- [ ] `co_return`
- [x] `co_yield`
- [ ] `co_await`
- [ ] `co_suspend`

**Q5. A `std::views::filter` / `transform` pipeline is evaluated:**
- [x] Lazily — only when iterated
- [ ] Eagerly — when the pipeline is constructed
- [ ] At compile time via `constexpr`
- [ ] In a background thread

**Q6. C++20 Modules (`import math;`) offer which primary advantage over `#include`?**
- [ ] They allow circular dependencies
- [ ] They enforce stronger type checking
- [x] They eliminate redundant re-parsing of headers, speeding up compilation
- [ ] They remove the need for a linker

**Q7. Which C++20 comparison feature generates all six relational operators from a single function?**
- [ ] `operator==` defaulting
- [x] `operator<=>` (the spaceship operator)
- [ ] `std::compare_three_way`
- [ ] `std::strong_ordering`
