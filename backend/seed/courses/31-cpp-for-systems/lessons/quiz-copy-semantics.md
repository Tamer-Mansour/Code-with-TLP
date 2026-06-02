# Quiz: Copy Semantics and the Rule of Three

Test your understanding of shallow vs deep copy, the copy constructor, copy assignment, self-assignment safety, and the Rule of Three.

---

**Q1. A class has a user-defined destructor that calls `delete[] ptr_` and no other user-defined special members. What does the compiler-generated copy constructor do?**

- [ ] Allocates new memory and copies the array contents into it (deep copy)
- [x] Copies the value of `ptr_` so both objects point to the same memory (shallow copy)
- [ ] Sets `ptr_` to `nullptr` in the copy
- [ ] Refuses to compile — a user-defined destructor disables the copy constructor

_The compiler-generated copy constructor performs a memberwise copy, which for a raw pointer means copying the address — a shallow copy. This is why the Rule of Three exists._

---

**Q2. Which statement about the copy-and-swap idiom is correct?**

- [ ] It requires an explicit `if (this == &rhs)` self-assignment check
- [ ] It provides only the basic exception-safety guarantee
- [x] It automatically handles self-assignment without a guard and provides the strong exception-safety guarantee
- [ ] It is less efficient than a hand-written copy assignment operator in all cases

_Copy-and-swap passes `rhs` by value (invoking the copy constructor), swaps with `*this`, then lets `rhs`'s destructor clean up — self-assignment makes a copy that is then safely destroyed, and any exception is thrown before state is changed._

---

**Q3. Consider the following class:**

```cpp
class Handle {
    int* p_;
public:
    Handle(int n) : p_(new int(n)) {}
    ~Handle() { delete p_; }
};
```

**What happens when you do `Handle a(1); Handle b = a;` and both go out of scope?**

- [ ] Both objects are destroyed cleanly — the compiler detects aliasing
- [ ] `b`'s destructor runs and frees the memory; `a`'s destructor does nothing
- [x] Both destructors call `delete` on the same pointer — double free — undefined behaviour
- [ ] A compile-time error occurs because Handle has no copy constructor

_The compiler generates a shallow copy constructor. `a.p_` and `b.p_` point to the same `int`. When both destructors run, `delete` fires twice on the same address._

---

**Q4. The Rule of Three says: if you define any one of the destructor, copy constructor, or copy assignment operator, you should define all three. What is the primary reason?**

- [ ] The C++ standard requires it for well-formed programs
- [ ] Otherwise the compiler generates them with incorrect behaviour for all types
- [x] Defining one signals resource ownership, and the compiler-generated copies of the other two will alias the resource, causing double-free or leaks
- [ ] The linker will produce errors if any of the three is missing

_The destructor signals that the class owns a resource. Without user-defined copy operations, the compiler generates shallow copies that alias the resource — leading to double-free on destruction and resource leaks on assignment._

---

**Q5. Which of the following prevents NRVO (Named Return Value Optimisation)?**

- [ ] Returning a local variable by name in a single `return` statement
- [x] Writing `return std::move(localVar);` in a function
- [ ] Declaring the return type as a non-copyable class
- [ ] Using `-O2` optimisation level

_`std::move` converts the local to an xvalue, which prevents the compiler from applying NRVO. The compiler then uses the move constructor instead of eliding the operation entirely. You should return local variables without `std::move` to allow NRVO._

---

**Q6. When does the compiler NOT generate a move constructor for a class?**

- [ ] When the class has more than one data member
- [ ] When the class inherits from another class
- [x] When the class has a user-declared destructor, copy constructor, or copy assignment operator
- [ ] When the class has any `const` member variable

_The C++11 rules suppress the generated move constructor if the user declares a destructor, a copy constructor, or a copy assignment operator — precisely to maintain backwards compatibility with pre-C++11 classes that rely on copy semantics._
