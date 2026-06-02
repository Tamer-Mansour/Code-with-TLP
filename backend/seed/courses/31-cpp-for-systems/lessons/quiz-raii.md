# Quiz: RAII and Resource Management

Test your understanding of RAII, ownership, scope guards, and exception safety.

---

**Q1. What is the primary guarantee that makes RAII work in C++?**

- [ ] The compiler inserts `free()` calls automatically for all heap allocations.
- [x] Destructors of local objects are called automatically when they go out of scope, even during exception unwinding.
- [ ] The operating system reclaims all handles when a function returns.
- [ ] `noexcept` prevents destructors from being skipped.

_Explanation: C++ guarantees that destructors of objects with automatic storage duration run on scope exit — including during stack unwinding. RAII places cleanup code in the destructor to exploit this guarantee._

---

**Q2. You have a RAII file descriptor wrapper. Which of the following is MOST likely to cause a double-close bug?**

- [ ] Marking the destructor `noexcept`.
- [ ] Using `std::exchange` in the move constructor.
- [x] Allowing the default compiler-generated copy constructor.
- [ ] Adding a `release()` method that returns the raw fd and sets the member to -1.

_Explanation: The default copy constructor copies the integer fd value, so two wrapper objects share the same fd. When both are destroyed, `close()` is called twice — undefined behavior._

---

**Q3. Which C++ standard library type provides deadlock-free locking of multiple mutexes simultaneously?**

- [ ] `std::lock_guard`
- [ ] `std::unique_lock`
- [ ] `std::recursive_mutex`
- [x] `std::scoped_lock` (C++17)

_Explanation: `std::scoped_lock` accepts variadic mutexes and uses a deadlock-avoidance algorithm to lock all of them atomically. `lock_guard` and `unique_lock` operate on a single mutex at a time._

---

**Q4. A function acquires two resources, A then B. B's constructor throws. What happens to A in well-written RAII code?**

- [ ] A is leaked because the destructor of the enclosing object was never called.
- [ ] A must be released manually in a catch block.
- [x] A is automatically released because its destructor runs during stack unwinding.
- [ ] A is released only if the programmer calls `std::current_exception()`.

_Explanation: When B's constructor throws, the C++ runtime unwinds the stack. Because A is already fully constructed, its destructor is called automatically — no manual cleanup needed._

---

**Q5. What is the purpose of the `dismiss()` method on a scope guard?**

- [ ] To immediately execute the cleanup action without waiting for scope exit.
- [ ] To transfer the cleanup action to another scope guard.
- [x] To cancel the cleanup action because the operation succeeded and no rollback is needed.
- [ ] To pause the cleanup action until the guard is reassigned.

_Explanation: A dismissible scope guard registers rollback as the default behavior. If all steps succeed, `dismiss()` is called so the destructor is a no-op — implementing commit-or-rollback without exceptions._

---

**Q6. In a class with two RAII member objects declared as `Logger logger_` then `Database db_`, which is destroyed first?**

- [ ] `db_`, because it was initialized first in the constructor body.
- [ ] `logger_`, because it was declared first.
- [x] `db_`, because members are destroyed in reverse order of declaration.
- [ ] The order is implementation-defined and cannot be relied upon.

_Explanation: C++ destroys non-static data members in the reverse order of their declaration in the class body, regardless of initializer-list order. `db_` is declared second, so it is destroyed first._
