# Quiz: Templates and Generic Programming

**Q1. What does `template <typename T>` declare?**
- [ ] A variable that can hold any type at runtime
- [x] A compile-time parameter — the compiler generates code for each concrete type used
- [ ] A virtual base class parameterized on T
- [ ] A runtime type-erasure wrapper

**Q2. `T&&` in a function template with deduced `T` is a:**
- [ ] Plain rvalue reference — it only binds to rvalues
- [ ] Const lvalue reference
- [x] Forwarding reference (universal reference) — binds to both lvalues and rvalues via reference collapsing
- [ ] Pointer to T

**Q3. What does SFINAE stand for?**
- [ ] Static Function Is Not An Error
- [x] Substitution Failure Is Not An Error
- [ ] Symbol Forwarding Is Not Allowed Explicitly
- [ ] Single Function Instantiation Not Applicable Everywhere

**Q4. In C++17, what does `if constexpr (condition)` do?**
- [ ] Evaluates the condition at runtime and skips the branch
- [ ] Causes a compile error if condition is false
- [x] Discards the inactive branch entirely at compile time, preventing instantiation errors
- [ ] Replaces `#ifdef` preprocessor directives

**Q5. Which C++17 feature allows you to apply a binary operator to all elements in a parameter pack?**
- [ ] Variadic macros
- [ ] `std::apply`
- [x] Fold expressions: `(pack op ...)`
- [ ] `std::accumulate` on a tuple

**Q6. A C++20 Concept is best described as:**
- [ ] A base class that enforces an interface via virtual functions
- [ ] A `static_assert` placed inside a function body
- [x] A named compile-time predicate on template arguments that produces clear error messages
- [ ] A runtime type-check using `dynamic_cast`

**Q7. Template full specialization means:**
- [x] Providing a completely different implementation for a single specific type combination
- [ ] Providing a default implementation used when no other overload matches
- [ ] Instantiating a template manually to speed up compilation
- [ ] Inheriting from a template class to extend it

**Q8. Why do templates tend to increase compile times?**
- [ ] They disable compiler optimizations
- [ ] They require dynamic linking
- [x] Each unique instantiation generates a separate copy of the code that must be compiled and linked
- [ ] They force the use of RTTI (run-time type information)
