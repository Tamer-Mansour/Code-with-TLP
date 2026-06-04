# Quiz: Error Handling and Exception Safety

**Q1. What are the three exception safety guarantees in order from weakest to strongest?**
- [ ] no-throw, strong, basic
- [ ] basic, no-throw, strong
- [x] basic, strong, no-throw
- [ ] safe, strong, complete

**Q2. The `noexcept` specifier on a function:**
- [ ] Prevents the function from being called in a try block
- [x] Promises the function will not throw; the program terminates via `std::terminate` if it does
- [ ] Makes all exceptions caught silently
- [ ] Is only valid on destructors

**Q3. `std::optional<T>` is best used when:**
- [ ] You need to store a polymorphic object
- [x] A function may or may not return a value, and you want to avoid exceptions or sentinel values like `-1`
- [ ] You need to hold multiple alternative types
- [ ] You need a nullable pointer to a heap object

**Q4. `std::variant<A, B, C>` stores:**
- [ ] A pointer to one of A, B, or C on the heap
- [ ] All three values simultaneously
- [x] Exactly one value at a time, which is one of the listed types; the active type is tracked
- [ ] A type-erased wrapper around an arbitrary type

**Q5. `std::expected<T, E>` (C++23) is designed to:**
- [ ] Replace all exceptions in the C++ standard
- [ ] Store a value and an error simultaneously
- [x] Hold either a success value of type T or an error value of type E, enabling error propagation without exceptions
- [ ] Wrap `std::optional` with an error code

**Q6. When should a destructor be marked `noexcept`?**
- [ ] Never — destructors should propagate exceptions
- [ ] Only when the destructor is trivial
- [x] Always (it is the default in C++11 and later); a throwing destructor during stack unwinding calls `std::terminate`
- [ ] Only when the class has no base classes

**Q7. What does `std::visit` do with `std::variant`?**
- [ ] Converts the variant to a `std::any`
- [ ] Checks if the variant holds a given type
- [x] Applies a callable (overloaded or templated) to the currently active alternative in the variant
- [ ] Iterates over all stored alternatives simultaneously

**Q8. The "strong exception safety guarantee" means:**
- [ ] The function never throws
- [ ] The program state is left in an unspecified but valid state if an exception is thrown
- [x] If an exception is thrown, the program state is unchanged — the operation either completes fully or has no effect (commit-or-rollback)
- [ ] All exceptions are converted to error codes
