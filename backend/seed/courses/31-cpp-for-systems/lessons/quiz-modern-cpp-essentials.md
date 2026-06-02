# Quiz: Modern C++ Essentials

Test your understanding of modern C++ features used in systems and OS programming.

---

**Q1. What type does `auto x = {1, 2, 3};` deduce for `x` in C++11/14?**

- [ ] `int[3]`
- [ ] `std::vector<int>`
- [x] `std::initializer_list<int>`
- [ ] `int*`

_`auto` combined with a braced initializer list deduces `std::initializer_list<T>` in C++11 and C++14. In C++17 with a single element `auto x{1}`, `int` is deduced instead._

---

**Q2. Given `int x = 5;`, what is the type of `decltype((x))`?**

- [ ] `int`
- [x] `int&`
- [ ] `const int&`
- [ ] `int&&`

_Parenthesizing a named variable turns it into an lvalue expression. `decltype` applied to an lvalue expression yields `T&`. Without the extra parentheses, `decltype(x)` would be `int`._

---

**Q3. Which of the following best describes a narrowing conversion in the context of brace initialization?**

- [ ] Converting a `char` to `int`
- [ ] Converting an `int` to `long`
- [x] Converting a `double` to `int`
- [ ] Converting `unsigned char` to `unsigned int`

_Brace initialization rejects conversions that may lose information. `double` to `int` truncates the fractional part — a narrowing conversion. Widening conversions like `int` to `long` are always safe and not considered narrowing._

---

**Q4. What does `enum class Status : uint8_t` guarantee compared to a plain `enum`?**

- [ ] Enumerators are visible in the global namespace
- [ ] Implicit conversion to `int` is allowed
- [x] Enumerators are scoped and no implicit integer conversion occurs
- [ ] The underlying storage is platform-dependent

_`enum class` scopes enumerators (must write `Status::OK`) and disables implicit conversion to integer types. The `: uint8_t` suffix explicitly controls the storage size to exactly 1 byte._

---

**Q5. In the lambda `[&base](int x) { return base + x; }`, what is the risk if the lambda is stored and called after `base` goes out of scope?**

- [ ] `base` will be zero-initialized
- [ ] The compiler rejects the code
- [x] Undefined behavior due to a dangling reference
- [ ] `base` is automatically promoted to static storage

_Reference captures bind to the captured variable's address. If the lambda outlives the variable (e.g., stored in a callback table and called after the enclosing function returns), the reference is dangling and any access is undefined behavior._

---

**Q6. Which statement about `std::optional<T>` is correct?**

- [ ] It always allocates `T` on the heap
- [ ] Accessing an empty optional returns a default-constructed `T`
- [x] It stores `T` inline and `operator*` on an empty optional is undefined behavior
- [ ] It is equivalent to `std::variant<T, std::monostate>`

_`std::optional` stores its value inline (no heap allocation). Dereferencing an empty optional with `*opt` is undefined behavior; use `opt.value()` to get a `std::bad_optional_access` exception, or `opt.value_or(default)` for a safe fallback. While conceptually similar to `variant<T, monostate>`, the two types have different APIs and semantics._
