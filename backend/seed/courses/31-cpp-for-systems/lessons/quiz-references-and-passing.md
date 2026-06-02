# Quiz: References and Parameter Passing

Test your understanding of C++ references, pointers, and parameter-passing styles.

---

**Q1. Which of the following statements about C++ references is TRUE?**

- [ ] A reference can be reseated to refer to a different object after initialization.
- [x] A reference must be initialized at the point of declaration and cannot be null.
- [ ] A reference stores the address of the object, just like a pointer.
- [ ] You must dereference a reference with `*` to access the underlying value.

_A reference is an alias — always bound at declaration, cannot be null or reseated. It requires no dereference syntax and has no separate storage requirement._

---

**Q2. What does the following code print?**

```cpp
int a = 1, b = 2;
int& r = a;
r = b;
std::cout << a;
```

- [ ] 1
- [x] 2
- [ ] Prints the address of b
- [ ] Undefined behavior

_`r = b` assigns the value of `b` (which is 2) to the object `r` aliases (`a`). The reference `r` is NOT reseated to `b`. So `a` becomes 2._

---

**Q3. Which parameter-passing style should you choose for a large, read-only `std::vector<double>` argument?**

- [ ] Pass by value (`std::vector<double> v`)
- [ ] Pass by non-const reference (`std::vector<double>& v`)
- [x] Pass by const reference (`const std::vector<double>& v`)
- [ ] Pass by raw pointer (`const std::vector<double>* v`)

_`const T&` avoids copying the entire vector (which could be megabytes of data) while giving the compiler-enforced guarantee that the function will not modify it. A raw pointer would also avoid the copy but adds nullable semantics that are not needed here._

---

**Q4. What is wrong with this code?**

```cpp
int& getRef() {
    int local = 42;
    return local;
}
```

- [ ] `local` should be `static` for this to compile.
- [ ] The return type should be `int*`, not `int&`.
- [x] It returns a reference to a local variable that is destroyed when the function returns, causing a dangling reference.
- [ ] Nothing is wrong; `local` is kept alive by the reference.

_`local` lives on the stack and is destroyed when `getRef` returns. The returned reference points to freed memory — accessing it is undefined behavior. Most compilers warn about this._

---

**Q5. What does C++ lifetime extension guarantee when you write `const std::string& r = std::string("hello");`?**

- [ ] Nothing — this is a compile error because you cannot bind a const reference to a temporary.
- [ ] The temporary is copied into `r`; both exist independently.
- [x] The temporary `std::string("hello")` is kept alive until `r` goes out of scope.
- [ ] The temporary lives only until the end of the statement.

_Binding a `const` reference directly to a temporary extends the temporary's lifetime to match the reference's scope. This is a standard-guaranteed rule (not an optimization)._

---

**Q6. Which call-site characteristic is the PRIMARY reason some style guides prefer pointer parameters over reference parameters for output arguments?**

- [ ] Pointers are faster than references at runtime.
- [ ] Pointers allow the function to return multiple values.
- [x] The call site visibly signals mutation: `foo(&x)` shows `x` may be modified, while `foo(x)` does not.
- [ ] Pointer parameters are always checked for null by the compiler.

_With a reference, `foo(x)` looks identical to a by-value call. With a pointer, `foo(&x)` makes mutation visible at the call site. This explicitness is the primary stylistic argument for output pointer parameters._
