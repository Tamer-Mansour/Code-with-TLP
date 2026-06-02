# Quiz: Classes and Objects

Test your understanding of C++ classes, objects, access control, and related concepts.

---

**Q1. What is the only technical difference between `struct` and `class` in C++?**

- [ ] `struct` cannot have member functions; `class` can.
- [ ] `struct` cannot be used with inheritance; `class` can.
- [x] `struct` defaults to `public` member access; `class` defaults to `private`.
- [ ] `struct` members are stored on the stack; `class` members on the heap.

The C++ standard specifies that the sole syntactic difference is the default access specifier and default inheritance mode. Both keywords produce fully capable types.

---

**Q2. Which access specifier makes a member visible to derived classes but NOT to arbitrary external code?**

- [ ] `public`
- [ ] `private`
- [x] `protected`
- [ ] `internal`

`protected` members are accessible within the class itself, its friends, and classes that inherit from it — but not from unrelated code. `internal` is not a C++ keyword.

---

**Q3. What is the type of `this` inside a `const` member function of class `Foo`?**

- [ ] `Foo*`
- [ ] `const Foo&`
- [x] `const Foo*`
- [ ] `Foo* const`

In a `const` member function the compiler treats `this` as a pointer-to-const (`const Foo*`), preventing modification of data members. `Foo* const` would mean the pointer itself is const but the pointed-to object could be modified.

---

**Q4. Which of the following correctly defines the out-of-class storage for a static data member (before C++17 inline statics)?**

- [ ] `static int MyClass::count = 0;` inside the `.cpp` file
- [x] `int MyClass::count = 0;` inside the `.cpp` file
- [ ] `MyClass::static int count = 0;` inside the `.cpp` file
- [ ] No definition is needed; the in-class declaration provides storage.

The out-of-class definition uses the fully qualified name without the `static` keyword. Omitting the definition causes a linker error (undefined symbol). C++17 `inline static` members are the exception.

---

**Q5. A `friend` function declared inside class `X` has which of the following properties?**

- [ ] It is automatically also a friend of any class derived from `X`.
- [ ] It becomes a friend of every class that `X` is a friend of.
- [x] It can access `X`'s private and protected members, but friendship is not inherited or transitive.
- [ ] It must be defined inside the class body.

Friendship grants access to private/protected members, but it is neither inherited (subclasses do not inherit friends) nor transitive (A friend of B, B friend of C, does not make A a friend of C).

---

**Q6. Given the struct below, what is the most likely value of `sizeof(S)` on a 64-bit platform with default alignment?**

```cpp
struct S {
    char   a;
    int    b;
    char   c;
};
```

- [ ] 6
- [ ] 7
- [x] 12
- [ ] 8

`a` is 1 byte at offset 0, then 3 bytes of padding to align `b` (int, 4 bytes) at offset 4, then `c` at offset 8 (1 byte), then 3 bytes of trailing padding so the struct size is a multiple of 4. Total = 12. Reordering to `int b; char a; char c;` gives 8 bytes.
