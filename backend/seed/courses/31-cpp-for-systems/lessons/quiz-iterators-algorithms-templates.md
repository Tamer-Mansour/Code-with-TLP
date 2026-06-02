# Quiz: Iterators, Algorithms, and Templates

**Q1. Which iterator category is required by `std::sort`?**

- [ ] Forward iterator
- [ ] Bidirectional iterator
- [x] Random-access iterator
- [ ] Input iterator

`std::sort` uses index arithmetic and `it + n` jumps that only random-access iterators support. Calling it on a `std::list` is a compile error.

---

**Q2. What happens to all iterators into a `std::vector` when an insertion causes reallocation?**

- [ ] Only iterators before the insert point are invalidated
- [ ] Only the inserted-position iterator is invalidated
- [x] All iterators, pointers, and references are invalidated
- [ ] No iterators are invalidated; reallocation is transparent

When `vector` reallocates, it copies/moves all elements to a new buffer. Every existing iterator, pointer, and reference now points to freed memory.

---

**Q3. What does the following code print?**

```cpp
#include <numeric>
#include <vector>
std::vector<int> v = {1, 2, 3, 4};
int r = std::accumulate(v.begin(), v.end(), 10);
std::cout << r;
```

- [ ] 10
- [ ] 100
- [x] 20
- [ ] 24

`accumulate` starts from the init value `10` and adds 1+2+3+4 = 10, giving 20.

---

**Q4. Which statement about partial template specialization is correct?**

- [ ] It can be applied to both class templates and function templates
- [x] It can only be applied to class templates, not function templates
- [ ] It requires all template parameters to be specified
- [ ] It is the same as full specialization

Partial specialization fixes some parameters while leaving others open. The C++ standard only allows partial specialization for class templates; function templates must use overloading instead.

---

**Q5. In CRTP (Curiously Recurring Template Pattern), what is the main advantage over virtual dispatch?**

- [ ] It allows heterogeneous containers
- [ ] It requires less code to write
- [x] Dispatch is resolved at compile time, enabling inlining and zero vtable overhead
- [ ] It supports runtime type checking

CRTP uses `static_cast<Derived*>(this)` which is a compile-time operation. The compiler can inline the call entirely, unlike a vtable indirect jump which blocks inlining.

---

**Q6. What is the purpose of the `requires` expression inside a C++20 concept definition?**

- [ ] It enforces runtime preconditions, similar to `assert`
- [ ] It generates test cases for template functions
- [x] It checks that a set of expressions is syntactically valid for the given type at compile time
- [ ] It deduces template arguments automatically

A `requires { expr; }` block tests whether each expression compiles for the constrained type. If any expression is ill-formed, the concept evaluates to `false` and the constraint is not satisfied.
