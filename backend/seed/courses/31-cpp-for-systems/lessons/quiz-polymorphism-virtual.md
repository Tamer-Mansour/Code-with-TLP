# Quiz: Polymorphism and Virtual Functions

Test your understanding of runtime polymorphism, virtual dispatch, and related C++ mechanisms.

---

**Q1. What is the primary difference between compile-time and runtime polymorphism in C++?**

- [ ] Runtime polymorphism is faster because the CPU can cache function addresses.
- [ ] Compile-time polymorphism requires the `virtual` keyword.
- [x] Compile-time polymorphism resolves function calls at build time (zero runtime cost); runtime polymorphism resolves them during execution via the vtable.
- [ ] Runtime polymorphism is implemented with function overloading; compile-time with virtual functions.

_Compile-time polymorphism (overloading, templates) lets the compiler embed a direct call address; runtime polymorphism (virtual functions) stores function pointers in a vtable and resolves the call while the program runs._

---

**Q2. What does the `override` keyword guarantee?**

- [ ] That the function will be inlined by the compiler.
- [ ] That the function cannot be overridden further in derived classes.
- [ ] That the function is called at runtime instead of compile time.
- [x] That the function matches a virtual function signature in a base class — a compile error is raised if no matching virtual exists.

_`override` triggers a compile error if the annotated function does not exactly match a base-class virtual (name, parameter types, and `const`/`volatile` qualifiers must all match), catching typos and signature drift early._

---

**Q3. Given the code below, what does `a->speak()` print?**

```cpp
struct Animal {
    void speak() const { std::cout << "Animal\n"; }  // NOT virtual
};
struct Dog : Animal {
    void speak() const { std::cout << "Dog\n"; }
};
Animal* a = new Dog();
a->speak();
```

- [x] `Animal`
- [ ] `Dog`
- [ ] Undefined behavior
- [ ] Compile error

_Because `speak` is not declared `virtual`, the call is statically bound to `Animal::speak` using the declared type of the pointer (`Animal*`). No vtable lookup occurs._

---

**Q4. What is object slicing?**

- [ ] Splitting an object across multiple cache lines.
- [ ] Dividing an object into base and derived vtables.
- [x] Copying a derived-class object into a base-class value, discarding derived members and replacing the vtable with the base class's.
- [ ] Accessing only part of an object's memory via a pointer cast.

_When a derived object is assigned or passed by value to a base-class variable, only the base sub-object is copied. Derived-specific data and the correct vptr are lost, causing virtual functions to dispatch to base-class implementations._

---

**Q5. Which statement about `final` on a class is correct?**

- [ ] It makes all member functions `const`.
- [ ] It prevents the class from having virtual functions.
- [ ] It forces all virtual functions to be pure virtual.
- [x] It prevents any other class from inheriting from it, and allows the compiler to devirtualize calls to its methods.

_`class Foo final` means no class may derive from `Foo`. Because the compiler knows no derived class can exist, virtual calls on `Foo` objects can be resolved statically, enabling inlining and other optimizations._

---

**Q6. A virtual function's body is defined inside the class definition. Which statement is true?**

- [ ] This is illegal — virtual functions must be defined outside the class.
- [ ] The function is guaranteed to be inlined even through a base pointer.
- [x] The function is implicitly `inline` for linkage purposes, but virtual dispatch through a base pointer still goes through the vtable and is not inlined.
- [ ] The `inline` status overrides the `virtual` keyword and makes dispatch static.

_Defining a member function in the class body makes it implicitly `inline`, which handles ODR (multiple definitions across translation units). However, when called through a pointer or reference to the base, the vtable is still used and inlining cannot occur because the callee is not known at compile time._
