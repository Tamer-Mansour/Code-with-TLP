# Quiz: Inheritance

Test your understanding of inheritance, access modes, name hiding, and the diamond problem.

---

**Q1. Given `class D : private B {};`, which statement is true?**

- [ ] `D*` can be implicitly converted to `B*` by any caller
- [ ] Public members of `B` become public in `D`
- [x] Public members of `B` become private in `D`, and no implicit `D*` to `B*` conversion is allowed outside `D`
- [ ] Private members of `B` become accessible in `D`

*Private inheritance makes all inherited members private in `D` and prevents external code from treating a `D` as a `B`. Only `D` itself (and its friends) can perform the conversion.*

---

**Q2. What does the following code print?**

```cpp
struct Base {
    void print(int)    { std::cout << "int\n"; }
    void print(double) { std::cout << "double\n"; }
};
struct Derived : Base {
    void print(const char*) { std::cout << "str\n"; }
};
int main() {
    Derived d;
    d.print(3.14);
}
```

- [ ] `double`
- [x] Compile error — `print(double)` is hidden
- [ ] `str`
- [ ] `int`

*The `print(const char*)` declaration in `Derived` hides all `Base::print` overloads. Because there is no `using Base::print;`, calling `d.print(3.14)` finds no matching function in `Derived`'s scope and the compilation fails.*

---

**Q3. Which cast performs a runtime type check and returns `nullptr` on failure for pointer types?**

- [ ] `static_cast`
- [ ] `reinterpret_cast`
- [ ] `const_cast`
- [x] `dynamic_cast`

*`dynamic_cast` uses RTTI to verify the actual runtime type. For pointer casts it returns `nullptr` if the object is not of the target type. For reference casts it throws `std::bad_cast`.*

---

**Q4. What is the "diamond problem" in C++ multiple inheritance?**

- [ ] A diamond-shaped vtable that causes slow dispatch
- [ ] Ambiguous operator overloading when two base classes define `operator+`
- [x] A common base class being duplicated when two intermediate classes both inherit from it non-virtually, causing ambiguity in a derived class that inherits from both
- [ ] Circular inheritance where A inherits from B and B inherits from A

*Without `virtual` inheritance, `struct D : B1, B2` gets two copies of any base shared by both `B1` and `B2`. Virtual inheritance (`virtual public Base`) ensures only one shared sub-object exists.*

---

**Q5. Which class is responsible for constructing a virtual base sub-object?**

- [ ] The first class in the inheritance list that virtually inherits the base
- [ ] The virtual base class itself through its default constructor only
- [ ] Any intermediate class, in order of declaration
- [x] The most-derived class in the hierarchy that is actually being constructed

*With virtual inheritance, the most-derived concrete class must initialize the virtual base directly in its member initializer list. Intermediate classes' initializers for the virtual base are ignored during full-object construction.*

---

**Q6. When should you prefer composition over inheritance?**

- [ ] When you need runtime polymorphism through virtual dispatch
- [x] When you want to reuse implementation details without committing to an is-a relationship or exposing the base class's interface
- [ ] When the derived class must override a virtual function
- [ ] When you need access to `protected` members of a class not designed for inheritance

*Composition couples classes through their public interfaces rather than implementation details, avoids the fragile base-class problem, and allows components to be swapped at runtime — making it the default choice unless true is-a substitutability or virtual dispatch is required.*
