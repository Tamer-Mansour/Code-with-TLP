# Quiz: Operator Overloading

**Q1. Which of the following operators MUST be implemented as a member function?**

- [ ] `operator+`
- [ ] `operator<<`
- [x] `operator[]`
- [ ] `operator==`

The subscript `[]`, assignment `=`, call `()`, and arrow `->` operators are required by the language to be member functions. `operator+`, `operator<<`, and `operator==` are best implemented as non-members.

---

**Q2. You write a class `Celsius` with an implicit conversion constructor from `double`. You implement `operator+` as a member. What happens with `20.0 + Celsius{5.0}`?**

- [ ] It compiles and returns `Celsius{25.0}`
- [x] It does not compile — 20.0 cannot be the left operand of a member operator
- [ ] It compiles but returns a `double`
- [ ] It is undefined behaviour

A member `operator+` binds the left operand to `*this`, so it must already be of the class type. Implicit conversion is not applied to the left operand of a member operator. Making `operator+` a non-member free function would fix this.

---

**Q3. What is the correct signature for a postfix increment operator?**

- [ ] `T& operator++()`
- [ ] `T operator++(T)`
- [x] `T operator++(int)`
- [ ] `T& operator++(int)`

The dummy `int` parameter distinguishes postfix from prefix at compile time. It is never passed a value. Postfix returns the old value by value (not by reference), so `T` — not `T&` — is the return type.

---

**Q4. What does `auto cmp = a <=> b;` return when both `a` and `b` are `int`s and `a < b`?**

- [ ] `false`
- [ ] `-1`
- [x] A value of type `std::strong_ordering` that compares less than 0
- [ ] `std::weak_ordering::less`

`operator<=>` on integers returns `std::strong_ordering`. The result is not `-1` but a `strong_ordering` value you compare against 0 or against named constants like `std::strong_ordering::less`.

---

**Q5. Which statement about overloading `operator&&` is correct?**

- [ ] It preserves short-circuit evaluation just like the built-in version
- [ ] It is forbidden by the C++ standard
- [x] Both operands are evaluated before the operator function is called, losing short-circuit behaviour
- [ ] It works correctly only when both operands are the same type

Overloaded `&&` is a function call. Function arguments are fully evaluated before the call, so the right operand is always evaluated — even when the left is false. The short-circuit guarantee of the built-in `&&` is permanently lost.

---

**Q6. Given the following class, what is wrong with it?**

```cpp
struct Val {
    int n;
    std::strong_ordering operator<=>(const Val& rhs) const {
        return n <=> rhs.n;
    }
};
```

- [ ] `<=>` cannot be used with `int`
- [ ] The return type should be `std::weak_ordering`
- [x] `operator==` is not generated automatically when `<=>` is user-defined (not defaulted)
- [ ] The operator must be a non-member function

When `operator<=>` is user-defined rather than defaulted, the compiler does NOT automatically generate `operator==`. You must write it yourself. If `<=>` were `= default`, both `<=>` and `==` would be generated automatically.
