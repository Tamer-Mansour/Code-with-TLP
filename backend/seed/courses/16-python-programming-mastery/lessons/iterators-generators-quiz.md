# Quiz: Iterators, Generators, and Decorators

**Q1. What keyword makes a function a generator?**
- [ ] `return`
- [x] `yield`
- [ ] `async`
- [ ] `generate`

**Q2. What does `next()` do when a generator is exhausted?**
- [ ] Returns `None`
- [ ] Returns `0`
- [x] Raises `StopIteration`
- [ ] Restarts the generator from the beginning

**Q3. Which of the following is a generator expression (not a list comprehension)?**
- [ ] `[x * 2 for x in range(10)]`
- [x] `(x * 2 for x in range(10))`
- [ ] `{x * 2 for x in range(10)}`
- [ ] `{x: x * 2 for x in range(10)}`

**Q4. A decorator is:**
- [ ] A comment above a function definition
- [x] A callable that takes a function and returns a modified function
- [ ] A type annotation syntax
- [ ] A special class method

**Q5. What does `@functools.wraps(func)` do inside a decorator?**
- [ ] Speeds up the wrapped function
- [ ] Prevents the function from being called more than once
- [x] Copies the original function's `__name__`, `__doc__`, etc. onto the wrapper
- [ ] Makes the decorator thread-safe

**Q6. An object is iterable if it implements:**
- [ ] `__next__`
- [x] `__iter__`
- [ ] `__yield__`
- [ ] `__len__`

**Q7. What is the memory advantage of a generator over a list?**
- [ ] Generators compress data automatically
- [ ] Generators run faster due to C-level optimisation
- [x] Generators produce values one at a time so the entire sequence is never in memory at once
- [ ] There is no advantage — generators just have different syntax
