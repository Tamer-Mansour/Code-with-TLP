# Quiz: const, static, volatile, and Storage Qualifiers

**Q1. Given `const int* p`, which operation is legal?**
- [ ] `*p = 10;`
- [x] `p = &other_int;`
- [ ] Both are legal
- [ ] Neither is legal

The pointer `p` itself is mutable (can be redirected), but the `int` it points to is `const` and cannot be modified through `p`.

---

**Q2. What does `static` mean when applied to a free function at file scope?**
- [ ] The function is allocated in static memory
- [ ] The function can only be called once
- [x] The function has internal linkage and is invisible to the linker outside this translation unit
- [ ] The function is thread-safe

`static` on a file-scope function restricts its linkage to the current translation unit, preventing name collisions and hiding implementation details.

---

**Q3. Why is `volatile` necessary for a memory-mapped hardware register, but insufficient for a flag shared between two CPU threads?**
- [ ] `volatile` is slower than `std::atomic`
- [ ] `volatile` disables all optimizations globally
- [ ] `volatile` is deprecated and should never be used
- [x] `volatile` prevents compiler caching but does not prevent CPU out-of-order execution or guarantee atomicity across cores

`volatile` tells the compiler to always load/store, but the CPU may still reorder stores to different addresses or produce torn reads on multi-byte values. `std::atomic` adds the necessary hardware fences and atomicity guarantees.

---

**Q4. Which of the following is the canonical thread-safe Singleton pattern in C++11 and later?**
- [ ] `static Foo* p = new Foo(); return *p;`
- [ ] `if (!instance) { instance = new Foo(); } return *instance;`
- [x] `static Foo instance; return instance;`
- [ ] `volatile static Foo instance; return instance;`

A function-local `static` variable is guaranteed by C++11 to be initialized exactly once in a thread-safe manner (double-checked locking without manual synchronization).

---

**Q5. `constexpr int x = 42;` differs from `const int x = 42;` in that:**
- [x] `constexpr` guarantees compile-time evaluation; `const` only prevents modification and may be runtime
- [ ] `constexpr` values are stored in ROM; `const` values are stored in RAM
- [ ] `const` works with integers; `constexpr` works with any type
- [ ] There is no practical difference in modern C++

`constexpr` is a compile-time guarantee allowing the value to appear in array bounds, template arguments, and `switch` cases. A `const int` initialized from a runtime source does not satisfy constant expressions.

---

**Q6. What is the purpose of `mutable` in a C++ class member?**
- [ ] It allows the member to be accessed without an object instance
- [ ] It prevents the member from being copied during assignment
- [ ] It marks the member as thread-safe
- [x] It allows the member to be modified inside `const` member functions

`mutable` enables logical constness: the object's observable interface is const-correct, but internal implementation details (caches, mutexes, counters) can still be updated.
